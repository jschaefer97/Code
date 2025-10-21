import pandas as pd
from loguru import logger
from data.datautils.transform import Transform

class BlockingMixin:
    def to_mq_freq_dfs(self, datasets=None):
        """
        Prepare mixed-frequency time series by harmonizing frequencies.

        Converts daily series to monthly (via aggregation), while keeping
        monthly and quarterly series unchanged.

        Parameters:
            datasets (dict, optional): {'QE': df, 'ME': df, 'D': df}.
                Defaults to: self.im_df_q, self.im_df_m, self.im_df_d.

        Returns:
            dict: Dictionary with 'QE' and 'ME' keys containing harmonized series.
        """

        mq_freq_dfs = {
            "QE": pd.DataFrame(),
            "ME": pd.DataFrame()
        }

        for freq_key, df in datasets.items():
            if df is None or df.empty:
                logger.warning(f"{self.name}: No dataset with {freq_key} Frequency provided for component {self.name}")
                continue

            self._validate_df(df, "raw, imputed", "transformations")
            prepared_df = {}

            for series in df.columns:
                s = df[series]
                if freq_key == "D":
                    stock_flow = self.meta[series].stock_flow
                    s = Transform.freq_d_to_m(s, stock_flow)
                    prepared_df[series] = s
                elif freq_key == "ME":
                    prepared_df[series] = s
                elif freq_key == "QE":
                    mq_freq_dfs["QE"][series] = s  # assign directly since quarterly is untouched

            if freq_key in ["D", "ME"]:
                mq_freq_dfs["ME"] = pd.concat([mq_freq_dfs["ME"], pd.DataFrame(prepared_df)], axis=1)

        for freq, df in mq_freq_dfs.items():
            df.attrs["transformations"] = "raw, imputed, mq_freq"

        self.mq_freq_df_q = mq_freq_dfs["QE"]
        self.mq_freq_df_m = mq_freq_dfs["ME"]
        self.mq_freq_dfs = mq_freq_dfs

        return mq_freq_dfs

    def to_blocked_df(self, datasets=None):
        """
        Convert monthly & quarterly data into a blocked format for mixed-frequency models.
        """

        blocked_dfs = []

        for freq_key, df in datasets.items():
            if df is None or df.empty:
                logger.info(f"{self.name}: No dataset for frequency '{freq_key}'")
                continue

            self._validate_df(df, "raw, imputed, mq_freq", "transformations")

            for series in df.columns:
                s = df[series]
                blocked = Transform.skip_sampling_to_q(s, freq_key)
                blocked_dfs.append(blocked)

        blocked_df = pd.concat(blocked_dfs, axis=1) if blocked_dfs else pd.DataFrame()

        blocked_df.attrs["transformations"] = "raw, imputed, mq_freq, blocked"

        self.blocked_df = blocked_df

        return blocked_df


    def to_blocked_df_stat(self, datasets=None):
        """
        Convert monthly & quarterly data into a blocked format for mixed-frequency models.
        """

        blocked_dfs = []

        for freq_key, df in datasets.items():
            if df is None or df.empty:
                logger.info(f"{self.name}: No dataset for frequency '{freq_key}'")
                continue

            self._validate_df(df, "raw, imputed, mq_freq, stationary", "transformations")

            for series in df.columns:
                s = df[series]
                blocked = Transform.skip_sampling_to_q(s, freq_key)
                blocked_dfs.append(blocked)

        blocked_df = pd.concat(blocked_dfs, axis=1) if blocked_dfs else pd.DataFrame()

        blocked_df.attrs["transformations"] = "raw, imputed, mq_freq, stationary, blocked"

        self.blocked_df = blocked_df

        return blocked_df
