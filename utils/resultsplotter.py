import os
import re
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class ResultsPlotter:
    """
    Make a single overlay plot across all periods for a given (method, weight),
    using the per-period DataFrames produced by your pipeline.

    Minimal style:
      - no AR(4) line
      - no bottom RMSE/MSE axes
      - no stats box
      - equal thickness across all periods
      - legend labels rename p1,p2,p3 -> h0,h1,h2 and say 'GDP Nowcast'
      - large, consistent font sizes
    """

    def __init__(self,
                 output_dir: str,
                 fmt: str = "png",
                 dpi: int = 150,
                 base_fontsize: int = 14,
                 year_axis_offset: float = -0.08):
        """
        Parameters
        ----------
        output_dir : str
            Folder where plots will be saved.
        fmt : str
            File format (e.g. 'png', 'pdf', 'svg').
        dpi : int
            Dots per inch when saving raster formats (e.g. png).
        base_fontsize : int
            Base fontsize applied to title, labels, ticks, and legend.
        year_axis_offset : float
            Position of the year axis below the main x-axis (negative moves closer).
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fmt = fmt.lower()
        self.dpi = dpi
        self.base_fs = int(base_fontsize)
        self.year_axis_offset = float(year_axis_offset)

    @staticmethod
    def _to_dtindex(df: pd.DataFrame) -> pd.DatetimeIndex:
        if isinstance(df.index, pd.PeriodIndex):
            return df.index.to_timestamp()
        return pd.to_datetime(df.index)

    @staticmethod
    def _rename_period_label(p: str) -> str:
        s = str(p)
        m = re.match(r"p(\d+)$", s, flags=re.IGNORECASE)
        if m:
            k = int(m.group(1))
            return f"h{k-1}"
        if re.match(r"h\d+$", s, flags=re.IGNORECASE):
            return s
        return s  # fallback (leave as-is)

    @staticmethod
    def _natural_pkey(p):
        m = re.search(r"(\d+)$", str(p))
        return (0, int(m.group(1))) if m else (1, str(p))

    def _empty_figure(self, title: str, xlabel: str = "Quarter", ylabel: str = "GDP", figsize=(14, 8)):
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title(title, fontsize=self.base_fs + 2)
        ax.set_xlabel(xlabel, fontsize=self.base_fs)
        ax.set_ylabel(ylabel, fontsize=self.base_fs)
        ax.tick_params(axis="both", labelsize=self.base_fs)
        fig.tight_layout()
        plt.close(fig)
        return fig

    def plot_all_periods(
        self,
        periods_dict: Dict[str, pd.DataFrame],
        title: Optional[str] = None,
        filename: Optional[str] = None,
        *,
        method_name: Optional[str] = None,
        oos_start: Optional[int] = None,
        oos_end: Optional[int] = None,
    ):
        """
        Build the overlay plot across all periods.

        Parameters
        ----------
        periods_dict : Dict[str, pd.DataFrame]
            Mapping period -> quarterly DataFrame with columns including
            (at least) 'y_actual' and/or 'y_pred'. Index must be PeriodIndex(Q) or DatetimeIndex.
        title : Optional[str]
            (Ignored if method_name and an OOS range are provided.) Figure title.
        filename : Optional[str]
            If provided, save under output_dir / f"{filename}.{fmt}". If omitted, a safe name is derived.
        method_name : Optional[str]
            Name of the method (e.g., 'LASSO', 'Elastic Net') to show in the title.
        oos_start, oos_end : Optional[int]
            Out-of-sample start/end years for the title. If missing, inferred from the data's index.

        Returns
        -------
        fig : matplotlib.figure.Figure
        """
        # keep only non-empty frames
        frames = {p: df for p, df in periods_dict.items() if isinstance(df, pd.DataFrame) and not df.empty}
        if not frames:
            return self._empty_figure(f"{title or 'All Periods'} (no data)")

        # sort periods
        periods_sorted = sorted(frames.keys(), key=self._natural_pkey)

        # union index across periods
        all_idx = None
        for df in frames.values():
            idx = self._to_dtindex(df)
            all_idx = idx if all_idx is None else all_idx.union(idx)
        all_idx = all_idx.sort_values()

        # actual series (from first available df)
        first_df = frames[periods_sorted[0]]
        idx0 = self._to_dtindex(first_df)
        y_actual = pd.Series(first_df.get("y_actual", pd.Series(index=idx0, dtype=float)).values, index=idx0).reindex(all_idx)

        # predictions per period (NO AR4)
        preds = {}
        for p in periods_sorted:
            df = frames[p]
            idx = self._to_dtindex(df)
            if "y_pred" in df.columns:
                preds[p] = pd.Series(df["y_pred"].values, index=idx).reindex(all_idx)

        # infer OOS range if not provided
        if oos_start is None or oos_end is None:
            try:
                years = [int(d.year) for d in all_idx]
                if years:
                    oos_start_inferred = min(years)
                    oos_end_inferred = max(years)
                else:
                    oos_start_inferred = oos_end_inferred = None
            except Exception:
                oos_start_inferred = oos_end_inferred = None
            oos_start = oos_start if oos_start is not None else oos_start_inferred
            oos_end = oos_end if oos_end is not None else oos_end_inferred

        # build the title: "<Method> — OOS: YYYY–YYYY"
        if method_name and (oos_start is not None) and (oos_end is not None):
            title_final = f"{method_name} — OOS: {oos_start}–{oos_end}"
        elif method_name:
            title_final = f"{method_name}"
        elif (oos_start is not None) and (oos_end is not None):
            title_final = f"OOS: {oos_start}–{oos_end}"
        else:
            title_final = title or "All Periods"

        # x axis labels
        all_idx = pd.DatetimeIndex(all_idx)
        quarters = [f"Q{d.quarter}" for d in all_idx]
        years_str = [str(d.year) for d in all_idx]
        x_pos = np.arange(len(all_idx))

        fig, ax = plt.subplots(figsize=(14, 8))

        # actual line
        if y_actual.notna().any():
            ax.plot(
                x_pos,
                y_actual.values,
                marker="o",
                linestyle="-",
                color="k",
                label="GDP",
                linewidth=2.0,
                markersize=5.5,
            )

        # predictions: equal thickness, distinct hues only; label as "GDP Nowcast"
        lw = 2.0
        cmap = plt.get_cmap("Blues")
        nP = len(preds)
        t_min, t_max = 0.45, 0.85  # distinct color shades, same thickness

        for i, p in enumerate(periods_sorted):
            if p not in preds:
                continue
            t = t_min if nP == 1 else (t_min + (t_max - t_min) * (i / (nP - 1)))
            color = cmap(t)
            label = f"GDP Nowcast ({self._rename_period_label(p)})"
            ax.plot(
                x_pos,
                preds[p].values,
                marker="o",
                linestyle="-",
                color=color,
                linewidth=lw,
                markersize=5.0,
                label=label,
            )

        # base axes styling (larger fonts)
        ax.set_title(title_final, fontsize=self.base_fs + 4)
        ax.set_ylabel("GDP", fontsize=self.base_fs)
        ax.set_xlabel("Quarter", fontsize=self.base_fs)
        ax.tick_params(axis="both", labelsize=self.base_fs)
        ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(quarters, fontsize=self.base_fs)

        # year axis below main ticks, moved closer to the plot
        year_positions, year_labels = [], []
        i = 0
        while i < len(years_str):
            y = years_str[i]
            j = i + 1
            while j < len(years_str) and years_str[j] == y:
                j += 1
            mid = (i + (j - 1)) / 2.0
            year_positions.append(mid)
            year_labels.append(y)
            i = j

        ax_year = ax.twiny()
        ax_year.set_xlim(ax.get_xlim())
        ax_year.set_xticks(year_positions)
        ax_year.set_xticklabels(year_labels, fontsize=self.base_fs)
        ax_year.xaxis.set_ticks_position("bottom")
        ax_year.xaxis.set_label_position("bottom")
        # moved closer (more negative -> closer to main axis)
        ax_year.spines["bottom"].set_position(("axes", self.year_axis_offset))
        ax_year.spines["top"].set_visible(False)
        ax_year.set_xlabel("", fontsize=self.base_fs)
        ax_year.tick_params(axis="x", pad=1, labelsize=self.base_fs)

        # legend with larger font
        ax.legend(fontsize=self.base_fs, frameon=True)

        fig.tight_layout()

        # save
        safe_name = filename
        if not safe_name:
            # derive a safe filename from title_final
            base = title_final.strip().lower()
            base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
            safe_name = base or "all_periods"
        out_path = self.output_dir / f"{safe_name}.{self.fmt}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=self.dpi, bbox_inches="tight")

        plt.close(fig)
        return fig

    @staticmethod
    def build_selected_count_frames(results_dictionaries, methods, periods):
        """
        For each period p, return a DataFrame with rows=methods and columns=quarters (DatetimeIndex),
        entries = 'Selected_Count' for that method-quarter.
        """
        out = {}
        for p in periods:
            series_by_method = {}
            for m in methods:
                d = results_dictionaries[m]
                df_p = d["varselect"]["selected_vars_quarters"]["selected"]["bic"][p]
                s = df_p.loc["Selected_Count"]                      # quarters in columns
                s = pd.to_numeric(s, errors="coerce")
                # normalize column index to datetime
                if isinstance(s.index, pd.PeriodIndex):
                    s.index = s.index.to_timestamp()
                else:
                    s.index = pd.to_datetime(s.index)
                series_by_method[m] = s
            # align across methods; sort columns chronologically
            df_counts = pd.DataFrame(series_by_method).T
            df_counts = df_counts.reindex(columns=sorted(df_counts.columns))
            out[p] = df_counts
        return out

    # ---------- NEW: single-period plot ----------
    def plot_selected_counts(
        self,
        counts_df: pd.DataFrame,
        *,
        title: str,
        filename: str | None = None,
    ):
        """
        Plot lines of 'Selected_Count' over time for each method (row) in counts_df.
        Columns must be quarterly timestamps (DatetimeIndex or PeriodIndex(Q)).
        Quarter labels on main x-axis; years on a secondary axis placed below.
        """
        base_fs = self.base_fs

        if counts_df.empty:
            fig, ax = plt.subplots(figsize=(12, 7))
            ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=base_fs+2)
            fig.tight_layout()
            out_path = self.output_dir / f"{(filename or 'selected_counts')}.{self.fmt}"
            fig.savefig(out_path, dpi=self.dpi, bbox_inches="tight")
            plt.close(fig)
            return

        cols = counts_df.columns
        if isinstance(cols, pd.PeriodIndex):
            cols = cols.to_timestamp()
        else:
            cols = pd.to_datetime(cols)
        cols = pd.DatetimeIndex(cols).sort_values()
        data = counts_df.reindex(columns=cols)

        x = np.arange(len(cols))
        quarters = [f"Q{d.quarter}" for d in cols]
        years_str = [str(d.year) for d in cols]

        fig, ax = plt.subplots(figsize=(14, 8))

        # lines (one per method)
        for method in data.index:
            y = data.loc[method].values
            ax.plot(x, y, marker="o", linestyle="-", linewidth=2.2, label=str(method))

        # labels & grid
        ax.set_title(title, fontsize=base_fs + 4)
        ax.set_ylabel("Number of Selected Indicators", fontsize=base_fs)
        ax.set_xlabel("Quarter", fontsize=base_fs)
        ax.set_xticks(x)
        ax.set_xticklabels(quarters, fontsize=base_fs)
        ax.tick_params(axis="both", labelsize=base_fs)
        ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.6, alpha=0.6)

        # secondary x-axis for years, positioned below
        year_positions, year_labels = [], []
        i = 0
        while i < len(years_str):
            y = years_str[i]
            j = i + 1
            while j < len(years_str) and years_str[j] == y:
                j += 1
            mid = (i + (j - 1)) / 2.0
            year_positions.append(mid)
            year_labels.append(y)
            i = j

        ax_year = ax.twiny()
        ax_year.set_xlim(ax.get_xlim())
        ax_year.set_xticks(year_positions)
        ax_year.set_xticklabels(year_labels, fontsize=base_fs)
        ax_year.xaxis.set_ticks_position("bottom")
        ax_year.xaxis.set_label_position("bottom")
        ax_year.spines["bottom"].set_position(("axes", self.year_axis_offset))
        ax_year.spines["top"].set_visible(False)
        ax_year.set_xlabel("", fontsize=base_fs)
        ax_year.tick_params(axis="x", pad=1, labelsize=base_fs)

        ax.legend(fontsize=base_fs, frameon=True)

        fig.tight_layout()
        safe_name = filename
        if not safe_name:
            base = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") or "selected_counts"
            safe_name = base
        out_path = self.output_dir / f"{safe_name}.{self.fmt}"
        fig.savefig(out_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)

    def plot_selected_counts_for_periods(
        self,
        results_dictionaries,
        methods,
        periods,
        *,
        title_prefix: str = "Selected Indicators Over Time — ",
        filename_prefix: str = "selected_indicators_over_time_",
    ):
        """
        Builds the per-period DataFrames and writes one plot per period using class settings.
        Returns the dict of DataFrames (period -> DataFrame).
        """
        frames = self.build_selected_count_frames(results_dictionaries, methods, periods)
        for p, df_counts in frames.items():
            title = f"{title_prefix}{str(p).upper()}"
            filename = f"{filename_prefix}{str(p).lower()}"
            self.plot_selected_counts(df_counts, title=title, filename=filename)
        return frames

    def plot_one_period_all_methods(
        self,
        *,
        results_dictionaries: dict,
        methods: list[str],
        weight: str,           # e.g. "periods_mseweight" or "periods_avg"
        period: str,           # e.g. "p1" / "p2" / "p3"
        filename: str | None = None,
        method_label_map: dict[str, str] | None = None,
        oos_start: int | None = None,
        oos_end: int | None = None,
    ):
        """
        Plot y_actual and the y_pred lines for ALL methods on ONE period.

        Title shows the horizon label (h0/h1/h2). The raw period label (p1/p2/p3) is not shown.
        Expects each method's data at:
          results_dictionaries[method]["model"][weight]["selected"]["bic"][period]
          -> a DataFrame indexed by Q-dates with 'y_actual' and/or 'y_pred' columns.
        """
        # --- gather data ---
        preds_by_method = {}
        y_actual = None
        all_idx = None

        for m in methods:
            try:
                df = results_dictionaries[m]["model"][weight]["selected"]["bic"][period]
            except KeyError:
                # silently skip missing combos
                continue

            if not isinstance(df, pd.DataFrame) or df.empty:
                continue

            # normalize index
            idx = self._to_dtindex(df)
            # grab actuals once (first available)
            if y_actual is None and "y_actual" in df.columns:
                y_actual = pd.Series(df["y_actual"].values, index=idx, name="y_actual")

            # predictions for this method
            if "y_pred" in df.columns:
                preds_by_method[m] = pd.Series(df["y_pred"].values, index=idx, name=m)

            # union index
            all_idx = idx if all_idx is None else all_idx.union(idx)

        if all_idx is None or (not preds_by_method and y_actual is None):
            # Title also uses horizon, not p1...
            horizon_label = self._rename_period_label(period).upper()
            return self._empty_figure(f"{horizon_label} — All Methods (no data)")

        all_idx = pd.DatetimeIndex(all_idx.sort_values())

        # reindex to union
        if y_actual is not None:
            y_actual = y_actual.reindex(all_idx)

        for m in list(preds_by_method.keys()):
            preds_by_method[m] = preds_by_method[m].reindex(all_idx)

        # infer OOS range if not provided
        if oos_start is None or oos_end is None:
            years = [int(d.year) for d in all_idx]
            if years:
                oos_start_inferred, oos_end_inferred = min(years), max(years)
            else:
                oos_start_inferred = oos_end_inferred = None
            oos_start = oos_start if oos_start is not None else oos_start_inferred
            oos_end = oos_end if oos_end is not None else oos_end_inferred

        # --- figure title (HORIZON ONLY) ---
        horizon_label = self._rename_period_label(period).upper()  # h0/h1/h2
        title_bits = [f"{horizon_label} — All Specifications"]
        if oos_start is not None and oos_end is not None:
            title_bits.append(f"OOS: {oos_start}–{oos_end}")
        title_final = " — ".join(title_bits)

        # --- x axis ticks (quarters) + year axis below ---
        x_pos = np.arange(len(all_idx))
        quarters = [f"Q{d.quarter}" for d in all_idx]
        years_str = [str(d.year) for d in all_idx]

        fig, ax = plt.subplots(figsize=(14, 8))

        # Actual line
        if y_actual is not None and y_actual.notna().any():
            ax.plot(
                x_pos, y_actual.values,
                marker="o", linestyle="-", color="k",
                label="GDP", linewidth=2.0, markersize=5.5,
            )

        # Method predictions: equal thickness, distinct hues
        lw = 2.2
        cm = plt.get_cmap("tab10") if len(preds_by_method) <= 10 else plt.get_cmap("viridis")
        for i, (m, s) in enumerate(preds_by_method.items()):
            label = method_label_map.get(m, m) if method_label_map else m
            ax.plot(
                x_pos, s.values,
                marker="o", linestyle="-", linewidth=lw, markersize=5.0,
                label=label, color=cm(i % cm.N)
            )

        # axes style
        ax.set_title(title_final, fontsize=self.base_fs + 4)
        ax.set_ylabel("QoQ GDP growth (%)", fontsize=self.base_fs)
        ax.set_xlabel("Quarter", fontsize=self.base_fs)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(quarters, fontsize=self.base_fs)
        ax.tick_params(axis="both", labelsize=self.base_fs)
        ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5, alpha=0.6)

        # years axis (below)
        year_positions, year_labels = [], []
        i = 0
        while i < len(years_str):
            y = years_str[i]
            j = i + 1
            while j < len(years_str) and years_str[j] == y:
                j += 1
            mid = (i + (j - 1)) / 2.0
            year_positions.append(mid)
            year_labels.append(y)
            i = j

        ax_year = ax.twiny()
        ax_year.set_xlim(ax.get_xlim())
        ax_year.set_xticks(year_positions)
        ax_year.set_xticklabels(year_labels, fontsize=self.base_fs)
        ax_year.xaxis.set_ticks_position("bottom")
        ax_year.xaxis.set_label_position("bottom")
        ax_year.spines["bottom"].set_position(("axes", self.year_axis_offset))
        ax_year.spines["top"].set_visible(False)
        ax_year.set_xlabel("", fontsize=self.base_fs)
        ax_year.tick_params(axis="x", pad=1, labelsize=self.base_fs)

        ax.legend(fontsize=self.base_fs, frameon=True)

        fig.tight_layout()

        # save
        if not filename:
            base = f"all_methods_{horizon_label.lower()}_{weight}".lower()
            base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
            filename = base or "all_methods_one_period"

        out_path = self.output_dir / f"{filename}.{self.fmt}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=self.dpi, bbox_inches="tight")

        plt.close(fig)
        return fig

    def plot_one_period_ar4(
        self,
        *,
        results_dictionary: dict,   # <-- single dictionary (not a dict of methods)
        weight: str,                # e.g. "periods_mseweight" or "periods_avg"
        period: str,                # e.g. "p1" / "p2" / "p3"
        filename: str | None = None,
        oos_start: int | None = None,
        oos_end: int | None = None,
    ):
        """
        Plot y_actual and the AR(4) predictions (y_pred_ar4) for ONE period using a single
        results_dictionary.

        Expects period data at:
        results_dictionary["model"][weight]["selected"]["bic"][period]
        -> DataFrame indexed by Q-dates with columns including 'y_actual' and 'y_pred_ar4'.
        """
        # --- fetch data for this period ---
        try:
            df = results_dictionary["model"][weight]["selected"]["bic"][period]
        except KeyError:
            horizon_label = self._rename_period_label(period).upper()
            return self._empty_figure(f"{horizon_label} — AR(4) (no data)")

        if not isinstance(df, pd.DataFrame) or df.empty:
            horizon_label = self._rename_period_label(period).upper()
            return self._empty_figure(f"{horizon_label} — AR(4) (no data)")

        # normalize index
        idx = self._to_dtindex(df)
        all_idx = pd.DatetimeIndex(idx.sort_values())

        # series
        y_actual = None
        if "y_actual" in df.columns:
            y_actual = pd.Series(df["y_actual"].values, index=idx, name="y_actual").reindex(all_idx)

        y_pred_ar4 = None
        if "y_pred_ar4" in df.columns:
            y_pred_ar4 = pd.Series(df["y_pred_ar4"].values, index=idx, name="y_pred_ar4").reindex(all_idx)

        if y_actual is None and y_pred_ar4 is None:
            horizon_label = self._rename_period_label(period).upper()
            return self._empty_figure(f"{horizon_label} — AR(4) (no data)")

        # infer OOS range if not provided
        if oos_start is None or oos_end is None:
            years = [int(d.year) for d in all_idx] if len(all_idx) else []
            if years:
                oos_start_inferred, oos_end_inferred = min(years), max(years)
            else:
                oos_start_inferred = oos_end_inferred = None
            oos_start = oos_start if oos_start is not None else oos_start_inferred
            oos_end = oos_end if oos_end is not None else oos_end_inferred

        # --- title (HORIZON ONLY) ---
        horizon_label = self._rename_period_label(period).upper()  # h0/h1/h2
        title_bits = [f"AR(4)"]
        if oos_start is not None and oos_end is not None:
            title_bits.append(f"OOS: {oos_start}–{oos_end}")
        title_final = " — ".join(title_bits)

        # --- x axis ticks (quarters) + year axis below ---
        x_pos = np.arange(len(all_idx))
        quarters = [f"Q{d.quarter}" for d in all_idx]
        years_str = [str(d.year) for d in all_idx]

        fig, ax = plt.subplots(figsize=(14, 8))

        # Actual line
        if y_actual is not None and y_actual.notna().any():
            ax.plot(
                x_pos, y_actual.values,
                marker="o", linestyle="-", color="k",
                label="GDP", linewidth=2.0, markersize=5.5,
            )

        # AR(4) predictions
        if y_pred_ar4 is not None and y_pred_ar4.notna().any():
            ax.plot(
                x_pos, y_pred_ar4.values,
                marker="o", linestyle="-",
                linewidth=2.2, markersize=5.0,
                label="AR(4) Benchmark",
            )

        # axes style
        ax.set_title(title_final, fontsize=self.base_fs + 4)
        ax.set_ylabel("QoQ GDP growth (%)", fontsize=self.base_fs)
        ax.set_xlabel("Quarter", fontsize=self.base_fs)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(quarters, fontsize=self.base_fs)
        ax.tick_params(axis="both", labelsize=self.base_fs)
        ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5, alpha=0.6)

        # years axis (below)
        year_positions, year_labels = [], []
        i = 0
        while i < len(years_str):
            y = years_str[i]
            j = i + 1
            while j < len(years_str) and years_str[j] == y:
                j += 1
            mid = (i + (j - 1)) / 2.0
            year_positions.append(mid)
            year_labels.append(y)
            i = j

        ax_year = ax.twiny()
        ax_year.set_xlim(ax.get_xlim())
        ax_year.set_xticks(year_positions)
        ax_year.set_xticklabels(year_labels, fontsize=self.base_fs)
        ax_year.xaxis.set_ticks_position("bottom")
        ax_year.xaxis.set_label_position("bottom")
        ax_year.spines["bottom"].set_position(("axes", self.year_axis_offset))
        ax_year.spines["top"].set_visible(False)
        ax_year.set_xlabel("", fontsize=self.base_fs)
        ax_year.tick_params(axis="x", pad=1, labelsize=self.base_fs)

        # legend
        ax.legend(fontsize=self.base_fs, frameon=True)

        fig.tight_layout()

        # save
        if not filename:
            base = f"ar4_{horizon_label.lower()}_{weight}".lower()
            base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
            filename = base or "ar4_one_period"

        out_path = self.output_dir / f"{filename}.{self.fmt}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=self.dpi, bbox_inches="tight")

        plt.close(fig)
        return fig
