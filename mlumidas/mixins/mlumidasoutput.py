import re
from typing import Dict, Optional, Iterable, Set

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


class MLUMidasOutputMixin:
    """
    Build per-branch (latest/selected), per-criterion, per-period plots from MLUMidas results_dict.

    Supports three pooled outputs:
      - results_dict["model"]["periods_avg"]
      - results_dict["model"]["periods_median"]
      - results_dict["model"]["periods_mseweight"]
    """

    # ------------------------ #
    # ------ Utilities ------- #
    # ------------------------ #

    @staticmethod
    def _empty_figure(title: str, xlabel: str = "Quarter", ylabel: str = "GDP", figsize=(14, 8)):
        """Create a consistent empty figure with title and axes labels."""
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        fig.tight_layout()
        plt.close(fig)  # prevent auto-display
        return fig

    @staticmethod
    def _merge_title(extra: Optional[str], base: str) -> str:
        """Place an optional extra title line above the base title."""
        return f"{extra}\n{base}" if extra else base

    # ------------------------ #
    # ---- Quarter Series ---- #
    # ------------------------ #

    def _plot_quarter_series(
        self,
        df_quarters: pd.DataFrame,
        title: str,
        ci_lower: Optional[pd.Series] = None,
        ci_upper: Optional[pd.Series] = None,
    ):
        # include AR(4) column in the candidate list
        cols_present = [c for c in ["y_actual", "y_pred", "y_pred_ar4"] if c in df_quarters.columns]
        if not cols_present:
            return self._empty_figure(f"{title} (no y_actual/y_pred columns found)")

        dfp = df_quarters[cols_present].dropna(how="all").copy()

        # --- extract quarters and years
        if isinstance(dfp.index, pd.PeriodIndex):
            quarters = [f"Q{p.quarter}" for p in dfp.index]
            years = [str(p.year) for p in dfp.index]
            dt_index = dfp.index.to_timestamp()
        else:
            dt_index = pd.to_datetime(dfp.index)
            quarters = [f"Q{d.quarter}" for d in dt_index]
            years = [str(d.year) for d in dt_index]

        x_pos = np.arange(len(dfp))

        # --- plot main series
        fig, ax = plt.subplots(figsize=(14, 8))
        if "y_actual" in dfp:
            ax.plot(x_pos, dfp["y_actual"], marker="o", linestyle="-", color="k", label="Actual GDP")
        if "y_pred" in dfp:
            ax.plot(x_pos, dfp["y_pred"], marker="o", linestyle="-", color="C0", label="Predicted GDP")
        if "y_pred_ar4" in dfp:
            ax.plot(
                x_pos,
                dfp["y_pred_ar4"],
                marker="o",
                linestyle="-",
                color="0.5",
                label="Predicted GDP (AR4)",
            )

        # --- optional CI band (aligned to index)
        if ci_lower is not None and ci_upper is not None:
            try:
                # align to the datetime index used for plotting
                ci_lo_a = pd.to_numeric(ci_lower.reindex(dt_index), errors="coerce").to_numpy(dtype=float)
                ci_hi_a = pd.to_numeric(ci_upper.reindex(dt_index), errors="coerce").to_numpy(dtype=float)
                if np.isfinite(ci_lo_a).any() and np.isfinite(ci_hi_a).any():
                    ax.fill_between(x_pos, ci_lo_a, ci_hi_a, color="C0", alpha=0.15, label="95% CI", zorder=1.5)
            except Exception:
                # be permissive—if CI cannot be aligned, just skip
                pass

        ax.set_title(title)
        ax.set_ylabel("GDP")
        ax.legend()
        ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5, alpha=0.6)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(quarters)

        # --- compute contiguous year runs for label positions
        year_positions, year_labels = [], []
        n = len(years)
        i = 0
        while i < n:
            y = years[i]
            j = i + 1
            while j < n and years[j] == y:
                j += 1
            mid = (i + (j - 1)) / 2.0
            year_positions.append(mid)
            year_labels.append(y)
            i = j

        # --- years axis (bottom)
        ax_year = ax.twiny()
        ax_year.set_xlim(ax.get_xlim())
        ax_year.set_xticks(year_positions)
        ax_year.set_xticklabels(year_labels)
        ax_year.xaxis.set_ticks_position("bottom")
        ax_year.xaxis.set_label_position("bottom")
        ax_year.spines["bottom"].set_position(("axes", -0.15))
        ax_year.spines["top"].set_visible(False)
        ax_year.set_xlabel("")
        ax_year.tick_params(axis="x", pad=2)

        # --- third axis: Avg RMSE per year (below years)
        if "rmse" in df_quarters.columns or "avg_rmse_y" in df_quarters.columns:
            if "avg_rmse_y" in df_quarters.columns:
                rmse_by_year = (
                    pd.Series(df_quarters["avg_rmse_y"].to_numpy(), index=dt_index.year).groupby(level=0).first()
                )
            else:
                rmse_by_year = (
                    pd.Series(df_quarters["rmse"].to_numpy(), index=dt_index.year).groupby(level=0).mean()
                )

            rmse_map = {str(int(k)): float(v) for k, v in rmse_by_year.items() if np.isfinite(v)}
            rmse_tick_labels = [f"{rmse_map[y]:.2f}" if y in rmse_map else "" for y in year_labels]

            ax_rmse = ax.twiny()
            ax_rmse.set_xlim(ax.get_xlim())
            ax_rmse.set_xticks(year_positions)
            ax_rmse.set_xticklabels(rmse_tick_labels)
            ax_rmse.xaxis.set_ticks_position("bottom")
            ax_rmse.xaxis.set_label_position("bottom")
            ax_rmse.spines["bottom"].set_position(("axes", -0.30))  # below years axis
            ax_rmse.spines["top"].set_visible(False)
            ax_rmse.set_xlabel("Avg RMSE (year)")
            ax_rmse.tick_params(axis="x", pad=2)

            # info box with total & median RMSE + MSE
            rmse_series = pd.to_numeric(df_quarters.get("rmse", pd.Series(dtype=float)), errors="coerce").dropna()
            mse_series = pd.to_numeric(df_quarters.get("mse", pd.Series(dtype=float)), errors="coerce").dropna()
            if rmse_series.size:
                total_rmse = float(rmse_series.sum()) if not rmse_series.empty else np.nan
                avg_rmse = float(rmse_series.mean()) if not rmse_series.empty else np.nan
                median_rmse = float(rmse_series.median()) if not rmse_series.empty else np.nan

                total_mse = float(mse_series.sum()) if not mse_series.empty else np.nan
                avg_mse = float(mse_series.mean()) if not mse_series.empty else np.nan
                median_mse = float(mse_series.median()) if not mse_series.empty else np.nan

                textstr = (
                    f"Avg RMSE: {avg_rmse:.2f}\n"
                    f"Median RMSE: {median_rmse:.2f}\n"
                    f"Total RMSE: {total_rmse:.2f}\n\n"
                    f"Avg MSE: {avg_mse:.2f}\n"
                    f"Median MSE: {median_mse:.2f}\n"
                    f"Total MSE: {total_mse:.2f}"
                )
                ax.text(
                    0.02,
                    0.98,
                    textstr,
                    transform=ax.transAxes,
                    ha="left",
                    va="top",
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
                )

        # --- fourth axis: Avg MSE per year (below RMSE)
        if "mse" in df_quarters.columns or "avg_mse_y" in df_quarters.columns:
            if "avg_mse_y" in df_quarters.columns:
                mse_by_year = (
                    pd.Series(df_quarters["avg_mse_y"].to_numpy(), index=dt_index.year).groupby(level=0).first()
                )
            else:
                mse_by_year = (
                    pd.Series(df_quarters["mse"].to_numpy(), index=dt_index.year).groupby(level=0).mean()
                )

            mse_map = {str(int(k)): float(v) for k, v in mse_by_year.items() if np.isfinite(v)}
            mse_tick_labels = [f"{mse_map[y]:.2f}" if y in mse_map else "" for y in year_labels]

            ax_mse = ax.twiny()
            ax_mse.set_xlim(ax.get_xlim())
            ax_mse.set_xticks(year_positions)
            ax_mse.set_xticklabels(mse_tick_labels)
            ax_mse.xaxis.set_ticks_position("bottom")
            ax_mse.xaxis.set_label_position("bottom")
            ax_mse.spines["bottom"].set_position(("axes", -0.45))  # below RMSE axis
            ax_mse.spines["top"].set_visible(False)
            ax_mse.set_xlabel("Avg MSE (year)")
            ax_mse.tick_params(axis="x", pad=2)

        fig.tight_layout()
        plt.close(fig)  # prevent auto-display
        return fig

    def get_oof_plots(self, results_dict: Dict, title: Optional[str] = None):
        """
        Returns nested dict of per-period figures for three pools (avg, median, mseweight),
        split by branch (latest/selected) and criterion.

        {
          "avg":       {"latest": {crit: {period: fig, ...}, ...}, "selected": {...}},
          "median":    {"latest": {...}, "selected": {...}},
          "mseweight": {"latest": {...}, "selected": {...}}
        }
        """
        plots = {
            "avg": {"latest": {}, "selected": {}},
            "median": {"latest": {}, "selected": {}},
            "mseweight": {"latest": {}, "selected": {}},
        }

        model = results_dict.get("model", {})
        periods_avg = model.get("periods_avg", {})
        periods_median = model.get("periods_median", {})
        periods_mseweight = model.get("periods_mseweight", {})
        periods_details_all = model.get("periods_details", {})  # branch -> crit -> quarter -> period -> df

        def _build_ci_for_period(branch: str, crit: str, period: str, index_like):
            """
            For a given period's quarterly series, assemble per-quarter CI from periods_details:
            expects details at results_dict['model']['periods_details'][branch][crit][quarter][period]
            with rows 'ci_lower' and 'ci_upper' and a column 'y_pred'.
            """
            ci_lo = pd.Series(index=pd.to_datetime(index_like if not isinstance(index_like, pd.PeriodIndex) else index_like.to_timestamp()), dtype=float)
            ci_hi = ci_lo.copy()
            details_map = periods_details_all.get(branch, {}).get(crit, {})
            if not details_map:
                return None, None

            # Keys in details_map are the *quarter* identifiers used by your pipeline (often Periods or Timestamps)
            for q in ci_lo.index:
                # try exact key first, then tolerant conversions
                key_candidates = [q]
                if isinstance(q, pd.Timestamp):
                    key_candidates.append(q.to_period("Q"))
                else:
                    try:
                        key_candidates.append(pd.Timestamp(q))
                    except Exception:
                        pass
                df_detail = None
                for kc in key_candidates:
                    df_detail = details_map.get(kc, {}).get(period)
                    if isinstance(df_detail, pd.DataFrame):
                        break
                    df_detail = None

                if isinstance(df_detail, pd.DataFrame) and "y_pred" in df_detail.columns:
                    if "ci_lower" in df_detail.index:
                        try:
                            ci_lo.loc[q] = float(df_detail.loc["ci_lower", "y_pred"])
                        except Exception:
                            pass
                    if "ci_upper" in df_detail.index:
                        try:
                            ci_hi.loc[q] = float(df_detail.loc["ci_upper", "y_pred"])
                        except Exception:
                            pass

            # Return None if both are entirely NaN
            if not np.isfinite(ci_lo.to_numpy(dtype=float)).any() and not np.isfinite(ci_hi.to_numpy(dtype=float)).any():
                return None, None
            return ci_lo, ci_hi

        # helper to render one pool
        def _render_pool(pool_name: str, pool_src: Dict):
            for branch in ["latest", "selected"]:
                branch_src = pool_src.get(branch, {})
                plots[pool_name][branch] = {}

                for crit in sorted(branch_src.keys()):
                    plots[pool_name][branch].setdefault(crit, {})
                    periods_dict = branch_src.get(crit, {})
                    for period, df_quarters in periods_dict.items():
                        if isinstance(df_quarters, pd.DataFrame) and not df_quarters.empty:
                            base = f"{pool_name.capitalize()} | {branch} | {crit.upper()} | {period}"
                            ci_lo, ci_hi = _build_ci_for_period(branch, crit, period, df_quarters.index)
                            fig = self._plot_quarter_series(
                                df_quarters,
                                self._merge_title(title, base),
                                ci_lower=ci_lo,
                                ci_upper=ci_hi,
                            )
                        else:
                            base = f"{pool_name.capitalize()} | {branch} | {crit.upper()} | {period} (no data)"
                            fig = self._empty_figure(self._merge_title(title, base))
                        plots[pool_name][branch][crit][period] = fig

        _render_pool("avg", periods_avg)
        _render_pool("median", periods_median)
        _render_pool("mseweight", periods_mseweight)

        return plots

    # -------------------------------- #
    # ---- All Periods (Overlays) ---- #
    # -------------------------------- #

    def _plot_all_periods_series(self, periods_dict: Dict[str, pd.DataFrame], title: str):
        # keep only non-empty frames
        period_frames = {p: df for p, df in periods_dict.items() if isinstance(df, pd.DataFrame) and not df.empty}
        if not period_frames:
            return self._empty_figure(f"{title} (no data)")

        # sort periods naturally by trailing int if present (p1, p2, ...); fallback to name
        def _pkey(p):
            m = re.search(r"(\d+)$", str(p))
            return (0, int(m.group(1))) if m else (1, str(p))

        periods_sorted = sorted(period_frames.keys(), key=_pkey)

        # union index across periods, convert to DatetimeIndex
        def _to_dtindex(df):
            return df.index.to_timestamp() if isinstance(df.index, pd.PeriodIndex) else pd.to_datetime(df.index)

        all_idx = None
        for df in period_frames.values():
            idx = _to_dtindex(df)
            all_idx = idx if all_idx is None else all_idx.union(idx)
        all_idx = all_idx.sort_values()

        # y_actual (assume identical across periods; fall back to first)
        first_df = period_frames[periods_sorted[0]]
        idx0 = _to_dtindex(first_df)
        y_actual = pd.Series(first_df.get("y_actual", pd.Series(index=idx0, dtype=float)).values, index=idx0).reindex(
            all_idx
        )

        # AR4 line (take from first df that has it)
        y_ar4 = None
        for df in period_frames.values():
            if "y_pred_ar4" in df.columns:
                idx = _to_dtindex(df)
                y_ar4 = pd.Series(df["y_pred_ar4"].values, index=idx).reindex(all_idx)
                break

        # predictions per period
        preds = {}
        for p in periods_sorted:
            df = period_frames[p]
            idx = _to_dtindex(df)
            if "y_pred" in df.columns:
                preds[p] = pd.Series(df["y_pred"].values, index=idx).reindex(all_idx)

        # compute ticks
        quarters = [f"Q{d.quarter}" for d in all_idx]
        years = [str(d.year) for d in all_idx]
        x_pos = np.arange(len(all_idx))

        fig, ax = plt.subplots(figsize=(14, 8))

        # main lines
        if y_actual.notna().any():
            ax.plot(x_pos, y_actual.values, marker="o", linestyle="-", color="k", label="Actual GDP")
        if y_ar4 is not None and y_ar4.notna().any():
            ax.plot(x_pos, y_ar4.values, marker="o", linestyle="-", color="0.5", label="Predicted GDP (AR4)")

        # period prediction lines: shades of blue + increasing linewidth
        nP = len(preds)
        lw_min, lw_max = 0.8, 3.0
        cmap = plt.get_cmap("Blues")
        # avoid ultra-pale/near-white & near-black extremes
        t_min, t_max = 0.45, 0.95

        for i, p in enumerate(periods_sorted):
            if p not in preds:
                continue
            # shade: first period light, last period dark
            t = t_max if nP == 1 else (t_min + (t_max - t_min) * (i / (nP - 1)))
            color = cmap(t)
            # thickness ramp
            lw = lw_min if nP == 1 else (lw_min + (lw_max - lw_min) * (i / (nP - 1)))
            ax.plot(
                x_pos,
                preds[p].values,
                marker="o",
                linestyle="-",
                color=color,
                linewidth=lw,
                label=f"Predicted GDP ({p})",
            )

        ax.set_title(title)
        ax.set_ylabel("GDP")
        ax.legend()
        ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(quarters)

        # year centers
        year_positions, year_labels = [], []
        n = len(years)
        i = 0
        while i < n:
            y = years[i]
            j = i + 1
            while j < n and years[j] == y:
                j += 1
            mid = (i + (j - 1)) / 2.0
            year_positions.append(mid)
            year_labels.append(y)
            i = j

        # years axis
        ax_year = ax.twiny()
        ax_year.set_xlim(ax.get_xlim())
        ax_year.set_xticks(year_positions)
        ax_year.set_xticklabels(year_labels)
        ax_year.xaxis.set_ticks_position("bottom")
        ax_year.xaxis.set_label_position("bottom")
        ax_year.spines["bottom"].set_position(("axes", -0.15))
        ax_year.spines["top"].set_visible(False)
        ax_year.set_xlabel("")
        ax_year.tick_params(axis="x", pad=2)

        # ===== Yearly averages across ALL periods for RMSE & MSE =====
        rmse_concat, mse_concat = [], []
        for _, df in period_frames.items():
            idx = _to_dtindex(df)
            if "rmse" in df.columns:
                rmse_concat.append(pd.Series(pd.to_numeric(df["rmse"], errors="coerce").values, index=idx.year))
            else:
                if "mse" in df.columns and "mse_ar4" in df.columns:
                    r = pd.to_numeric(df["mse"], errors="coerce") / pd.to_numeric(df["mse_ar4"], errors="coerce")
                    rmse_concat.append(pd.Series(r.values, index=idx.year))
            if "mse" in df.columns:
                mse_concat.append(pd.Series(pd.to_numeric(df["mse"], errors="coerce").values, index=idx.year))
            elif {"y_actual", "y_pred"} <= set(df.columns):
                se = (pd.to_numeric(df["y_actual"], errors="coerce") - pd.to_numeric(df["y_pred"], errors="coerce")) ** 2
                mse_concat.append(pd.Series(se.values, index=idx.year))

        rmse_by_year_all = pd.concat(rmse_concat).groupby(level=0).mean() if rmse_concat else pd.Series(dtype=float)
        mse_by_year_all = pd.concat(mse_concat).groupby(level=0).mean() if mse_concat else pd.Series(dtype=float)

        # third axis: Avg RMSE (year, all periods)
        if not rmse_by_year_all.empty:
            rmse_map = {str(int(k)): float(v) for k, v in rmse_by_year_all.items() if np.isfinite(v)}
            rmse_tick_labels = [f"{rmse_map[y]:.2f}" if y in rmse_map else "" for y in year_labels]

            ax_rmse = ax.twiny()
            ax_rmse.set_xlim(ax.get_xlim())
            ax_rmse.set_xticks(year_positions)
            ax_rmse.set_xticklabels(rmse_tick_labels)
            ax_rmse.xaxis.set_ticks_position("bottom")
            ax_rmse.xaxis.set_label_position("bottom")
            ax_rmse.spines["bottom"].set_position(("axes", -0.30))
            ax_rmse.spines["top"].set_visible(False)
            ax_rmse.set_xlabel("Avg RMSE (year, all periods)")
            ax_rmse.tick_params(axis="x", pad=2)

            # info box across ALL periods
            rmse_all_vals = pd.concat(rmse_concat, axis=0) if rmse_concat else pd.Series(dtype=float)
            rmse_all_vals = pd.to_numeric(rmse_all_vals, errors="coerce").dropna()
            mse_all_vals = pd.concat(mse_concat, axis=0) if mse_concat else pd.Series(dtype=float)
            mse_all_vals = pd.to_numeric(mse_all_vals, errors="coerce").dropna()
            if not rmse_all_vals.empty or not mse_all_vals.empty:
                text_lines = []
                if not rmse_all_vals.empty:
                    text_lines += [
                        f"Avg RMSE: {rmse_all_vals.mean():.2f}",
                        f"Median RMSE: {rmse_all_vals.median():.2f}",
                        f"Total RMSE: {rmse_all_vals.sum():.2f}",
                        "",
                    ]
                if not mse_all_vals.empty:
                    text_lines += [
                        f"Avg MSE: {mse_all_vals.mean():.2f}",
                        f"Median MSE: {mse_all_vals.median():.2f}",
                        f"Total MSE: {mse_all_vals.sum():.2f}",
                    ]
                ax.text(
                    0.02,
                    0.98,
                    "\n".join(text_lines),
                    transform=ax.transAxes,
                    ha="left",
                    va="top",
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
                )

        # fourth axis: Avg MSE (year, all periods)
        if not mse_by_year_all.empty:
            mse_map = {str(int(k)): float(v) for k, v in mse_by_year_all.items() if np.isfinite(v)}
            mse_tick_labels = [f"{mse_map[y]:.2f}" if y in mse_map else "" for y in year_labels]

            ax_mse = ax.twiny()
            ax_mse.set_xlim(ax.get_xlim())
            ax_mse.set_xticks(year_positions)
            ax_mse.set_xticklabels(mse_tick_labels)
            ax_mse.xaxis.set_ticks_position("bottom")
            ax_mse.xaxis.set_label_position("bottom")
            ax_mse.spines["bottom"].set_position(("axes", -0.45))
            ax_mse.spines["top"].set_visible(False)
            ax_mse.set_xlabel("Avg MSE (year, all periods)")
            ax_mse.tick_params(axis="x", pad=2)

        fig.tight_layout()
        plt.close(fig)  # prevent auto-display in notebooks
        return fig

    def get_oof_all_periods_plots(self, results_dict: Dict, title: Optional[str] = None):
        """
        Overlays ALL periods on one figure per (pool, branch, criterion).

        Returns:
            {
              "avg":       {"latest": {crit: fig, ...}, "selected": {crit: fig, ...}},
              "median":    {"latest": {crit: fig, ...}, "selected": {crit: fig, ...}},
              "mseweight": {"latest": {crit: fig, ...}, "selected": {crit: fig, ...}}
            }
        """
        plots = {"avg": {"latest": {}, "selected": {}},
                 "median": {"latest": {}, "selected": {}},
                 "mseweight": {"latest": {}, "selected": {}}}

        model = results_dict.get("model", {})
        periods_avg = model.get("periods_avg", {})
        periods_median = model.get("periods_median", {})
        periods_mseweight = model.get("periods_mseweight", {})

        for pool_name, pool_src in {"avg": periods_avg, "median": periods_median, "mseweight": periods_mseweight}.items():
            for branch in ["latest", "selected"]:
                branch_src = pool_src.get(branch, {})
                for crit in sorted(branch_src.keys()):
                    periods_dict = branch_src.get(crit, {})
                    base = f"All Periods | {pool_name.capitalize()} | {branch} | {crit.upper()}"
                    plots[pool_name][branch][crit] = self._plot_all_periods_series(periods_dict, self._merge_title(title, base))

        return plots

    # ------------------------------------------- #
    # ---- Single Quarter Across All Periods ---- #
    # ------------------------------------------- #

    def _plot_single_quarter_across_periods(
        self,
        quarter,
        periods_avg_dict,
        periods_details_dict,
        title: str,
        group_by: Optional[str] = None,
    ):
        """
        One figure for a given quarter, periods on x-axis.
        - Blue line: average y_pred across selected series for each period
        - Light-blue band: CI (ci_lower..ci_upper) per period (from details df)
        - Stacked bars: contributions of groups (component/subcategory/category) to the average y_pred
        - Last period: black diamond for y_actual, grey dot for AR4
        - Stats box: Avg MSE (all periods) and RMSE = MSE(last)/MSE_AR4(last)
        - Legend shown below plot with all group names
        """

        def _pkey(p):
            m = re.search(r"(\d+)$", str(p))
            return (0, int(m.group(1))) if m else (1, str(p))

        periods_sorted = sorted(list(periods_avg_dict.keys()), key=_pkey)
        if not periods_sorted:
            return self._empty_figure(f"{title} (no periods)", xlabel="Period")

        y_pred, y_act, y_ar4, ci_lo, ci_hi, mse_vals, mse_ar4_vals = [], [], [], [], [], [], []

        # collect all possible groups across periods for stable colors/order
        groups_all = []
        if group_by:
            gset = set()
            for p in periods_sorted:
                df_detail = periods_details_dict.get(quarter, {}).get(p)
                if isinstance(df_detail, pd.DataFrame) and group_by in df_detail.columns:
                    mask = ~df_detail.index.isin(["Average", "Median", "ci_lower", "ci_upper"])
                    gset.update(df_detail.loc[mask, group_by].fillna(f"no_{group_by}").astype(str).unique())
            groups_all = sorted(gset)

        # per-period group contributions (to the average)
        per_period_group_contribs = []
        for p in periods_sorted:
            df_q = periods_avg_dict.get(p)
            v_pred = v_act = v_ar4 = v_mse = v_mse_ar4 = np.nan
            if isinstance(df_q, pd.DataFrame) and (quarter in df_q.index):
                row = df_q.loc[quarter]
                v_pred = float(row.get("y_pred", np.nan))
                v_act = float(row.get("y_actual", np.nan))
                v_ar4 = float(row.get("y_pred_ar4", np.nan))
                v_mse = float(row.get("mse", np.nan))
                v_mse_ar4 = float(row.get("mse_ar4", np.nan))

            cl = cu = np.nan
            df_detail = periods_details_dict.get(quarter, {}).get(p)
            if isinstance(df_detail, pd.DataFrame) and "y_pred" in df_detail.columns:
                if "ci_lower" in df_detail.index:
                    cl = float(df_detail.loc["ci_lower", "y_pred"])
                if "ci_upper" in df_detail.index:
                    cu = float(df_detail.loc["ci_upper", "y_pred"])

            y_pred.append(v_pred)
            y_act.append(v_act)
            y_ar4.append(v_ar4)
            ci_lo.append(cl)
            ci_hi.append(cu)
            mse_vals.append(v_mse)
            mse_ar4_vals.append(v_mse_ar4)

            gcontrib = {}
            if group_by and isinstance(df_detail, pd.DataFrame) and group_by in df_detail.columns:
                mask = ~df_detail.index.isin(["Average", "Median", "ci_lower", "ci_upper"])
                sub = df_detail.loc[mask, [group_by, "y_pred"]].copy()
                sub[group_by] = sub[group_by].fillna(f"no_{group_by}").astype(str)
                sub["y_pred"] = pd.to_numeric(sub["y_pred"], errors="coerce")
                sub = sub.dropna(subset=["y_pred"])
                N = len(sub)
                if N > 0:
                    sums = sub.groupby(group_by)["y_pred"].sum()
                    gcontrib = (sums / N).to_dict()  # contributions that stack to the overall average
            per_period_group_contribs.append(gcontrib)

        x = np.arange(len(periods_sorted))
        fig, ax = plt.subplots(figsize=(14, 7))

        # stacked bars: group contributions to average (behind line)
        if groups_all:
            cmap = plt.cm.get_cmap("tab20", len(groups_all))
            width = 0.6
            bottoms_pos = np.zeros_like(x, dtype=float)
            bottoms_neg = np.zeros_like(x, dtype=float)
            for gi, g in enumerate(groups_all):
                color = cmap(gi)
                heights = np.array([float(per_period_group_contribs[i].get(g, 0.0)) for i in range(len(x))])
                pos = heights >= 0
                if pos.any():
                    ax.bar(
                        x[pos],
                        heights[pos],
                        width=width,
                        bottom=bottoms_pos[pos],
                        color=color,
                        alpha=0.45,
                        zorder=1,
                    )
                    bottoms_pos[pos] += heights[pos]
                neg = ~pos
                if neg.any():
                    ax.bar(
                        x[neg],
                        heights[neg],
                        width=width,
                        bottom=bottoms_neg[neg],
                        color=color,
                        alpha=0.45,
                        zorder=1,
                    )
                    bottoms_neg[neg] += heights[neg]

        # blue line: average y_pred per period
        ax.plot(x, y_pred, marker="o", linestyle="-", color="C0", label="Predicted GDP (avg)", zorder=2)

        # CI band
        ci_lo_a = np.array(ci_lo, dtype=float)
        ci_hi_a = np.array(ci_hi, dtype=float)
        if np.isfinite(ci_lo_a).any() and np.isfinite(ci_hi_a).any():
            ax.fill_between(x, ci_lo_a, ci_hi_a, color="C0", alpha=0.15, zorder=1.5, label="95% CI")

        # last-period markers
        i_last = len(x) - 1
        if i_last >= 0:
            if np.isfinite(y_act[i_last]):
                ax.plot(
                    x[i_last],
                    y_act[i_last],
                    marker="D",
                    markersize=10,
                    linestyle="None",
                    color="k",
                    label="Actual (last period)",
                    zorder=3,
                )
            if np.isfinite(y_ar4[i_last]):
                ax.plot(
                    x[i_last],
                    y_ar4[i_last],
                    marker="o",
                    markersize=8,
                    linestyle="None",
                    color="0.5",
                    label="AR4 (last period)",
                    zorder=3,
                )

        # axes styling
        ax.set_title(title)
        ax.set_xlabel("Period")
        ax.set_ylabel("GDP")
        ax.set_xticks(x)
        ax.set_xticklabels(periods_sorted)
        ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5, alpha=0.6)

        # stats box
        mse_arr = np.array(mse_vals, dtype=float)
        mse_ar4_arr = np.array(mse_ar4_vals, dtype=float)
        avg_mse = float(np.nanmean(mse_arr)) if np.isfinite(mse_arr).any() else np.nan
        rmse_last = np.nan
        if np.isfinite(mse_arr[i_last]) and np.isfinite(mse_ar4_arr[i_last]) and mse_ar4_arr[i_last] != 0:
            rmse_last = float(mse_arr[i_last] / mse_ar4_arr[i_last])
        lines = [f"Avg MSE (all periods): {avg_mse:.2f}"]
        if np.isfinite(rmse_last):
            lines.append(f"RMSE (last/AR4): {rmse_last:.2f}")
        ax.text(
            0.02,
            0.98,
            "\n".join(lines),
            transform=ax.transAxes,
            ha="left",
            va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        # custom legend BELOW plot with all group names included
        handles = [
            Line2D([0], [0], color="C0", marker="o", linestyle="-", label="Predicted GDP (avg)"),
            Patch(facecolor="C0", alpha=0.15, label="95% CI"),
            Line2D([0], [0], color="k", marker="D", linestyle="None", label="Actual (last period)"),
            Line2D([0], [0], color="0.5", marker="o", linestyle="None", label="AR4 (last period)"),
        ]
        if groups_all:
            cmap = plt.cm.get_cmap("tab20", len(groups_all))
            handles.extend(Patch(facecolor=cmap(gi), label=str(g)) for gi, g in enumerate(groups_all))

        ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=min(len(handles), 6), frameon=True)

        fig.tight_layout()
        plt.close(fig)
        return fig
        
    def get_oof_single_quarter_plots(
        self,
        results_dict: Dict,
        quarter_plots: Optional[Iterable[pd.Timestamp]] = None,
        group_by: Optional[str] = None,
        title: Optional[str] = None,
    ):
        """
        Build single-quarter plots across periods for three pools (avg, median, mseweight).

        Parameters
        ----------
        results_dict : Dict
            Results dictionary with keys:
            - model.periods_avg
            - model.periods_median
            - model.periods_mseweight
            - model.periods_details
        quarter_plots : Iterable[pd.Timestamp] or None
            If None or empty, all available quarters are plotted.
            Otherwise, only those in the list/set are plotted.
        group_by : Optional[str]
            One of {"component","subcategory","category"} or None.
        title : Optional[str]
            Title prefix merged with the auto-generated title per figure.
        """
        plots = {
            "avg": {"latest": {}, "selected": {}},
            "median": {"latest": {}, "selected": {}},
            "mseweight": {"latest": {}, "selected": {}},
        }

        model = results_dict.get("model", {})
        periods_avg_all = model.get("periods_avg", {})
        periods_med_all = model.get("periods_median", {})
        periods_msew_all = model.get("periods_mseweight", {})
        periods_details_all = model.get("periods_details", {})

        # Normalize quarters: None or empty → plot all
        requested_q_set: Optional[Set[pd.Timestamp]] = None
        if quarter_plots is not None:
            q_list = [pd.Timestamp(q) for q in quarter_plots]
            if len(q_list) > 0:
                requested_q_set = set(q_list)  # only filter if non-empty

        for pool_name, pool_src in {"avg": periods_avg_all, "median": periods_med_all, "mseweight": periods_msew_all}.items():
            for branch in ["latest", "selected"]:
                branch_src = pool_src.get(branch, {})
                plots[pool_name][branch] = {}

                for crit, periods_dict in branch_src.items():
                    # union available quarters
                    available_quarters = pd.Index([])
                    for _, df_q in periods_dict.items():
                        if isinstance(df_q, pd.DataFrame):
                            available_quarters = available_quarters.union(df_q.index)

                    try:
                        available_quarters = pd.to_datetime(available_quarters)
                    except Exception:
                        pass

                    # Filter to requested quarters (if given and non-empty)
                    if requested_q_set is not None:
                        q_to_plot = [q for q in available_quarters if pd.Timestamp(q) in requested_q_set]
                    else:
                        q_to_plot = list(available_quarters)

                    plots[pool_name][branch][crit] = {}

                    if not q_to_plot:
                        continue

                    periods_details_dict = periods_details_all.get(branch, {}).get(crit, {})

                    for q in q_to_plot:
                        date = pd.Timestamp(q)
                        base = f"Single Quarter | {pool_name} | {branch} | {crit.upper()} | {date.year}Q{date.quarter}"
                        fig = self._plot_single_quarter_across_periods(
                            quarter=date,
                            periods_avg_dict=periods_dict,
                            periods_details_dict=periods_details_dict,
                            title=self._merge_title(title, base),
                            group_by=group_by,
                        )
                        plots[pool_name][branch][crit][date] = fig

        return plots
