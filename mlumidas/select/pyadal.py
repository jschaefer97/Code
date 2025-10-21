from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from asgl import Regressor

SelectionRule = Literal["pt", "cv_min", "cv_se", "cv_1se", "k_ic"]  # kept for API-compat only


@dataclass
class PYADAL:
    """
    Adaptive LASSO using `asgl` with TimeSeriesSplit CV.
    API-compatible with PYENTSCV (unused selection-rule params are accepted but ignored).

    Parameters (kept to match PYENTSCV)
    -----------------------------------
    tcv_splits : int
    test_size : Optional[int]
    gap : int
    max_train_size : Optional[int]
    alphas : int
        Ignored here (grid fixed per asgl example); kept for API compatibility.
    max_iter : int
        Kept for parity; not passed to asgl (its solver handles iterations internally).
    with_mean, with_std : bool
    fit_intercept : bool
    """

    # ---- EN/CV-like hyperparams (kept for API compatibility) ----
    tcv_splits: int
    test_size: Optional[int]
    gap: int
    max_train_size: Optional[int]
    alphas: int
    max_iter: int
    with_mean: bool
    with_std: bool
    fit_intercept: bool

    # selection-rule-related (ignored; accepted for API stability)
    selection_rule: SelectionRule = "cv_min"
    se_factor: Optional[float] = None
    threshold_divisor: float = 1.0
    coef_tol: float = 0.0
    k_indicators: Optional[int] = None

    # ---- Fitted attributes ----
    pipeline_cv_: Optional[GridSearchCV] = None
    pipeline_: Optional[Pipeline] = None
    model_cv_: Optional[Regressor] = None
    model_: Optional[Regressor] = None
    coef_series_: Optional[pd.Series] = None
    coef_series_selected_: Optional[pd.Series] = None
    selected_features_: Optional[list[str]] = None
    best_alpha_: Optional[float] = None
    best_alpha_weights_: Optional[float] = None
    feature_names_: Optional[list[str]] = None

    def fit(self, X: pd.DataFrame, y: pd.Series | pd.DataFrame):
        # y can be Series or 1-col DataFrame (match PYENTSCV behavior)
        if isinstance(y, pd.DataFrame):
            y = y.iloc[:, 0]

        self.feature_names_ = list(X.columns)

        logger.info(
            f"Fitting PYADAL (asgl adaptive lasso, lasso weights) | X shape={X.shape}, y len={len(y)} | "
            f"splits={self.tcv_splits}, test_size={self.test_size}, gap={self.gap}, max_train_size={self.max_train_size}"
        )

        # TimeSeries CV splitter
        tscv = TimeSeriesSplit(
            n_splits=self.tcv_splits,
            test_size=self.test_size,
            max_train_size=self.max_train_size,
            gap=self.gap,
        )

        # Estimator: adaptive lasso with LASSO-based weights
        alasso = Regressor(
            model="lm",
            penalization="alasso",
            weight_technique="ridge", # NOTE: lasso, ridge - Ridge is rooted in the literature, lasso not
            fit_intercept=self.fit_intercept,
            # We leave lambda1_weights and individual_power_weight at asgl defaults;
            # only lambda1 is tuned to match the asgl example grid.
        )

        # --- AUTO-CLEAN: drop columns with ±inf or too-large values -------------
        X_num = X.apply(pd.to_numeric, errors="coerce")

        # Identify bad entries
        vals = X_num.to_numpy()
        cols = X_num.columns.to_list()

        pos_inf_mask = np.isposinf(vals)
        neg_inf_mask = np.isneginf(vals)
        too_large_mask = np.abs(vals) > np.finfo(np.float64).max

        # Columns to drop if *any* offending value appears
        drop_mask = (pos_inf_mask.any(axis=0)) | (neg_inf_mask.any(axis=0)) | (too_large_mask.any(axis=0))
        drop_cols = list(np.array(cols)[drop_mask])

        if drop_cols:
            for c in drop_cols:
                logger.warning(f"Dropping feature '{c}' due to ±inf/too-large values.")
            X_num = X_num.drop(columns=drop_cols)

        # (Optional) also drop columns that are entirely NaN after cleaning
        all_nan_cols = X_num.columns[X_num.isna().all(axis=0)]
        if len(all_nan_cols) > 0:
            for c in all_nan_cols:
                logger.warning(f"Dropping feature '{c}' because it is all NaN after cleaning.")
            X_num = X_num.drop(columns=list(all_nan_cols))

        # Replace remaining ±inf with NaN just in case (should be none now)
        X_num = X_num.replace([np.inf, -np.inf], np.nan)

        # Use cleaned X and keep feature order
        X = X_num
        self.feature_names_ = list(X.columns)


        pipe = Pipeline(steps=[
            ("scaler", StandardScaler(with_mean=self.with_mean, with_std=self.with_std)),
            ("alasso", alasso),
        ])

        # >>> EXACTLY the asgl example grid (namespaced via pipeline step):
        # param_grid = {'lambda1': 10 ** np.arange(-2, 1.51, 0.1)}
        param_grid = {
            "alasso__lambda1": 10 ** np.arange(-2, 1.51, 0.1)
        }

        gs = GridSearchCV(
            estimator=pipe,
            param_grid=param_grid,
            scoring="neg_mean_squared_error",
            cv=tscv,
            n_jobs=-1,
        )
        gs.fit(X.values, y.values)

        # Store CV / best pipeline
        self.pipeline_cv_ = gs
        self.pipeline_ = gs.best_estimator_

        # Extract the inner asgl model to surface coefs etc.
        best_alasso: Regressor = self.pipeline_.named_steps["alasso"]
        self.model_cv_ = best_alasso
        self.model_ = best_alasso

        coefs = np.asarray(best_alasso.coef_, dtype=float)
        self.coef_series_ = pd.Series(coefs, index=self.feature_names_)

        # Selection: no custom rule — just nonzero coefficients (API keeps these fields)
        nz_mask = np.abs(coefs) > 0
        self.selected_features_ = [self.feature_names_[i] for i, m in enumerate(nz_mask) if m]
        self.coef_series_selected_ = self.coef_series_.loc[self.selected_features_]

        # Best penalties
        self.best_alpha_ = float(gs.best_params_.get("alasso__lambda1"))
        # Not tuned in this grid; try to read from estimator or leave None
        self.best_alpha_weights_ = getattr(best_alasso, "lambda1_weights", None)

        logger.info(
            "PYADAL fit completed | lambda1*={:.6g} | nnz={}".format(
                self.best_alpha_, nz_mask.sum()
            )
        )
        return self

    def predict(self, X_new: pd.DataFrame) -> np.ndarray:
        if self.pipeline_ is None:
            raise RuntimeError("Model not fitted. Call fit() first.")
        # Align columns by training order
        X_new = X_new[self.feature_names_]
        return self.pipeline_.predict(X_new.values)

    def get_result(self) -> dict:
        # Keys mirror PYENTSCV so downstream code can consume it unchanged
        return {
            "selected_features": self.selected_features_,
            "coef_series": self.coef_series_,
            "coef_series_selected": self.coef_series_selected_,
            "best_alpha": self.best_alpha_,
            "pipeline_cv": self.pipeline_cv_,
            "model_cv": self.model_cv_,
            "pipeline": self.pipeline_,
            "model": self.model_,
            "tcv_splits": self.tcv_splits,
            "test_size": self.test_size,
            "gap": self.gap,
            "max_train_size": self.max_train_size,
            "best_alpha_weights": self.best_alpha_weights_,
        }
