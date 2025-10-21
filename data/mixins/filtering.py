from datetime import datetime
import pandas as pd
from loguru import logger
from utils.checks import Checks
from collections import defaultdict
from collections import Counter       
from data.datautils.statistics import Statistics

class FilteringMixin:
    def to_filtered_df(self, dataset=None, start_date=None, end_date=None, dropvarlist=None, lags=0, umidas_model_lags=0, y_var=None, y_var_lags=0):
        if dataset is None or dataset.empty:
            logger.warning(f"{self.name}: No dataset provided.")
            return pd.DataFrame()
    
        self._validate_df(
            dataset,
            expected_value="raw, imputed, mq_freq, blocked, stationary",
            attr_key="transformations"
        )

        # self._validate_df(
        #     dataset,
        #     expected_value="raw, imputed, mq_freq, stationary, blocked",
        #     attr_key="transformations"
        # )

        meta_names_to_drop = set()
        drop_reasons = {}

        def drop(series_meta_name, reason):
            if series_meta_name == y_var:
                return
            if series_meta_name not in meta_names_to_drop:
                meta_names_to_drop.add(series_meta_name)
                drop_reasons[series_meta_name] = reason
                logger.info(f"{self.name}: Dropping '{series_meta_name}' - {reason}")

        subset = dataset.loc[start_date:end_date] if start_date and end_date else dataset

        # 1. Drop based on explicit dropvarlist
        if dropvarlist:
            for var in dropvarlist:
                series_meta_name = Checks.get_series_meta_name(var)
                if series_meta_name != y_var:
                    drop(series_meta_name, "Manually excluded via dropvarlist")

        # 2. Drop based on metadata
        valid_freqs = {"D", "ME", "QE"}
        release_attrs = [
            "m1_period", "m2_period", "m3_period",
            "m1_lag1_period", "m2_lag1_period", "m3_lag1_period",
            "q_period", "q_lag1_period"
        ]

        for series_meta_name, meta in self.meta.items():
            if series_meta_name == y_var or series_meta_name in meta_names_to_drop:
                continue

            elif meta.freq == "QE" and getattr(meta, "stationarity_q", None) == False:
                drop(series_meta_name, "Non-stationary quarterly series")
            elif meta.freq in ("ME", "D"):
                # Drop if any monthly block is non-stationary
                m_flags = {f"m{i}": getattr(meta, f"stationarity_m{i}", None) for i in (1, 2, 3)}
                if any(flag is False for flag in m_flags.values()):
                    bad = ", ".join(k for k, v in m_flags.items() if v is False)
                    drop(series_meta_name, f"Non-stationary monthly block(s): {bad}")
            elif meta.freq not in valid_freqs:
                drop(series_meta_name, f"Unsupported frequency: {meta.freq}")
            elif any("Error" in str(getattr(meta, attr, "")) for attr in release_attrs):
                drop(series_meta_name, "Error in one or more release periods")
            elif meta.freq == "QE" and getattr(meta, "q_period", None) == "outsideQ":
                drop(series_meta_name, 'QE frequency with q_period == "outsideQ"')
            elif meta.freq == "ME":
                m_periods = [getattr(meta, p, None) for p in ("m1_period", "m2_period", "m3_period")]
                m_lag1_periods = [getattr(meta, p, None) for p in ("m1_lag1_period", "m2_lag1_period", "m3_lag1_period")]
                if any(p == "outsideQ" for p in m_lag1_periods):
                    drop(series_meta_name, 'ME frequency with one or more m*_lag1_period == "outsideQ"')
                elif all(p == "outsideQ" for p in m_periods):
                    drop(series_meta_name, 'ME frequency with all m*_period == "outsideQ"')

        # 3. Drop if start_date not in index
        if start_date:
            if start_date not in dataset.index:
                for col in dataset.columns:
                    series_meta_name = Checks.get_series_meta_name(col)
                    if series_meta_name != y_var:
                        drop(series_meta_name, f"Start date {start_date.date()} not in dataset index")

        # 4. Drop based on missing values in the sample window
        for col in subset.columns:
            series_meta_name = Checks.get_series_meta_name(col)
            if series_meta_name == y_var:
                continue
            if subset[col].isnull().any():
                drop(series_meta_name, f"Missing values between {start_date.date()} and {end_date.date()}")

        # 5. Drop based on insufficient history for lagging
        if start_date:
            for col in dataset.columns:
                series_meta_name = Checks.get_series_meta_name(col)
                if series_meta_name == y_var or series_meta_name in meta_names_to_drop:
                    continue

                base_required_lags = lags
                required_lags = umidas_model_lags if col == y_var else base_required_lags

                series = dataset[col].dropna()
                if series.empty:
                    drop(series_meta_name, "Series is empty")
                    continue

                aligned_start = series.index[series.index >= start_date]
                if aligned_start.empty:
                    drop(series_meta_name, f"No data on or after start date {start_date.date()}")
                    continue

                start_pos = series.index.get_loc(aligned_start[0])
                if start_pos < required_lags:
                    drop(series_meta_name, f"Insufficient lags ({required_lags}) before {aligned_start[0].date()}")

        # 6. Warning for duplicates in the source variable names
        variable_source_map = []

        for key in self.meta.keys():
            # series_meta_name = Checks.get_series_meta_name(col)

            variable_key = self.meta[key].source.variable
            variable_source_map.append((variable_key, key))

            # Find variable_keys that appear more than once

            variable_keys = [vk for vk, _ in variable_source_map]
            duplicates = [vk for vk, count in Counter(variable_keys).items() if count > 1]

            # For each duplicate variable_key, collect all keys that have this variable_key
            self.duplicate_rows = []
            for dup in duplicates:
                rows = [key for vk, key in variable_source_map if vk == dup]
                self.duplicate_rows.append((dup, rows))

        logger.warning(f"{self.name}: Duplicate variable keys found: {duplicates}. Check the mappings and decide how to handle them. A list of the corresponding series is available in self.duplicate_rows.")

        # Final drop
        cols_to_drop = [
            col for col in dataset.columns
            if Checks.get_series_meta_name(col) in meta_names_to_drop
        ]
        filtered_df = dataset.drop(columns=cols_to_drop, errors='ignore')

        # Update metadata
        for series_meta_name in meta_names_to_drop:
            if series_meta_name in self.meta:
                self.meta[series_meta_name].filtered = drop_reasons[series_meta_name]
                self.series_dataframes.pop(series_meta_name, None)

        self._update_meta_df()

        if cols_to_drop:
            logger.info(f"{self.name}: Final dropped columns: {cols_to_drop}")
        else:
            logger.info(f"{self.name}: No variables dropped.")

        filtered_df.attrs["transformations"] = "raw, imputed, mq_freq, blocked, stationary, filtered"
        
        # filtered_df.attrs["transformations"] = "raw, imputed, mq_freq, stationary, blocked, filtered"

        self.filtered_df = filtered_df
        return filtered_df




























    # def to_full_sample_df_stat(self, dataset, fwr_idx_dict, y_var, confidence=0.05):
    #     """
    #     Keep only those base series whose ALL lags/blocks are stationary across all rolling train windows.
    #     If any lag or block of a base series is non-stationary at any window, drop the entire base (all cols).
    #     """
    #     if dataset is None or dataset.empty:
    #         logger.warning(f"{self.name}: No dataset provided to drop_non_stat.")
    #         return pd.DataFrame()

    #     # Map each column to its base meta name once
    #     base_by_col = {col: Checks.get_series_meta_name(col) for col in dataset.columns}

    #     bad_bases = set()                          # base series to drop
    #     failures = defaultdict(list)               # base -> list of (col, q, reason)

    #     # Iterate rolling train windows
    #     for quarter in fwr_idx_dict.keys():
    #         train_idx = fwr_idx_dict[quarter]["train_idx"]

    #         df_q = dataset.loc[train_idx,]

    #         for col in df_q.columns:
    #             base = base_by_col[col]
    #             if base == y_var or base in bad_bases:
    #                 continue

    #             s = df_q[col].dropna()
    #             if s.empty:
    #                 bad_bases.add(base)
    #                 failures[base].append((col, quarter, "empty"))
    #                 continue

    #             try:
    #                 stat = Statistics.check_stationarity_s(s, confidence)
    #             except Exception as e:
    #                 stat = False
    #                 failures[base].append((col, quarter, f"error: {e!s}"))

    #             if not stat:
    #                 bad_bases.add(base)
    #                 failures[base].append((col, quarter, "non-stationary"))

    #     # Build final list of columns to keep (drop every column whose base is in bad_bases, except y_var)
    #     cols_to_keep = []
    #     for col in dataset.columns:
    #         base = Checks.get_series_meta_name(col)
    #         if base == y_var or base not in bad_bases:
    #             cols_to_keep.append(col)

    #     full_sample_stat_df = dataset.loc[:, cols_to_keep].copy()

    #     # Update meta + logging
    #     if bad_bases:
    #         for base in sorted(bad_bases):
    #             if base == y_var:
    #                 continue
    #             if base in self.meta:
    #                 self.meta[base].stationarity = False
    #                 self.meta[base].filtered = "Non-stationary in rolling train windows"
    #             logger.info(f"{self.name}: Dropping base '{base}' (all lags/blocks). Failures: {failures.get(base)}")
    #     else:
    #         logger.info(f"{self.name}: No non-stationary bases detected across rolling windows (alpha={confidence}).")

    #     self._update_meta_df()

    #     # Mark transform history
    #     prev = dataset.attrs.get("transformations", "")
    #     suffix = "nonstat_filtered"
    #     full_sample_stat_df.attrs["transformations"] = f"{prev}, {suffix}" if prev else suffix

    #     return full_sample_stat_df


