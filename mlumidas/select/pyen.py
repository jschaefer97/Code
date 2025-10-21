from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SelectionRule = Literal["pt", "cv_min", "cv_se", "cv_1se"]  # kept for backward-compat


@dataclass
class PYEN:
    """
    Elastic Net (or Lasso when l1_ratio=1.0) WITHOUT cross-validation.
    Uses a user-provided `lambda_fix` (alpha) directly.
    """

    # Core hyperparameters
    l1_ratio: float
    max_iter: int
    random_state: int
    with_mean: bool
    with_std: bool
    fit_intercept: bool
    selection_rule: SelectionRule
    se_factor: Optional[float]
    threshold_divisor: float
    coef_tol: float
    lambda_fix: float  # fixed alpha; must be > 0

    # Fitted attributes (kept for API compatibility)
    pipeline_cv_: Optional[any] = None         # always None here
    pipeline_: Optional[any] = None
    model_cv_: Optional[any] = None            # always None here
    model_: Optional[ElasticNet] = None
    coef_series_: Optional[pd.Series] = None
    coef_series_selected_: Optional[pd.Series] = None
    selected_features_: Optional[list[str]] = None
    best_alpha_: Optional[float] = None

    # ---------- Helpers (same selection behavior as before) ----------

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
        """
        Apply configured selection rule to coefficient vector.
        Non-'pt' rules use coef_tol to decide non-zeros.
        """
        if self.selection_rule == "pt":
            return self._apply_pt(coefs)
        else:
            mask = np.abs(coefs.values) > self.coef_tol
            return list(coefs.index[mask])

    # ---------- Core API ----------

    def fit(self, X: pd.DataFrame, y: pd.Series | pd.DataFrame):
        # Validate types
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame.")
        if not isinstance(y, (pd.Series, pd.DataFrame)):
            raise ValueError("y must be a pandas Series or a 1-col DataFrame.")
        if isinstance(y, pd.DataFrame):
            if y.shape[1] != 1:
                raise ValueError("y must be a 1-column DataFrame or a Series.")
            y = y.iloc[:, 0]

        logger.info(f"Fitting PYEN (no-CV) | X shape={X.shape}, y length={len(y)}")

        # Always use the provided lambda_fix
        self.best_alpha_ = float(self.lambda_fix)
        if not np.isfinite(self.best_alpha_) or self.best_alpha_ <= 0:
            raise ValueError("lambda_fix must be a positive finite float (> 0).")

        final_pipe = make_pipeline(
            StandardScaler(with_mean=self.with_mean, with_std=self.with_std),
            ElasticNet(
                alpha=self.best_alpha_,
                l1_ratio=self.l1_ratio,
                fit_intercept=self.fit_intercept,
                max_iter=self.max_iter,
                random_state=self.random_state,
            ),
        ).fit(X, y)

        en: ElasticNet = final_pipe.named_steps["elasticnet"]
        coefs = pd.Series(en.coef_, index=X.columns, dtype=float)

        # Selection
        selected = self._select_features(coefs)
        coef_sel = coefs.loc[selected]

        # Store
        self.pipeline_ = final_pipe
        self.model_ = en
        self.coef_series_ = coefs
        self.coef_series_selected_ = coef_sel
        self.selected_features_ = selected

        logger.info(
            "EN fit completed (no-CV) | l1_ratio={:.3f} | alpha={:.6g} | rule={} | "
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
        # Keep payload shape/keys identical to PYENCV for easy swapping
        return {
            "selected_features": self.selected_features_,
            "coef_series": self.coef_series_,
            "coef_series_selected": self.coef_series_selected_,
            "best_alpha": self.best_alpha_,
            "l1_ratio": self.l1_ratio,
            "pipeline_cv": self.pipeline_cv_,  # None
            "model_cv": self.model_cv_,        # None
            "pipeline": self.pipeline_,
            "model": self.model_,
            "selection_rule": self.selection_rule,
            "se_factor": self.se_factor,
            "threshold_divisor": self.threshold_divisor,
            "coef_tol": self.coef_tol,
        }
