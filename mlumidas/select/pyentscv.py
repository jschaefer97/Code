from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Optional, Union

import numpy as np
import pandas as pd
from loguru import logger

from sklearn.linear_model import ElasticNet
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SelectionRule = Literal["pt", "cv_min", "k_ic"]


@dataclass
class PYENTSCV:
    """
    Elastic Net (or Lasso when l1_ratio=1.0) with TimeSeriesSplit CV and
    feature selection rules. Uses a *single* leakage-safe pipeline:

        StandardScaler -> ElasticNet
        (pipeline is cross-validated with GridSearchCV)
    """

    # ---- EN/CV hyperparams ----
    l1_ratio: float
    tcv_splits: int
    test_size: Optional[int]
    gap: int
    max_train_size: Optional[int]

    # alphas: either number of points (int) -> logspace grid; or iterable of float values
    alphas: Union[int, Iterable[float]]

    max_iter: int
    random_state: int
    with_mean: bool
    with_std: bool
    fit_intercept: bool

    # selection
    selection_rule: SelectionRule
    threshold_divisor: float
    coef_tol: float
    k_indicators: Optional[int] = None

    # optional CV settings
    scoring: str = "neg_mean_squared_error"
    n_jobs: int = -1
    refit: bool = True
    verbose: int = 0

    # Fitted attributes
    pipeline_: Optional[any] = None                  # best estimator (pipeline)
    model_: Optional[ElasticNet] = None              # best ElasticNet
    coef_series_: Optional[pd.Series] = None
    coef_series_selected_: Optional[pd.Series] = None
    selected_features_: Optional[list[str]] = None
    best_alpha_: Optional[float] = None
    grid_: Optional[GridSearchCV] = None             # the fitted GridSearchCV

    # Back-compat aliases (same single pipeline/model)
    pipeline_cv_: Optional[any] = None
    model_cv_: Optional[ElasticNet] = None

    # ---------- Helpers ----------

    def _normalize_alpha_grid(self) -> np.ndarray:
        """
        Convert self.alphas to a 1D numpy array of strictly positive floats.
        If alphas is an int N, produce logspace grid of length N on [1e-4, 1e1].
        """
        if isinstance(self.alphas, int):
            if self.alphas <= 0:
                raise ValueError("alphas as an int must be > 0.")
            grid = np.logspace(-4, 1, self.alphas, dtype=float)
        else:
            grid = np.array(list(self.alphas), dtype=float)
            if grid.ndim != 1 or grid.size == 0:
                raise ValueError("alphas iterable must be 1D and non-empty.")
        if not np.all(np.isfinite(grid)) or np.any(grid <= 0):
            raise ValueError("All alphas must be finite and > 0.")
        return np.unique(grid)

    def _apply_pt(self, coefs: pd.Series) -> list[str]:
        """Paper-style soft-threshold: keep |beta_j| >= max|beta| / threshold_divisor."""
        if self.threshold_divisor <= 0:
            raise ValueError("threshold_divisor must be > 0 when using 'pt'.")
        if coefs.size == 0:
            return []
        max_abs = float(np.nanmax(np.abs(coefs.values)))
        if not np.isfinite(max_abs) or max_abs == 0.0:
            return []
        threshold = max_abs / self.threshold_divisor
        mask = np.abs(coefs.values) >= threshold
        return list(coefs.index[mask])

    def _select_features(self, coefs: pd.Series) -> list[str]:
        """Apply configured selection rule to the coefficient vector."""
        rule = self.selection_rule
        if rule == "pt":
            return self._apply_pt(coefs)
        elif rule == "k_ic":
            base = coefs[np.abs(coefs.values) > self.coef_tol]
            if base.empty:
                return []
            k = 0 if self.k_indicators is None else int(self.k_indicators)
            if k <= 0:
                return []
            topk_idx = np.argsort(-np.abs(base.values))[:k]
            return list(base.index[topk_idx])
        else:  # 'cv_min'
            mask = np.abs(coefs.values) > self.coef_tol
            return list(coefs.index[mask])

    # ---------- Core API ----------

    def fit(self, X: pd.DataFrame, y: pd.Series | pd.DataFrame):
        # ---- Validate types ----
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame.")
        if not isinstance(y, (pd.Series, pd.DataFrame)):
            raise ValueError("y must be a pandas Series or a 1-col DataFrame.")
        if isinstance(y, pd.DataFrame):
            if y.shape[1] != 1:
                raise ValueError("y must be a 1-column DataFrame or a Series.")
            y = y.iloc[:, 0]

        # ---- Coerce to numeric & drop pathological columns ----
        X_num = X.apply(pd.to_numeric, errors="coerce")
        # columns with any inf or values exceeding float64 range
        max_float64 = np.finfo(np.float64).max
        bad_inf = np.isinf(X_num).any(axis=0)
        bad_big = X_num.abs().gt(max_float64).any(axis=0)
        bad_allnan = X_num.isna().all(axis=0)
        bad_cols_mask = bad_inf | bad_big | bad_allnan
        if bad_cols_mask.any():
            bad_cols = list(X.columns[bad_cols_mask.values])
            for col in bad_cols:
                logger.warning(f"Removing feature '{col}' (inf/too-large/all-NaN).")
            X_num = X_num.drop(columns=bad_cols)

        # any remaining NaNs? (You can swap this for an imputer if desired.)
        if X_num.isna().any().any():
            n_bad = int(X_num.isna().sum().sum())
            raise ValueError(f"Found {n_bad} NaNs in X after cleaning. "
                             "Impute or drop rows/columns before fitting.")

        if X_num.shape[1] == 0:
            raise ValueError("No valid features left after cleaning X.")

        logger.info(
            f"Fitting PYENTSCV (TSCV, leakage-safe) | X shape={X_num.shape}, y length={len(y)} | "
            f"splits={self.tcv_splits}, gap={self.gap}, test_size={self.test_size}, max_train_size={self.max_train_size}"
        )

        # ---- TimeSeriesSplit for CV ----
        tscv = TimeSeriesSplit(
            n_splits=self.tcv_splits,
            test_size=self.test_size,
            max_train_size=self.max_train_size,
            gap=self.gap,
        )

        # ---- Pipeline: Standardize X -> ElasticNet (no internal CV) ----
        pipe = make_pipeline(
            StandardScaler(with_mean=self.with_mean, with_std=self.with_std),
            ElasticNet(
                l1_ratio=self.l1_ratio,
                max_iter=self.max_iter,
                fit_intercept=self.fit_intercept,
                random_state=self.random_state,
            ),
        )

        # ---- Param grid (alphas) ----
        alpha_grid = self._normalize_alpha_grid()
        param_grid = {"elasticnet__alpha": alpha_grid}

        # ---- GridSearchCV over the *pipeline* ----
        grid = GridSearchCV(
            estimator=pipe,
            param_grid=param_grid,
            scoring=self.scoring,
            cv=tscv,
            n_jobs=self.n_jobs,
            refit=self.refit,
            verbose=self.verbose,
        )

        grid.fit(X_num, y)

        # best pipeline & model
        best_pipe = grid.best_estimator_
        en_best: ElasticNet = best_pipe.named_steps["elasticnet"]

        # store alpha*
        best_alpha = float(grid.best_params_["elasticnet__alpha"])

        # coefficients aligned to surviving columns
        coefs = pd.Series(en_best.coef_, index=X_num.columns, dtype=float)

        # ---- Selection ----
        selected = self._select_features(coefs)
        coef_sel = coefs.loc[selected]

        # ---- Store ----
        self.pipeline_ = best_pipe
        self.model_ = en_best
        self.coef_series_ = coefs
        self.coef_series_selected_ = coef_sel
        self.selected_features_ = selected
        self.best_alpha_ = best_alpha
        self.grid_ = grid

        # Back-compat aliases
        self.pipeline_cv_ = best_pipe
        self.model_cv_ = en_best

        logger.info(
            "EN (TSCV) fit completed | l1_ratio={:.3f} | alpha*={:.6g} | rule={} | "
            "threshold_divisor={} | coef_tol={} | selected={}".format(
                self.l1_ratio,
                self.best_alpha_,
                self.selection_rule,
                self.threshold_divisor,
                self.coef_tol,
                len(selected),
            )
        )
        return self

    def get_result(self) -> dict:
        return {
            "selected_features": self.selected_features_,
            "coef_series": self.coef_series_,
            "coef_series_selected": self.coef_series_selected_,
            "best_alpha": self.best_alpha_,
            "l1_ratio": self.l1_ratio,
            "pipeline": self.pipeline_,
            "model": self.model_,
            "pipeline_cv": self.pipeline_cv_,  # same as pipeline
            "model_cv": self.model_cv_,        # same as model
            "selection_rule": self.selection_rule,
            "threshold_divisor": self.threshold_divisor,
            "coef_tol": self.coef_tol,
            "tcv_splits": self.tcv_splits,
            "test_size": self.test_size,
            "gap": self.gap,
            "max_train_size": self.max_train_size,
            "k_indicators": self.k_indicators,
            "fit_intercept": self.fit_intercept,
            "with_mean": self.with_mean,
            "with_std": self.with_std,
            "random_state": self.random_state,
            "max_iter": self.max_iter,
            "alphas": self._normalize_alpha_grid(),
            "scoring": self.scoring,
            "n_jobs": self.n_jobs,
            "refit": self.refit,
        }
