import pandas as pd
from loguru import logger
from data.datautils.statistics import Statistics
from data.datautils.transform import Transform, TRANSFORMATIONS
from utils.checks import Checks
import re

class StationarityMixin:
    """
    Mixin class for checking and transforming quarterly time series data to ensure stationarity.
    """

    def to_stat_df(self, dataset=None, transform_all=False, confidence=None, start_date=None, end_date=None):
        """
        Transform quarterly time series data to ensure stationarity.

        Parameters:
            df (pd.DataFrame, optional): Quarterly frequency dataset.
                                         Defaults to self.prep_freq_stat_df_q.
            transform_all (bool): Whether to apply a default transformation to all series.
            confidence (float, optional): Confidence level for stationarity test.

        Returns:
            pd.DataFrame: Transformed (stationary) quarterly DataFrame.
        """

        if dataset is None or dataset.empty:
            logger.warning(f"{self.name}: No quarterly dataset provided.")
            return pd.DataFrame()

        self._validate_df(dataset, expected_value="raw, imputed, mq_freq, blocked", attr_key="transformations")
        processed = {}

        for series in dataset.columns:
            s = dataset[series]
            series_meta_name = Checks.get_series_meta_name(series)
            meta = self.meta.get(series_meta_name)

            if not meta:
                logger.warning(f"{self.name}: No metadata for series '{series}'. Skipping.")
                continue
            if s.empty or s.isna().all():
                logger.warning(f"{self.name}: Series '{series}' is empty or NaN. Skipping.")
                continue

            try:
                transformed = self._make_series_stationary(s, series, meta, confidence, transform_all, start_date=start_date, end_date=end_date)
                processed[series] = transformed
            except Exception as e:
                logger.error(f"{self.name}: Failed to process '{series}': {e}")

        stat_df = pd.DataFrame(processed)
        stat_df.attrs["transformations"] = "raw, imputed, mq_freq, blocked, stationary"

        self._update_meta_df()
        logger.info(f"{self.name}: Finished processing {len(processed)} quarterly series for stationarity.")

        return stat_df

    def _make_series_stationary(self, s, series, meta, confidence, transform_all, start_date=None, end_date=None):
        """
        Transform a single series to achieve stationarity.

        Returns:
            pd.Series: Transformed series.
        """
        # decide sample window for testing
        s_check = s.loc[start_date:end_date] if (start_date is not None or end_date is not None) else s
        s_stat_df = s  # full series to return transformed
        logger.debug(f"{self.name}: Testing stationarity for '{series}' on sample window {s_check.index.min()} to {s_check.index.max()}.")

        if Statistics.check_stationarity_s(s_check, confidence):
            logger.info(f"{self.name}: '{series}' is already stationary.")
        else:
            logger.warning(f"{self.name}: '{series}' is non-stationary. Attempting transformation.")

        # choose transformation
        if getattr(meta, "transformation", None):
            transformation = meta.transformation
        elif (meta.freq in {"ME", "D"}) and getattr(meta, "transformation_m1", None):
            # allow using a pre-set m1 transform for monthly/daily
            transformation = meta.transformation_m1
            logger.info(f"{self.name}: Using m1 preset transformation '{transformation}' for monthly/daily series '{series}'.")
        elif isinstance(transform_all, str) and transform_all in TRANSFORMATIONS:
            transformation = transform_all
        else:
            transformation = None

        # apply transformation on the (sample) series and evaluate
        if transformation:
            logger.info(f"{self.name}: Applying transformation '{transformation}' to '{series}'.")
            transformed_check = Transform.unit_q(s_check, transformation)
            transformed_stat_df = Transform.unit_q(s_stat_df, transformation)
            used_trans = transformation
            stationary = Statistics.check_stationarity_s(transformed_check, confidence)
        else:
            transformed, stationary, used_trans = self._stat_s_loop(series, s_check, confidence)
            if used_trans != "none":
                transformed_stat_df = Transform.unit_q(s_stat_df, used_trans)
            else:
                transformed_stat_df = s_stat_df

        # write generic meta
        try:
            meta.transformation_applied = used_trans
            meta.stationarity = stationary
        except Exception:
            pass

        # frequency-specific meta
        if meta.freq in ("ME", "D"):
            # monthly/daily use m1/m2/m3 blocks; no quarterly flags here
            meta.stationarity_q = None
            meta.transformation_applied_q = None

            m_block = self._get_m_block(series)  # 'm1' | 'm2' | 'm3' | ''
            if m_block == "m1":
                meta.stationarity_m1 = stationary
                meta.transformation_applied_m1 = used_trans
                # store per-block transform if you keep such a field
                try:
                    meta.transformation_m1 = used_trans
                except Exception:
                    pass
            elif m_block == "m2":
                meta.stationarity_m2 = stationary
                meta.transformation_applied_m2 = used_trans
            elif m_block == "m3":
                meta.stationarity_m3 = stationary
                meta.transformation_applied_m3 = used_trans
            # if '', we silently skip (not an m-blocked name)

        elif meta.freq == "QE":
            # quarterly: set q flags; clear monthly ones
            meta.stationarity_q = stationary
            meta.transformation_applied_q = used_trans

            meta.stationarity_m1 = None
            meta.transformation_applied_m1 = None
            meta.stationarity_m2 = None
            meta.transformation_applied_m2 = None
            meta.stationarity_m3 = None
            meta.transformation_applied_m3 = None
        else:
            raise ValueError(f"Unexpected frequency '{meta.freq}' for series '{series}'.")

        return transformed_stat_df

    def _stat_s_loop(self, series, s, confidence=None):
        """
        Try a set of transformations to achieve stationarity for a quarterly series.

        Returns:
            (pd.Series, bool, str): Transformed series, is_stationary flag, and used transformation name.
        """
        last_transformed = s

        for t in TRANSFORMATIONS:
            try:
                transformed = Transform.unit_q(s, t)
                if Statistics.check_stationarity_s(transformed, confidence):
                    logger.info(f"{self.name}: '{series}' became stationary with transformation '{t}'.")
                    return transformed, True, t
                last_transformed = transformed
            except Exception as e:
                logger.error(f"{self.name}: Failed trying transformation '{t}' for '{series}': {e}")

        logger.warning(f"{self.name}: No transformation made '{series}' stationary.")

        return last_transformed, False, "none"

    def _get_m_block(self, series: str) -> str:
        """
        Extract the rightmost 'm' block (e.g., 'm1', 'm2') scanning from the end.

        Examples:
            'gdp_m1'                   → 'm1'
            'ifocast_ip_tot_m2_lag1'   → 'm2'
            'de_bb_ms_m1_eur'          → 'm1'
            'de_bb_ms_m2_eur_m1'       → 'm1'
            'sales_lag2'               → ''   (no m-block)
        """
        parts = series.split('_')
        for part in reversed(parts):
            if re.fullmatch(r'm\d+', part):
                return part
        return ""

    def check_stationarity_df(self, dataset=None, confidence=None):
        """
        Perform ADF stationarity test on a quarterly dataset.

        Parameters:
            df (pd.DataFrame, optional): Dataset to check. Defaults to self.blocked_series_df.
            confidence (float, optional): Confidence level for ADF test.

        Returns:
            pd.DataFrame: ADF test summary for each series.
        """
        if dataset is None or dataset.empty:
            logger.warning(f"{self.name}: No quarterly dataset provided.")
            return pd.DataFrame()

        results = []
        for series in dataset.columns:
            s = dataset[series].dropna()
            adf_result = Statistics.check_unit_root(s, confidence)

            results.append({
                "Series": series,
                "Stationarity": adf_result.stationary,
                "ADF test statistic": adf_result.results[0],
                "ADF p-value": adf_result.results[1]
            })

            if not adf_result.stationary:
                logger.warning(f"{self.name}: {series} is non-stationary at confidence level {confidence}")

        check_stationarity_df = pd.DataFrame(results)

        return check_stationarity_df
    
















# import pandas as pd
# from loguru import logger
# from data.datautils.statistics import Statistics
# from data.datautils.transform import Transform, TRANSFORMATIONS
# from utils.checks import Checks
# import re

# class StationarityMixin:
#     """
#     Mixin class for checking and transforming quarterly time series data to ensure stationarity.
#     """

#     def to_stat_df(self, dataset_sample=None, dataset=None, transform_all=False, confidence=None):
#         """
#         Transform quarterly time series data to ensure stationarity.

#         Parameters:
#             df (pd.DataFrame, optional): Quarterly frequency dataset.
#                                          Defaults to self.prep_freq_stat_df_q.
#             transform_all (bool): Whether to apply a default transformation to all series.
#             confidence (float, optional): Confidence level for stationarity test.

#         Returns:
#             pd.DataFrame: Transformed (stationary) quarterly DataFrame.
#         """

#         if dataset is None or dataset.empty:
#             logger.warning(f"{self.name}: No quarterly dataset provided.")
#             return pd.DataFrame()

#         self._validate_df(dataset, expected_value="raw, imputed, mq_freq, blocked", attr_key="transformations")
#         processed = {}

#         for series in dataset.columns:
#             s_full = dataset[series]
#             # Use dataset_sample for choosing/checking transformations; fallback to full if not provided
#             s_sample = dataset_sample[series] if (dataset_sample is not None and series in dataset_sample.columns) else s_full

#             series_meta_name = Checks.get_series_meta_name(series)
#             meta = self.meta.get(series_meta_name)

#             if not meta:
#                 logger.warning(f"{self.name}: No metadata for series '{series}'. Skipping.")
#                 continue
#             if s_sample.empty or s_sample.isna().all():
#                 logger.warning(f"{self.name}: Series '{series}' is empty or NaN in sample. Skipping.")
#                 continue

#             try:
#                 # Decide stationarity and transformation based on the SAMPLE
#                 _ = self._make_series_stationary(s_sample, series, meta, confidence, transform_all)

#                 # Read back the chosen transformation from meta and apply it to the FULL series
#                 if meta.freq in ("ME", "D"):
#                     m_block = self._get_m_block(series)
#                     if m_block == "m1":
#                         used_trans = getattr(meta, "transformation_applied_m1", None)
#                     elif m_block == "m2":
#                         used_trans = getattr(meta, "transformation_applied_m2", None)
#                     elif m_block == "m3":
#                         used_trans = getattr(meta, "transformation_applied_m3", None)
#                     else:
#                         used_trans = None
#                 elif meta.freq == "QE":
#                     used_trans = getattr(meta, "transformation_applied_q", None)
#                 else:
#                     raise ValueError(f"Unexpected frequency '{meta.freq}' for series '{series}'.")

#                 if used_trans and used_trans != "none":
#                     processed[series] = Transform.unit_q(s_full, used_trans)
#                 else:
#                     # No valid transformation found on the sample → keep original series
#                     processed[series] = s_full

#             except Exception as e:
#                 logger.error(f"{self.name}: Failed to process '{series}': {e}")

#         stat_df = pd.DataFrame(processed)
#         stat_df.attrs["transformations"] = "raw, imputed, mq_freq, blocked, stationary"

#         self.imp_stat_df_q = stat_df
#         self.imp_stat_dfs = {"QE": stat_df}

#         self._update_meta_df()
#         logger.info(f"{self.name}: Finished processing {len(processed)} quarterly series for stationarity.")

#         return stat_df

#     def _make_series_stationary(self, s, series, meta, confidence, transform_all):
#         """
#         Transform a single series to achieve stationarity.

#         Returns:
#             pd.Series: Transformed series.
#         """
#         # Log current status
#         if Statistics.check_stationarity_s(s, confidence):
#             logger.info(f"{self.name}: '{series}' is already stationary.")
#         else:
#             logger.warning(f"{self.name}: '{series}' is non-stationary. Attempting transformation.")

#         # Choose transformation
#         if getattr(meta, "transformation", None):
#             transformation = meta.transformation
#         elif isinstance(transform_all, str) and transform_all in TRANSFORMATIONS:
#             transformation = transform_all
#         else:
#             transformation = None

#         # Apply transformation
#         if transformation:
#             logger.info(f"{self.name}: Applying transformation '{transformation}' to '{series}'.")
#             transformed = Transform.unit_q(s, transformation)
#             used_trans = transformation
#             stationary = Statistics.check_stationarity_s(transformed, confidence)
#         else:
#             transformed, stationary, used_trans = self._stat_s_loop(series, s, confidence)

#         # --- Update metadata (unified path) ---
#         if meta.freq in ("ME", "D"):
#             # monthly/daily use m1/m2/m3 blocks; no quarterly flags here
#             meta.stationarity_q = None
#             meta.transformation_applied_q = None

#             m_block = self._get_m_block(series)  # 'm1' | 'm2' | 'm3' | ''
#             if m_block == "m1":
#                 meta.stationarity_m1 = stationary
#                 meta.transformation_applied_m1 = used_trans
#             elif m_block == "m2":
#                 meta.stationarity_m2 = stationary
#                 meta.transformation_applied_m2 = used_trans
#             elif m_block == "m3":
#                 meta.stationarity_m3 = stationary
#                 meta.transformation_applied_m3 = used_trans
#             # if '', we silently skip (not an m-blocked name)

#         elif meta.freq == "QE":
#             # quarterly: set q flags; clear monthly ones
#             meta.stationarity_q = stationary
#             meta.transformation_applied_q = used_trans

#             meta.stationarity_m1 = None
#             meta.transformation_applied_m1 = None
#             meta.stationarity_m2 = None
#             meta.transformation_applied_m2 = None
#             meta.stationarity_m3 = None
#             meta.transformation_applied_m3 = None
#         else:
#             raise ValueError(f"Unexpected frequency '{meta.freq}' for series '{series}'.")

#         return transformed

#     def _stat_s_loop(self, series, s, confidence=None):
#         """
#         Try a set of transformations to achieve stationarity for a quarterly series.

#         Returns:
#             (pd.Series, bool, str): Transformed series, is_stationary flag, and used transformation name.
#         """
#         last_transformed = s

#         for t in TRANSFORMATIONS:
#             try:
#                 transformed = Transform.unit_q(s, t)
#                 if Statistics.check_stationarity_s(transformed, confidence):
#                     logger.info(f"{self.name}: '{series}' became stationary with transformation '{t}'.")
#                     return transformed, True, t
#                 last_transformed = transformed
#             except Exception as e:
#                 logger.error(f"{self.name}: Failed trying transformation '{t}' for '{series}': {e}")

#         logger.warning(f"{self.name}: No transformation made '{series}' stationary.")

#         return last_transformed, False, "none"

#     def check_stationarity_df(self, dataset=None, confidence=None):
#         """
#         Perform ADF stationarity test on a quarterly dataset.

#         Parameters:
#             df (pd.DataFrame, optional): Dataset to check. Defaults to self.blocked_series_df.
#             confidence (float, optional): Confidence level for ADF test.

#         Returns:
#             pd.DataFrame: ADF test summary for each series.
#         """
#         if dataset is None or dataset.empty:
#             logger.warning(f"{self.name}: No quarterly dataset provided.")
#             return pd.DataFrame()

#         results = []
#         for series in dataset.columns:
#             s = dataset[series].dropna()
#             adf_result = Statistics.check_unit_root(s, confidence)

#             results.append({
#                 "Series": series,
#                 "Stationarity": adf_result.stationary,
#                 "ADF test statistic": adf_result.results[0],
#                 "ADF p-value": adf_result.results[1]
#             })

#             if not adf_result.stationary:
#                 logger.warning(f"{self.name}: {series} is non-stationary at confidence level {confidence}")

#         check_stationarity_df = pd.DataFrame(results)

#         return check_stationarity_df

#     def _get_m_block(self, series: str) -> str:
#         """
#         Extract the 'm' block (e.g., '_m1', '_m2') from blocked or lagged series names.

#         Examples:
#             'gdp_m1'                → 'm1'
#             'ifocast_ip_tot_m2_lag1' → 'm2'
#             'sales_lag2'            → ''   (no m-block)
#         """
#         match = re.search(r'_m\d+', series)
#         return match.group(0).lstrip("_") if match else ""






































































































    # def to_stat_dfs(self, datasets=None, transform_all=False, confidence=None, start_date=None, end_date=None):
    #     """
    #     Transform time series data (per frequency) to ensure stationarity.

    #     Returns:
    #         dict[str, pd.DataFrame]: {"QE": df, "ME": df}
    #     """

    #     stat_dfs = {
    #         "QE": pd.DataFrame(),
    #         "ME": pd.DataFrame()
    #     }

    #     if not datasets:
    #         logger.warning(f"{self.name}: No datasets dict provided.")
    #         return stat_dfs

    #     for freq_key, df in datasets.items():

    #         if df is None or df.empty:
    #             logger.warning(f"{self.name}: No dataset with {freq_key} frequency provided for component {self.name}")
    #             continue

    #         self._validate_df(df, "raw, imputed, mq_freq", "transformations")

    #         processed = {}  # <-- reset per frequency

    #         for series in df.columns:
    #             s = df[series]
    #             series_meta_name = Checks.get_series_meta_name(series)
    #             meta = self.meta.get(series_meta_name)

    #             if not meta:
    #                 logger.warning(f"{self.name}: No metadata for series '{series}'. Skipping.")
    #                 continue
    #             if s.empty or s.isna().all():
    #                 logger.warning(f"{self.name}: Series '{series}' is empty or NaN. Skipping.")
    #                 continue

    #             try:
    #                 if freq_key == "ME":
    #                     logger.info(f"{self.name}: [ME] processing '{series}'")
    #                     transformed = self._make_series_stationary_m(s, series, meta, confidence, transform_all, start_date, end_date)
    #                 else:
    #                     logger.info(f"{self.name}: [QE] processing '{series}'")
    #                     transformed = self._make_series_stationary_q(s, series, meta, confidence, transform_all, start_date, end_date)
    #                 processed[series] = transformed
    #             except Exception as e:
    #                 logger.error(f"{self.name}: Failed to process '{series}': {e}")

    #         if processed:
    #             stat_dfs[freq_key] = pd.DataFrame(processed)
    #             stat_dfs[freq_key].attrs["transformations"] = "raw, imputed, mq_freq, stationary"
    #             logger.info(f"{self.name}: Finished {freq_key}: {len(processed)} series transformed.")

    #     # meta updated once at the end
    #     self._update_meta_df()
    #     total_series = sum(len(df.columns) for df in stat_dfs.values() if not df.empty)
    #     logger.info(f"{self.name}: Finished processing across frequencies. Total series: {total_series}")

    #     return stat_dfs

    # def _make_series_stationary_m(self, s, series, meta, confidence, transform_all, start_date=None, end_date=None):
    #     """
    #     MONTHLY: decide on stationarity using the sample window, but return FULL series transformed.
    #     """
    #     # Split into sample (decision) vs full (return)
    #     s_full = s
    #     s_sample = s_full.loc[start_date:end_date] if (start_date is not None or end_date is not None) else s_full

    #     pre_stat = Statistics.check_stationarity_s(s_sample, confidence)
    #     logger.info(f"{self.name}: [ME] pre-check on sample for '{series}': {pre_stat}")

    #     # Choose a transformation candidate (if provided)
    #     if meta.transformation:
    #         transformation = meta.transformation
    #     elif isinstance(transform_all, str) and transform_all in TRANSFORMATIONS:
    #         transformation = transform_all
    #     else:
    #         transformation = None

    #     if transformation:
    #         logger.info(f"{self.name}: [ME] applying preset/global transform '{transformation}' on SAMPLE for '{series}'.")
    #         transformed_sample = Transform.unit_q(s_sample, transformation)
    #         stationary = Statistics.check_stationarity_s(transformed_sample, confidence)
    #         meta.transformation_applied = transformation
    #         meta.stationarity = stationary
    #         logger.info(f"{self.name}: [ME] preset/global → stationary={stationary} on sample; returning FULL transformed.")

    #         # Always return FULL transformed series
    #         transformed_full = Transform.unit_q(s_full, transformation)
    #         return transformed_full

    #     # Otherwise, search on the SAMPLE to find a working transform
    #     transformed_sample, stationary, used_trans = self._stat_s_loop_m(series, s_sample, confidence)
    #     meta.transformation_applied = used_trans
    #     meta.stationarity = stationary
    #     logger.info(f"{self.name}: [ME] search chose '{used_trans}' for '{series}', stationary={stationary} on sample.")

    #     if used_trans and used_trans != "none":
    #         transformed_full = Transform.unit_q(s_full, used_trans)
    #         return transformed_full

    #     # No usable transform → return FULL series unchanged
    #     return s_full

    # def _make_series_stationary_q(self, s, series, meta, confidence, transform_all, start_date=None, end_date=None):
    #     """
    #     QE (or generic): decide on stationarity using the sample window, but return FULL series transformed.
    #     """
    #     # Split into sample (decision) vs full (return)
    #     s_full = s
    #     s_sample = s_full.loc[start_date:end_date] if (start_date is not None or end_date is not None) else s_full

    #     pre_stat = Statistics.check_stationarity_s(s_sample, confidence)
    #     logger.info(f"{self.name}: [QE] pre-check on sample for '{series}': {pre_stat}")

    #     # Choose a transformation candidate (if provided)
    #     if getattr(meta, "transformation", None):
    #         transformation = meta.transformation
    #     elif isinstance(transform_all, str) and transform_all in TRANSFORMATIONS:
    #         transformation = transform_all
    #     else:
    #         transformation = None

    #     if transformation:
    #         logger.info(f"{self.name}: [QE] applying preset/global transform '{transformation}' on SAMPLE for '{series}'.")
    #         transformed_sample = Transform.unit_q(s_sample, transformation)
    #         stationary = Statistics.check_stationarity_s(transformed_sample, confidence)
    #         meta.transformation_applied = transformation
    #         meta.stationarity = stationary
    #         logger.info(f"{self.name}: [QE] preset/global → stationary={stationary} on sample; returning FULL transformed.")

    #         transformed_full = Transform.unit_q(s_full, transformation)
    #         return transformed_full

    #     # Otherwise, search on the SAMPLE to find a working transform
    #     transformed_sample, stationary, used_trans = self._stat_s_loop(series, s_sample, confidence)
    #     meta.transformation_applied = used_trans
    #     meta.stationarity = stationary
    #     logger.info(f"{self.name}: [QE] search chose '{used_trans}' for '{series}', stationary={stationary} on sample.")

    #     if used_trans and used_trans != "none":
    #         transformed_full = Transform.unit_q(s_full, used_trans)
    #         return transformed_full

    #     # No usable transform → return FULL series unchanged
    #     return s_full

    # def _stat_s_loop_m(self, series, s, confidence=None):
    #     """
    #     Generic search loop (e.g., for QE). Tries TRANSFORMATIONS on the SAMPLE.
    #     Returns: (transformed_sample, is_stationary, used_transform)
    #     """
    #     last_transformed = s
    #     for t in TRANSFORMATIONS:
    #         try:
    #             x = Transform.unit_m(s, t)
    #             if Statistics.check_stationarity_s(x, confidence):
    #                 logger.info(f"{self.name}: [QE] '{series}' stationary on sample with '{t}'.")
    #                 return x, True, t
    #             last_transformed = x
    #         except Exception as e:
    #             logger.error(f"{self.name}: [QE] error applying '{t}' to '{series}': {e}")

    #     logger.warning(f"{self.name}: [QE] no transform makes '{series}' stationary on sample.")
    #     return last_transformed, False, "none"
