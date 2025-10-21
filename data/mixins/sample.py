import pandas as pd
from loguru import logger

class SampleMixin:
    def to_sample_dfs(self, dataset=None, start_date=None, end_date=None, nowcast_start=None):
        """
        Split dataset into:
        - Full-Sample: [start_date, end_date]
        - In-Sample: [start_date, nowcast_start)
        - Out-of-Sample: [nowcast_start, end_date]

        Also trims all model dictionaries in self.series_model_dataframes to [start_date, end_date].

        Returns:
            dict of DataFrames.
        """
        if dataset is None or dataset.empty:
            logger.warning(f"{self.name}: No dataset provided.")
            return {
                "Full-Sample": pd.DataFrame(),
                "In-Sample": pd.DataFrame(),
                "Out-of-Sample": pd.DataFrame()
            }

        self._validate_df(
            dataset,
            expected_value="raw, imputed, mq_freq, blocked, stationary, filtered, lagged",
            attr_key="transformations"
        )

        # self._validate_df(
        #     dataset,
        #     expected_value="raw, imputed, mq_freq,stationary, blocked, filtered, lagged",
        #     attr_key="transformations"
        # )

        if nowcast_start is None:
            raise ValueError("nowcast_start must be provided.")
        nowcast_start = pd.Timestamp(nowcast_start)

        if start_date is None:
            start_date = dataset.index.min()
            logger.info(f"{self.name}: No start_date provided. Defaulting to earliest index date: {start_date.date()}")
        else:
            start_date = pd.Timestamp(start_date)

        if end_date is None:
            end_date = dataset.index.max()
            logger.info(f"{self.name}: No end_date provided. Defaulting to latest index date: {end_date.date()}")
        else:
            end_date = pd.Timestamp(end_date)

        # Trim to full sample window
        full_sample_df = dataset.loc[start_date:end_date]

        # Split into sub-samples
        in_sample_df = full_sample_df.loc[start_date:nowcast_start - pd.Timedelta(days=1)]
        out_sample_df = full_sample_df.loc[nowcast_start:end_date]

        logger.info(f"{self.name}: In-sample shape: {in_sample_df.shape}, Out-of-sample shape: {out_sample_df.shape}")

        sample_dfs = {
            "Full-Sample": full_sample_df,
            "In-Sample": in_sample_df,
            "Out-of-Sample": out_sample_df
        }

        self.sample_dfs = sample_dfs

        for df in sample_dfs.values():
            df.attrs["transformations"] = "raw, imputed, mq_freq, blocked, stationary, filtered, lagged, sampled"

        # --- Trim each model_df inside self.series_model_dataframes
        if hasattr(self, "series_model_dataframes") and self.series_model_dataframes:
            for series_name, model_dict in self.series_model_dataframes.items():
                for key, df in model_dict.items():
                    if isinstance(df, pd.DataFrame):
                        trimmed_df = df.loc[start_date:end_date]
                        self.series_model_dataframes[series_name][key] = trimmed_df
                        # logger.debug(f"{self.name}: Trimmed '{series_name}' [{key}] to shape {trimmed_df.shape}")

        return sample_dfs

    def to_full_sample_df(self, dataset=None, start_date=None, end_date=None, nowcast_start=None):
            """
            Split dataset into:
            - Full-Sample: [start_date, end_date]
            - In-Sample: [start_date, nowcast_start)
            - Out-of-Sample: [nowcast_start, end_date]

            Also trims all model dictionaries in self.series_model_dataframes to [start_date, end_date].

            Returns:
                dict of DataFrames.
            """
            if dataset is None or dataset.empty:
                logger.warning(f"{self.name}: No dataset provided.")
                return {
                    "Full-Sample": pd.DataFrame(),
                    "In-Sample": pd.DataFrame(),
                    "Out-of-Sample": pd.DataFrame()
                }

            self._validate_df(
                dataset,
                expected_value="raw, imputed, mq_freq, stationary, blocked, filtered, lagged",
                attr_key="transformations"
            )

            if nowcast_start is None:
                raise ValueError("nowcast_start must be provided.")
            nowcast_start = pd.Timestamp(nowcast_start)

            if start_date is None:
                start_date = dataset.index.min()
                logger.info(f"{self.name}: No start_date provided. Defaulting to earliest index date: {start_date.date()}")
            else:
                start_date = pd.Timestamp(start_date)

            if end_date is None:
                end_date = dataset.index.max()
                logger.info(f"{self.name}: No end_date provided. Defaulting to latest index date: {end_date.date()}")
            else:
                end_date = pd.Timestamp(end_date)

            # Trim to full sample window
            full_sample_df = dataset.loc[start_date:end_date]

            logger.info(f"{self.name}: Full-Sample shape: {full_sample_df.shape}")

            full_sample_df.attrs["transformations"] = "raw, imputed, mq_freq,stationary, blocked, filtered, lagged, sampled"

            # --- Trim each model_df inside self.series_model_dataframes
            if hasattr(self, "series_model_dataframes") and self.series_model_dataframes:
                for series_name, model_dict in self.series_model_dataframes.items():
                    for key, df in model_dict.items():
                        if isinstance(df, pd.DataFrame):
                            trimmed_df = df.loc[start_date:end_date]
                            self.series_model_dataframes[series_name][key] = trimmed_df
                            logger.info(f"{self.name}: Trimmed '{series_name}' [{key}] to shape {trimmed_df.shape}")

            return full_sample_df




























    # def to_full_sample_df(self, dataset=None, start_date=None, end_date=None, nowcast_start=None):
    #     """
    #     Split dataset into:
    #     - Full-Sample: [start_date, end_date]
    #     - In-Sample: [start_date, nowcast_start)
    #     - Out-of-Sample: [nowcast_start, end_date]

    #     Also trims all model dictionaries in self.series_model_dataframes to [start_date, end_date].

    #     Returns:
    #         dict of DataFrames.
    #     """
    #     if dataset is None or dataset.empty:
    #         logger.warning(f"{self.name}: No dataset provided.")
    #         return {
    #             "Full-Sample": pd.DataFrame(),
    #             "In-Sample": pd.DataFrame(),
    #             "Out-of-Sample": pd.DataFrame()
    #         }

    #     self._validate_df(
    #         dataset,
    #         expected_value="raw, imputed, mq_freq, blocked, stationary, filtered, lagged",
    #         attr_key="transformations"
    #     )

    #     if nowcast_start is None:
    #         raise ValueError("nowcast_start must be provided.")
    #     nowcast_start = pd.Timestamp(nowcast_start)

    #     if start_date is None:
    #         start_date = dataset.index.min()
    #         logger.info(f"{self.name}: No start_date provided. Defaulting to earliest index date: {start_date.date()}")
    #     else:
    #         start_date = pd.Timestamp(start_date)

    #     if end_date is None:
    #         end_date = dataset.index.max()
    #         logger.info(f"{self.name}: No end_date provided. Defaulting to latest index date: {end_date.date()}")
    #     else:
    #         end_date = pd.Timestamp(end_date)

    #     # Trim to full sample window
    #     full_sample_df = dataset.loc[start_date:end_date]

    #     logger.info(f"{self.name}: Full-Sample shape: {full_sample_df.shape}")

    #     full_sample_df.attrs["transformations"] = "raw, imputed, mq_freq, blocked, sampled"

    #     # --- Trim each model_df inside self.series_model_dataframes
    #     if hasattr(self, "series_model_dataframes") and self.series_model_dataframes:
    #         for series_name, model_dict in self.series_model_dataframes.items():
    #             for key, df in model_dict.items():
    #                 if isinstance(df, pd.DataFrame):
    #                     trimmed_df = df.loc[start_date:end_date]
    #                     self.series_model_dataframes[series_name][key] = trimmed_df
    #                     logger.info(f"{self.name}: Trimmed '{series_name}' [{key}] to shape {trimmed_df.shape}")

    #     return full_sample_df
