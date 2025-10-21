import math
from collections import Counter, defaultdict
from datetime import datetime, date
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.dates import DayLocator, DateFormatter

from data.datautils.transform import Transform
class DataOutputMixin:

    def get_release_calendar_plot(
        self,
        y_var: str,
        ax: plt.Axes | None = None,
        include_quarterly: bool = True,
        figsize: tuple[float, float] = (18, 5),   # wide by default
        mapping_periods: dict | None = None
    ):
        """
        Q2 release calendar (stacked daily counts) with:
        - only series where meta.filtered == False
        - PERIOD TOTALS computed via self._match_date_to_period(...) for exact
          consistency with get_release_periods()
        - vertical dashed mapping_periods endpoints and p-labels
        - total releases per period shown under each label
        - numbers on top of each daily bar
        - red vertical line at the Q2 release of `y_var`
        - x ticks every 10 days, labels without the year
        Returns (fig, ax).
        """
        # Make sure _match_date_to_period uses the same mapping
        self._mapping_periods = mapping_periods if mapping_periods is not None else getattr(self, "_mapping_periods", None)
        
        # ---------- helpers ----------
        def _to_dt(md: tuple[int, int], year: int) -> datetime:
            m, d = md
            return datetime(year, m, d)

        def _series_is_included(series_name: str) -> bool:
            meta = self.meta.get(series_name)
            return meta is not None and not getattr(meta, "filtered", False)

        def _norm_to_base_year(dt_like, year: int) -> datetime:
            """Normalize any timestamp to `year` (keep month & day, 00:00 time)."""
            ts = pd.Timestamp(dt_like)
            return datetime(year, ts.month, ts.day)

        def _month_end(y: int, m: int) -> datetime:
            return (pd.Timestamp(datetime(y, m, 1)) + pd.offsets.MonthEnd(0)).to_pydatetime()

        # ---------- choose base_year (prefer y_var's latest complete Q2; if y_var is 'D', use current year) ----------
        base_year = None
        y_release_dt = None
        if y_var in self.meta and _series_is_included(y_var):
            try:
                freq = self.meta[y_var].freq
                if freq == "D":
                    base_year = datetime.now().year
                    y_release_dt = _month_end(base_year, 6)
                else:
                    y_df = self.series_release_values_dataframes[y_var][f"{y_var}_rd"]
                    probe_df = Transform.skip_sampling_to_q(y_df, freq) if freq == "ME" else y_df
                    y_valid_q, _ = self._find_latest_complete_q2(probe_df, y_var, freq)
                    if y_valid_q is not None:
                        base_year = int(y_valid_q.year)
                        if freq == "QE":
                            y_release_dt = pd.Timestamp(y_df.loc[y_valid_q]).normalize().to_pydatetime()
                        else:  # ME → prefer m3, then m2, then m1
                            row = probe_df.loc[y_valid_q]
                            for m in ("m3", "m2", "m1"):
                                col = f"{y_var}_rd_{m}"
                                if pd.notnull(row[col]):
                                    y_release_dt = pd.Timestamp(row[col]).normalize().to_pydatetime()
                                    break
            except Exception:
                pass

        if base_year is None:
            # fallback: first available unfiltered series
            for series, meta in self.meta.items():
                if not _series_is_included(series):
                    continue
                try:
                    freq = meta.freq
                    if freq == "D":
                        base_year = datetime.now().year
                        break
                    s_df = self.series_release_values_dataframes[series][f"{series}_rd"]
                    probe_df = Transform.skip_sampling_to_q(s_df, freq) if freq == "ME" else s_df
                    valid_q, _ = self._find_latest_complete_q2(probe_df, series, freq)
                    if valid_q is not None:
                        base_year = int(valid_q.year)
                        break
                except Exception:
                    continue
        if base_year is None:
            base_year = datetime.now().year  # last resort

        # ---------- collect DAILY counts & PERIOD totals (via _match_date_to_period) ----------
        counts_by_day = defaultdict(lambda: {"m1": 0, "m2": 0, "m3": 0, "q": 0})
        period_totals = defaultdict(int)  # p1..p6 -> count

        def _count_release(dt_like, bucket_key: str):
            """Count one release both by normalized day and by period label (using _match_date_to_period)."""
            day_norm = _norm_to_base_year(dt_like, base_year)
            counts_by_day[day_norm][bucket_key] += 1
            p_label = self._match_date_to_period(day_norm, base_year)
            if self._period_gate_ok(p_label) and self._is_p_label(p_label):
                period_totals[p_label] += 1

        for series, meta in self.meta.items():
            if not _series_is_included(series):
                continue

            freq = meta.freq
            try:
                if freq == "ME":
                    blocked = Transform.skip_sampling_to_q(
                        self.series_release_values_dataframes[series][f"{series}_rd"], freq
                    )
                    valid_q, _ = self._find_latest_complete_q2(blocked, series, freq)
                    if valid_q is None:
                        continue
                    row = blocked.loc[valid_q]
                    for m in ("m1", "m2", "m3"):
                        col = f"{series}_rd_{m}"
                        dt = row[col]
                        if pd.notnull(dt):
                            _count_release(dt, m)

                elif freq == "QE" and include_quarterly:
                    s_df = self.series_release_values_dataframes[series][f"{series}_rd"]
                    valid_q, _ = self._find_latest_complete_q2(s_df, series, freq)
                    if valid_q is None:
                        continue
                    dt = s_df.loc[valid_q]
                    if pd.notnull(dt):
                        _count_release(dt, "q")

                elif freq == "D":
                    # Assume Q2 month-ends (Apr, May, Jun) for the chosen base_year
                    m_dates = [_month_end(base_year, 4), _month_end(base_year, 5), _month_end(base_year, 6)]
                    for m_key, dt in zip(("m1", "m2", "m3"), m_dates):
                        _count_release(dt, m_key)

            except Exception:
                continue

        # ---------- handle empty ----------
        if not counts_by_day:
            if ax is None:
                fig, ax = plt.subplots(figsize=figsize)
            ax.set_title("Q2 release calendar – no releases found")
            return ax.figure, ax

        # ---------- prepare vectors ----------
        dates = sorted(counts_by_day.keys())
        y_m1 = np.array([counts_by_day[d]["m1"] for d in dates])
        y_m2 = np.array([counts_by_day[d]["m2"] for d in dates])
        y_m3 = np.array([counts_by_day[d]["m3"] for d in dates])
        y_q  = np.array([counts_by_day[d]["q"]  for d in dates]) if include_quarterly else np.zeros_like(y_m1)
        totals = y_m1 + y_m2 + y_m3 + y_q
        max_total = int(totals.max()) if len(totals) else 1

        # ---------- figure/axes ----------
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure

        # one bar per day, stacked
        width = 0.8  # in "days"
        ax.bar(dates, y_m2, width=width, label="Release Second Month")
        ax.bar(dates, y_m3, width=width, bottom=y_m2, label="Release Third Month")
        ax.bar(dates, y_m1, width=width, bottom=y_m2 + y_m3, label="Release First Month")
        if include_quarterly:
            ax.bar(dates, y_q, width=width, bottom=y_m2 + y_m3 + y_m1, label="Quarterly Releases")

        # ---------- formatting ----------
        ax.xaxis.set_major_locator(DayLocator(interval=10))   # every 10 days
        ax.xaxis.set_major_formatter(DateFormatter("%d.%m"))  # drop the year
        xpad = pd.Timedelta(days=7)
        ax.set_xlim(dates[0] - xpad, dates[-1] + xpad)
        ax.set_ylim(0, max(1, max_total) * 1.20)
        ax.set_ylabel("Number of releases")
        ax.set_title("Q2 release calendar – daily counts by category")
        ax.grid(axis="y", linewidth=0.5, alpha=0.5)
        ax.tick_params(axis="x", labelsize=9)
        ax.tick_params(axis="y", labelsize=9)

        # Legend: small font, stacked vertically on the right; extra right margin
        fig.subplots_adjust(right=0.86)
        ax.legend(
            loc="upper left",
            bbox_to_anchor=(1.005, 1),
            borderaxespad=0,
            frameon=False,
            fontsize=8,
            ncol=1,
        )

        # ---------- numbers on top of each total bar ----------
        y_offset = max(1, max_total) * 0.02
        for d, tot in zip(dates, totals):
            if tot > 0:
                ax.text(d, tot + y_offset, f"{int(tot)}", ha="center", va="bottom", fontsize=8, clip_on=True)

        # ---------- vertical lines and p-labels (+ totals per period via _match_date_to_period) ----------
        left_num, right_num = ax.get_xlim()
        left_dt = mdates.num2date(left_num).replace(tzinfo=None)
        right_dt = mdates.num2date(right_num).replace(tzinfo=None)
        y_top = ax.get_ylim()[1]

        for p_label in sorted(mapping_periods.keys(), key=self._p_key):
            start_md, end_md = mapping_periods[p_label]
            s_dt, e_dt = _to_dt(start_md, base_year), _to_dt(end_md, base_year)

            # dashed endpoint lines
            ax.axvline(s_dt, linestyle="--", linewidth=1, color="gray", alpha=0.6)
            ax.axvline(e_dt, linestyle="--", linewidth=1, color="gray", alpha=0.6)

            # use period_totals computed via _match_date_to_period
            p_total = int(period_totals.get(p_label, 0))

            # label & count (extra spacing)
            mid = s_dt + (e_dt - s_dt) / 2
            if left_dt <= mid <= right_dt:
                ax.text(mid, y_top * 0.98, p_label, ha="center", va="top", fontsize=10)
                ax.text(mid, y_top * 0.92, f"+{p_total}", ha="center", va="top", fontsize=10)

        # ---------- red vertical line for y_var release ----------
        if y_release_dt is not None:
            y_norm = _norm_to_base_year(y_release_dt, base_year)
            ax.axvline(y_norm, color="red", linewidth=2, alpha=0.8)
            ax.text(y_norm, y_top * 0.88, f"{y_var} release", rotation=90,
                    ha="right", va="top", fontsize=9, color="red")

        fig.tight_layout()
        return fig, ax

    def get_release_calendar_plot_clean(
        self,
        y_var: str,
        ax: plt.Axes | None = None,
        include_quarterly: bool = True,
        figsize: tuple[float, float] = (18, 5),
        mapping_periods: dict | None = None,
        *,
        color_m1: str | None = None,
        color_m2: str | None = None,
        color_m3: str | None = None,
        color_q: str | None = None,
    ):
        """
        Q2 release calendar (stacked daily counts), like get_release_calendar_plot but:
        - no per-bar count labels
        - no y_var name printed at its release (red line remains)
        - manual color control for monthly buckets (and quarterly, optional)

        Parameters
        ----------
        y_var : str
            Target series used to determine the base year and to draw the red release line.
        ax : plt.Axes | None
            Matplotlib axes to draw on. If None, a new fig/ax is created.
        include_quarterly : bool
            Whether to include quarterly series as a stacked layer.
        figsize : (float, float)
            Figure size when ax is None.
        mapping_periods : dict | None
            Dict like {'p1': ((m, d), (m, d)), ..., 'p6': ((m, d), (m, d))}.
            Used to draw vertical dashed lines and period labels/totals.
        color_m1, color_m2, color_m3 : str | None
            Colors for First/Second/Third month releases. If None, matplotlib defaults are used.
        color_q : str | None
            Color for quarterly releases (used only if include_quarterly=True).

        Returns
        -------
        (fig, ax)
        """
        # Reuse the same mapping used by _match_date_to_period
        self._mapping_periods = mapping_periods if mapping_periods is not None else getattr(self, "_mapping_periods", None)

        # ---------- helpers ----------
        def _to_dt(md: tuple[int, int], year: int) -> datetime:
            m, d = md
            return datetime(year, m, d)

        def _series_is_included(series_name: str) -> bool:
            meta = self.meta.get(series_name)
            return meta is not None and not getattr(meta, "filtered", False)

        def _norm_to_base_year(dt_like, year: int) -> datetime:
            ts = pd.Timestamp(dt_like)
            return datetime(year, ts.month, ts.day)

        def _month_end(y: int, m: int) -> datetime:
            return (pd.Timestamp(datetime(y, m, 1)) + pd.offsets.MonthEnd(0)).to_pydatetime()

        # ---------- choose base_year & y_release_dt (same logic as original) ----------
        base_year = None
        y_release_dt = None
        if y_var in self.meta and _series_is_included(y_var):
            try:
                freq = self.meta[y_var].freq
                if freq == "D":
                    base_year = datetime.now().year
                    y_release_dt = _month_end(base_year, 6)
                else:
                    y_df = self.series_release_values_dataframes[y_var][f"{y_var}_rd"]
                    probe_df = Transform.skip_sampling_to_q(y_df, freq) if freq == "ME" else y_df
                    y_valid_q, _ = self._find_latest_complete_q2(probe_df, y_var, freq)
                    if y_valid_q is not None:
                        base_year = int(y_valid_q.year)
                        if freq == "QE":
                            y_release_dt = pd.Timestamp(y_df.loc[y_valid_q]).normalize().to_pydatetime()
                        else:  # ME: prefer m3, then m2, then m1
                            row = probe_df.loc[y_valid_q]
                            for m in ("m3", "m2", "m1"):
                                col = f"{y_var}_rd_{m}"
                                if pd.notnull(row[col]):
                                    y_release_dt = pd.Timestamp(row[col]).normalize().to_pydatetime()
                                    break
            except Exception:
                pass

        if base_year is None:
            for series, meta in self.meta.items():
                if not _series_is_included(series):
                    continue
                try:
                    freq = meta.freq
                    if freq == "D":
                        base_year = datetime.now().year
                        break
                    s_df = self.series_release_values_dataframes[series][f"{series}_rd"]
                    probe_df = Transform.skip_sampling_to_q(s_df, freq) if freq == "ME" else s_df
                    valid_q, _ = self._find_latest_complete_q2(probe_df, series, freq)
                    if valid_q is not None:
                        base_year = int(valid_q.year)
                        break
                except Exception:
                    continue
        if base_year is None:
            base_year = datetime.now().year

        # ---------- collect DAILY counts & PERIOD totals ----------
        from collections import defaultdict
        counts_by_day = defaultdict(lambda: {"m1": 0, "m2": 0, "m3": 0, "q": 0})
        period_totals = defaultdict(int)

        def _count_release(dt_like, bucket_key: str):
            day_norm = _norm_to_base_year(dt_like, base_year)
            counts_by_day[day_norm][bucket_key] += 1
            p_label = self._match_date_to_period(day_norm, base_year)
            if self._period_gate_ok(p_label) and self._is_p_label(p_label):
                period_totals[p_label] += 1

        for series, meta in self.meta.items():
            if not _series_is_included(series):
                continue
            freq = meta.freq
            try:
                if freq == "ME":
                    blocked = Transform.skip_sampling_to_q(
                        self.series_release_values_dataframes[series][f"{series}_rd"], freq
                    )
                    valid_q, _ = self._find_latest_complete_q2(blocked, series, freq)
                    if valid_q is None:
                        continue
                    row = blocked.loc[valid_q]
                    for m in ("m1", "m2", "m3"):
                        col = f"{series}_rd_{m}"
                        dt = row[col]
                        if pd.notnull(dt):
                            _count_release(dt, m)

                elif freq == "QE" and include_quarterly:
                    s_df = self.series_release_values_dataframes[series][f"{series}_rd"]
                    valid_q, _ = self._find_latest_complete_q2(s_df, series, freq)
                    if valid_q is None:
                        continue
                    dt = s_df.loc[valid_q]
                    if pd.notnull(dt):
                        _count_release(dt, "q")

                elif freq == "D":
                    m_dates = [_month_end(base_year, 4), _month_end(base_year, 5), _month_end(base_year, 6)]
                    for m_key, dt in zip(("m1", "m2", "m3"), m_dates):
                        _count_release(dt, m_key)

            except Exception:
                continue

        # ---------- empty guard ----------
        if not counts_by_day:
            if ax is None:
                fig, ax = plt.subplots(figsize=figsize)
            ax.set_title("Q2 release calendar – no releases found")
            return ax.figure, ax

        # ---------- vectors ----------
        dates = sorted(counts_by_day.keys())
        y_m1 = np.array([counts_by_day[d]["m1"] for d in dates])
        y_m2 = np.array([counts_by_day[d]["m2"] for d in dates])
        y_m3 = np.array([counts_by_day[d]["m3"] for d in dates])
        y_q  = np.array([counts_by_day[d]["q"] for d in dates]) if include_quarterly else np.zeros_like(y_m1)
        totals = y_m1 + y_m2 + y_m3 + y_q
        max_total = int(totals.max()) if len(totals) else 1

        # ---------- figure/axes ----------
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure

        width = 0.8  # in "days"
        # Order: stack m2, m3, then m1 on top (to match your original)
        ax.bar(dates, y_m2, width=width, label="Release Second Month", color=color_m2)
        ax.bar(dates, y_m3, width=width, bottom=y_m2, label="Release Third Month", color=color_m3)
        ax.bar(dates, y_m1, width=width, bottom=y_m2 + y_m3, label="Release First Month", color=color_m1)
        if include_quarterly:
            ax.bar(dates, y_q, width=width, bottom=y_m2 + y_m3 + y_m1, label="Quarterly Releases", color=color_q)

        # ---------- formatting ----------
        ax.xaxis.set_major_locator(DayLocator(interval=10))
        ax.xaxis.set_major_formatter(DateFormatter("%d.%m"))
        xpad = pd.Timedelta(days=7)
        ax.set_xlim(dates[0] - xpad, dates[-1] + xpad)
        ax.set_ylim(0, max(1, max_total) * 1.20)
        ax.set_ylabel("Number of releases")
        ax.set_title("Q2 release calendar – daily counts by category")
        ax.grid(axis="y", linewidth=0.5, alpha=0.5)
        ax.tick_params(axis="x", labelsize=9)
        ax.tick_params(axis="y", labelsize=9)

        fig.subplots_adjust(right=0.86)
        ax.legend(
            loc="upper left",
            bbox_to_anchor=(1.005, 1),
            borderaxespad=0,
            frameon=False,
            fontsize=8,
            ncol=1,
        )

        # ---------- vertical lines and p-labels (+ totals per period) ----------
        left_num, right_num = ax.get_xlim()
        left_dt = mdates.num2date(left_num).replace(tzinfo=None)
        right_dt = mdates.num2date(right_num).replace(tzinfo=None)
        y_top = ax.get_ylim()[1]

        for p_label in sorted(mapping_periods.keys(), key=self._p_key):
            start_md, end_md = mapping_periods[p_label]
            s_dt, e_dt = _to_dt(start_md, base_year), _to_dt(end_md, base_year)
            ax.axvline(s_dt, linestyle="--", linewidth=1, color="gray", alpha=0.6)
            ax.axvline(e_dt, linestyle="--", linewidth=1, color="gray", alpha=0.6)

            p_total = int(period_totals.get(p_label, 0))
            mid = s_dt + (e_dt - s_dt) / 2
            if left_dt <= mid <= right_dt:
                ax.text(mid, y_top * 0.98, p_label, ha="center", va="top", fontsize=10)
                ax.text(mid, y_top * 0.92, f"+{p_total}", ha="center", va="top", fontsize=10)

        # ---------- red vertical line for y_var release (no label) ----------
        if y_release_dt is not None:
            y_norm = _norm_to_base_year(y_release_dt, base_year)
            ax.axvline(y_norm, color="red", linewidth=2, alpha=0.8)

        fig.tight_layout()
        return fig, ax
