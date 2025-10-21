from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, List
import re

import numpy as np
import pandas as pd
from loguru import logger
import statsmodels.api as sm


@dataclass
class PYHARDT:
    """
    Hard-threshold selector run directly on the provided X and y.

    For each candidate column v in X (excluding y-lag controls), run:
        y_t = a + (y-lag controls from X) + b * v_t + e_t
    using plain OLS, and record t- and p-values for b.

    Selection:
      - If k_indicators > 0: choose the top-k by |t|.
      - Else: choose all with p <= 1 - significance_level.

    Parameters
    ----------
    y_var : str
        Name of the dependent variable (used only to detect y-lag controls).
        A column in X is treated as a y-lag control iff it matches:
            ^{y_var}_lag\\d+$
    significance_level : float
        α in (0,1). If k_indicators == 0 or None, we keep p <= 1-α.
        Examples: α=0.95 → p<=0.05 ; α=0.99 → p<=0.01.
    k_indicators : int | None
        If >0, pick top-k by |t| (ignores α).

    Attributes after fit()
    ----------------------
    selected_features_ : list[str]
        Chosen predictors (NOT including y-lag controls).
    t_stats_ : pd.Series
        t-stat per candidate column.
    p_values_ : pd.Series
        p-value per candidate column.
    y_lag_controls_ : list[str]
        The y-lag controls detected inside X and used in every regression.
    """

    y_var: str
    significance_level: float = 0.99
    k_indicators: Optional[int] = None

    # Fitted artifacts
    selected_features_: Optional[List[str]] = None
    t_stats_: Optional[pd.Series] = None
    p_values_: Optional[pd.Series] = None
    y_lag_controls_: Optional[List[str]] = None

    # --------------- helpers ---------------

    def _is_y_lag_col(self, col: str) -> bool:
        return re.match(rf"^{re.escape(self.y_var)}_lag\d+$", str(col)) is not None

    def _ols_one(self, yv: np.ndarray, Xmat: np.ndarray):
        """
        Plain OLS. Last column is the candidate v.
        Returns (t_value_for_v, p_value_for_v).
        """
        res = sm.OLS(yv, Xmat).fit()
        j = Xmat.shape[1] - 1  # candidate is last column
        return float(res.tvalues[j]), float(res.pvalues[j])

    # --------------- core API ---------------

    def fit(self, X: pd.DataFrame, y: pd.Series | pd.DataFrame):
        # Validate
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame.")
        if isinstance(y, pd.DataFrame):
            if y.shape[1] != 1:
                raise ValueError("y must be a 1-column DataFrame or a Series.")
            y = y.iloc[:, 0]
        if not isinstance(y, pd.Series):
            raise ValueError("y must be a pandas Series or a 1-col DataFrame.")

        # Ensure numeric
        X = X.apply(pd.to_numeric, errors="coerce")
        y = pd.to_numeric(y, errors="coerce")

        # Identify y-lag controls present in X
        y_lags = [c for c in X.columns if self._is_y_lag_col(c)]
        self.y_lag_controls_ = y_lags.copy()

        logger.info(
            f"Fitting PYHTOnX | X={X.shape} | y_len={len(y)} | y_var='{self.y_var}' | "
            f"controls={len(y_lags)} y-lags | α={self.significance_level} | k={self.k_indicators}"
        )

        # Candidate predictors = all columns EXCEPT y-lag controls
        candidates = [c for c in X.columns if c not in y_lags]
        if len(candidates) == 0:
            self.selected_features_ = []
            self.t_stats_ = pd.Series(dtype=float)
            self.p_values_ = pd.Series(dtype=float)
            logger.warning("No candidate predictors (only y-lags present).")
            return self

        t_dict: Dict[str, float] = {}
        p_dict: Dict[str, float] = {}

        for col in candidates:
            cols = []
            if len(y_lags) > 0:
                cols += y_lags
            cols += [col]

            # Align: drop rows with any NaN in y or the columns used
            df = pd.concat([y, X[cols]], axis=1).dropna()
            if df.empty:
                t_dict[col] = np.nan
                p_dict[col] = np.nan
                continue

            yv = df.iloc[:, 0].to_numpy(float)
            # X design: const + y-lags (if any) + candidate
            Xpart = df.iloc[:, 1:].to_numpy(float)
            Xmat = sm.add_constant(Xpart, has_constant="add")

            t_i, p_i = self._ols_one(yv, Xmat)
            t_dict[col] = t_i
            p_dict[col] = p_i

        t_ser = pd.Series(t_dict, dtype=float)
        p_ser = pd.Series(p_dict, dtype=float)

        # Rank by |t|
        order = np.argsort(-np.abs(t_ser.values))
        ranked = list(t_ser.index[order])

        # Selection
        if self.k_indicators is not None and int(self.k_indicators) > 0:
            k = int(self.k_indicators)
            selected = ranked[:k]
        else:
            alpha = float(self.significance_level)
            if not (0.0 < alpha < 1.0):
                raise ValueError("significance_level must be in (0,1).")
            p_cut = 1.0 - alpha
            selected = [c for c in ranked if p_ser[c] <= p_cut]

        self.selected_features_ = selected
        self.t_stats_ = t_ser
        self.p_values_ = p_ser

        logger.info(
            f"PYHARDT done | y-lag controls kept={len(y_lags)} | candidates={len(candidates)} | selected={len(selected)}"
        )
        return self

    def get_result(self) -> dict:
        return {
            "selected_features": self.selected_features_,
            "t_stats": self.t_stats_,
            "p_values": self.p_values_,
            "y_lag_controls": self.y_lag_controls_,
            "coef_series": self.t_stats_,
            "coef_series_selected": (
                self.t_stats_.loc[self.selected_features_]
                if self.selected_features_
                else pd.Series(dtype=float)
            ),
            "significance_level": self.significance_level,
            "k_indicators": self.k_indicators,
        }
