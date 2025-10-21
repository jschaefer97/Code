from datetime import datetime
import pandas as pd
from loguru import logger
from collections import defaultdict

from data.datautils.transform import Transform

class RaggedEdgeSimulMixin:

    def _is_p_label(self, p) -> bool:
        return isinstance(p, str) and p.startswith("p") and p[1:].isdigit()

    def _p_key(self, p: str) -> int:
        return int(p[1:]) if self._is_p_label(p) else 10**9

    def _period_gate_ok(self, p) -> bool:
        """Mirror the gate used in get_release_periods_dict: truthy and not outsideQ/Error."""
        return bool(p) and p not in ("outsideQ", "Error")

    def get_release_periods(self, mapping_periods: dict | None = None):
        """
        Compute and write release-period labels into meta for each series.

        Parameters
        ----------
        mapping_periods : dict or None
        """
        # store mapping on the instance so helpers can use it
        self._mapping_periods = mapping_periods if mapping_periods is not None else getattr(self, "_mapping_periods", None)

        for series in self.meta.keys():

            meta = self.meta[series]
            series_freq = meta.freq
            logger.info(f"{self.name}: ▶ Processing series: {series} with frequency {series_freq}")

            series_release_values_df = self.series_release_values_dataframes[series]

            if series_freq == "ME":

                series_release_df = series_release_values_df[f"{series}_rd"]
                blocked_release_df = Transform.skip_sampling_to_q(series_release_df, series_freq)

                valid_q, lag_q = self._find_latest_complete_q2(blocked_release_df, series, series_freq)

                if valid_q is None:
                    logger.warning(f"{self.name}: No complete Q2 release found. Skipping...")
                    meta.m1_period = meta.m2_period = meta.m3_period = "Error"
                    meta.m1_lag1_period = meta.m2_lag1_period = meta.m3_lag1_period = "Error"
                    continue

                logger.info(f"{self.name}: Latest complete Q2 found at index: {valid_q}")
                base_year = valid_q.year
                row = blocked_release_df.loc[valid_q]

                # --- grouped log for m1/m2/m3 (current) ---
                release_info = []
                for m in ["m1", "m2", "m3"]:
                    col = f"{series}_rd_{m}"
                    date = row[col]
                    if pd.isnull(date):
                        setattr(meta, f"{m}_period", "Error")
                        release_info.append(f"{m}=missing(Error)")
                    else:
                        period = self._match_date_to_period(date, base_year)
                        setattr(meta, f"{m}_period", period)
                        release_info.append(f"{m}={date.date()}({period})")
                logger.info(f"{self.name}: {series} | current blocks → " + ", ".join(release_info) + " – matched via period windows")

                # --- grouped log for m1/m2/m3 (lag1) ---
                if lag_q is not None:
                    lag_row = blocked_release_df.loc[lag_q]
                    lag_release_info = []
                    for m in ["m1", "m2", "m3"]:
                        col = f"{series}_rd_{m}"
                        lag_date = lag_row[col]
                        if pd.isnull(lag_date):
                            setattr(meta, f"{m}_lag1_period", "Error")
                            lag_release_info.append(f"{m}_lag1=missing(Error)")
                        else:
                            period = self._match_date_to_period(lag_date, base_year)
                            setattr(meta, f"{m}_lag1_period", period)
                            lag_release_info.append(f"{m}_lag1={lag_date.date()}({period})")
                    logger.info(f"{self.name}: {series} | lag1 blocks → " + ", ".join(lag_release_info) + " – matched via period windows")
                else:
                    logger.warning(f"{self.name}: No lag available. Using hardcoded placeholders.")
                    meta.m1_lag1_period = meta.m2_lag1_period = meta.m3_lag1_period = "Error"

            elif series_freq == "QE":
                series_release_df = series_release_values_df[f"{series}_rd"]

                valid_q, lag_q = self._find_latest_complete_q2(series_release_df, series, series_freq)

                if valid_q is None:
                    logger.warning(f"{self.name}: No valid Q2 release with lag found.")
                    meta.q_period = meta.q_lag1_period = "Error"
                    continue

                logger.info(f"{self.name}: Q2 release with lag found at index: {valid_q}")
                base_year = valid_q.year
                release_date = series_release_df.loc[valid_q]
                lag_date = series_release_df.loc[lag_q]

                meta.q_period = self._match_date_to_period(release_date, base_year)
                if pd.isnull(lag_date):
                    meta.q_lag1_period = "Error"
                    lag_part = "q_lag1=missing(Error)"
                else:
                    meta.q_lag1_period = self._match_date_to_period(lag_date, base_year)
                    lag_part = f"q_lag1={lag_date.date()}({meta.q_lag1_period})"

                logger.info(
                    f"{self.name}: {series} | q={release_date.date()}({meta.q_period}), {lag_part} – matched via period windows"
                )

            elif series_freq == "D":
                # Daily series: assume releases at month-end of the first, second, and third month of the quarter.
                # For Q2: Apr/May/Jun. Lag1 uses month-ends of previous quarter (Q1: Jan/Feb/Mar).
                base_year = datetime.now().year

                def month_end(y: int, m: int) -> datetime:
                    return (pd.Timestamp(datetime(y, m, 1)) + pd.offsets.MonthEnd(0)).to_pydatetime()

                # Assumed month-end releases for Q2
                m_dates = [month_end(base_year, 4), month_end(base_year, 5), month_end(base_year, 6)]
                release_info = []
                for m, dt in zip(["m1", "m2", "m3"], m_dates):
                    period = self._match_date_to_period(dt, base_year)
                    setattr(meta, f"{m}_period", period)
                    release_info.append(f"{m}={dt.date()}({period})")
                logger.info(f"{self.name}: {series} | (D) current blocks → " + ", ".join(release_info) + " – assumed month-end mapping")

                # Lag1 = Q1 month-ends
                lag_dates = [month_end(base_year, 1), month_end(base_year, 2), month_end(base_year, 3)]
                lag_release_info = []
                for m, dt in zip(["m1", "m2", "m3"], lag_dates):
                    period = self._match_date_to_period(dt, base_year)
                    setattr(meta, f"{m}_lag1_period", period)
                    lag_release_info.append(f"{m}_lag1={dt.date()}({period})")
                logger.info(f"{self.name}: {series} | (D) lag1 blocks → " + ", ".join(lag_release_info) + " – assumed month-end mapping")

            else:
                logger.warning(f"{self.name}: Unsupported frequency '{series_freq}'")

        self._update_meta_df()

    def _match_date_to_period(self, date: datetime, base_year: int) -> str:
        # Use instance mapping if present; fall back to imported mapping.
        mapping = self._mapping_periods

        for pname, ((start_month, start_day), (end_month, end_day)) in mapping.items():
            start_date = datetime(base_year, start_month, start_day)
            end_date = datetime(base_year, end_month, end_day)
            if start_date <= date <= end_date:
                return pname

        if date < datetime(base_year, 3, 23):
            return "p1"
        elif date > datetime(base_year, 7, 29):
            return "outsideQ"
        else:
            return "outsideQ"

    def _find_latest_complete_q2(self, df, series, series_freq):
        """
        Finds the latest Q2 (June-ending) observation from the end of `df` that:
        - For "ME": has non-null m1, m2, m3 release dates.
        - For "QE": has a non-null release and a non-null lag.

        Returns: (valid_index, lag_index) or (None, None)
        """
        for i in reversed(range(1, len(df))):  # ensure lag is available
            idx = df.index[i]
            if idx.month != 6:
                continue

            if series_freq == "ME":
                row = df.iloc[i]
                if all(pd.notnull([
                    row.get(f"{series}_rd_m1"),
                    row.get(f"{series}_rd_m2"),
                    row.get(f"{series}_rd_m3")
                ])):
                    return idx, df.index[i - 1]

            elif series_freq == "QE":
                if pd.notnull(df.iloc[i]) and pd.notnull(df.iloc[i - 1]):
                    return idx, df.index[i - 1]

        return None, None

    def get_release_periods_dict(self):
        """
        Build cumulative dictionary mapping release periods (p1, p2, ..., pN) to variable names,
        with a strict gate:
        - ME/D series: include *only* series_m1/m2/m3, and only if m1_period is valid.
        - QE series:   include *only* the series (no lag), and only if q_period is valid.

        Lags are *not* included at all.
        'outsideQ' and 'Error' are excluded; inclusion is cumulative across periods.
        """
        period_blocks = defaultdict(list)

        for series, meta in self.meta.items():
            if meta.filtered == False:
                freq = getattr(meta, "freq", None)

                if freq in ("ME", "D"):
                    # Gate entire series on m1 being released
                    m1_period = getattr(meta, "m1_period", None)
                    if not self._period_gate_ok(m1_period):
                        continue

                    # Current blocks only (no lags)
                    for m in ["m1", "m2", "m3"]:
                        period = getattr(meta, f"{m}_period", None)
                        if self._period_gate_ok(period):
                            period_blocks[period].append(f"{series}_{m}")

                elif freq == "QE":
                    # Gate on q being released; no lags included
                    q_period = getattr(meta, "q_period", None)
                    if not self._period_gate_ok(q_period):
                        continue

                    period_blocks[q_period].append(series)

                else:
                    logger.warning(f"{self.name}: Unknown frequency '{freq}' for series '{series}'")

        # Sort periods numerically for cumulative build
        sorted_periods = sorted(period_blocks.keys(), key=self._p_key)

        # Cumulative inclusion: once a var is available, it remains available in later periods
        release_periods_dict = {}
        cumulative_vars = set()

        for period in sorted_periods:
            cumulative_vars.update(period_blocks[period])
            release_periods_dict[period] = sorted(cumulative_vars)

        return release_periods_dict
    
    def get_release_periods_dict_nc(self):
        """
        Build a *non-cumulative* dictionary that maps period labels (p1, p2, ..., pN)
        to the *latest available* block per series at that period.

        Differences vs. `get_release_periods_dict`:
        - For ME/D series: only one of {series_m1, series_m2, series_m3} will appear
        for a given period, namely the latest block that has been released on or
        before that period. Earlier blocks are *replaced* by later ones.
        - For QE series: the series (no lag) appears starting at its q_period.
        - Lags are *not* included at all.
        - 'outsideQ' and 'Error' are excluded.
        - Only series with meta.filtered == False are considered.

        Returns
        -------
        dict
            {
            "p1": [<vars with latest release up to p1>],
            "p2": [...],
            ...
            }
        """
        # Helper to validate a 'pN' label
        def _valid_p_label(p) -> bool:
            return self._period_gate_ok(p) and self._is_p_label(p)

        # 1) Collect all release events per series as (period_label, varname) and
        #    gather the universe of period labels we need to consider.
        per_series_releases = {}  # series -> List[(p_label, varname)]
        all_periods_set = set()

        for series, meta in self.meta.items():
            if getattr(meta, "filtered", None) is not False:
                continue

            freq = getattr(meta, "freq", None)
            releases = []

            if freq in ("ME", "D"):
                # Add m1/m2/m3 current blocks if they have valid p-labels
                for block in ("m1", "m2", "m3"):
                    p_label = getattr(meta, f"{block}_period", None)
                    if _valid_p_label(p_label):
                        varname = f"{series}_{block}"
                        releases.append((p_label, varname))
                        all_periods_set.add(p_label)

            elif freq == "QE":
                # Add only the current quarterly block if it has a valid p-label
                p_label = getattr(meta, "q_period", None)
                if _valid_p_label(p_label):
                    releases.append((p_label, series))
                    all_periods_set.add(p_label)

            else:
                logger.warning(f"{self.name}: Unknown frequency '{freq}' for series '{series}'")

            if releases:
                per_series_releases[series] = releases

        # Early exit if nothing to do
        if not all_periods_set:
            return {}

        # 2) Sort periods numerically and build an index map for ordering/comparisons.
        all_periods = sorted(all_periods_set, key=self._p_key)
        p_index = {p: i for i, p in enumerate(all_periods)}

        # 3) For each series, sort its releases by period and then "carry forward"
        #    the *latest* block up to each period. Populate the per-period dictionary
        #    with only the latest block per series (non-cumulative replacement).
        release_periods_dict = {p: [] for p in all_periods}

        for series, releases in per_series_releases.items():
            # Convert to (idx, varname) sorted by idx
            rel_sorted = sorted(((p_index[p], varname) for p, varname in releases),
                                key=lambda x: x[0])

            latest_var = None
            j = 0
            # Walk through the global period timeline, carrying the latest block
            for i, p in enumerate(all_periods):
                while j < len(rel_sorted) and rel_sorted[j][0] <= i:
                    latest_var = rel_sorted[j][1]
                    j += 1
                if latest_var is not None:
                    release_periods_dict[p].append(latest_var)

        # 4) Sort variable lists within each period for stability and return.
        for p in release_periods_dict:
            release_periods_dict[p] = sorted(release_periods_dict[p])

        return release_periods_dict


    def get_release_latest_block_dict(self):
        """
        Return:
            {
            series_name: {
                'p1': 'm1_period'|'m2_period'|'m3_period'|'q_period'|'m3_period_lag1'|'q_period_lag1',
                ...,
                'pN': ...
            },
            ...
            }

        Periods are collected from meta (no mapping_periods dependency).
        Only series with meta.filtered == False are included.

        Defaults:
        - ME/D freq → 'm3_period_lag1' where no block is available.
        - QE freq   → 'q_period_lag1' where no block is available.
        """
        # collect all periods from meta
        all_periods_set = set()
        for _series, meta in self.meta.items():
            for attr in ("m1_period", "m2_period", "m3_period", "q_period"):
                p = getattr(meta, attr, None)
                # Require both the generic gate AND a proper 'pN' label
                if self._period_gate_ok(p) and self._is_p_label(p):
                    all_periods_set.add(p)

        if not all_periods_set:
            return {}

        all_periods = sorted(all_periods_set, key=self._p_key)
        p_index = {p: i for i, p in enumerate(all_periods)}

        # build timelines per series
        release_latest_block_dict = {}

        for series, meta in self.meta.items():
            if getattr(meta, "filtered", None) is not False:
                # mirror your gating in get_release_periods_dict
                continue

            freq = getattr(meta, "freq", None)

            # Default fill depends on frequency
            default_fill = "q_period_lag1" if freq == "QE" else "m3_period_lag1" 
            series_timeline = {p: default_fill for p in all_periods}

            if freq in ("ME", "D"):
                # Gather available monthly blocks (ordered by when they become available)
                blocks = []
                for block in ("m1", "m2", "m3"):
                    p = getattr(meta, f"{block}_period", None)
                    if self._period_gate_ok(p) and self._is_p_label(p):
                        blocks.append((p_index[p], f"{block}_period"))

                blocks.sort(key=lambda x: x[0])

                latest = None
                j = 0
                for i, p in enumerate(all_periods):
                    while j < len(blocks) and blocks[j][0] <= i:
                        latest = blocks[j][1]
                        j += 1
                    # fallback uses frequency-appropriate default
                    series_timeline[p] = latest if latest is not None else default_fill

            elif freq == "QE":
                p = getattr(meta, "q_period", None)
                if self._period_gate_ok(p) and self._is_p_label(p):
                    start = p_index[p]
                    for i, per in enumerate(all_periods):
                        if i >= start:
                            series_timeline[per] = "q_period"
                # periods before 'start' remain at 'q_period_lag1'

            else:
                # Unsupported → keep defaults
                pass

            release_latest_block_dict[series] = series_timeline

        return release_latest_block_dict


