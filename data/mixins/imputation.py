import pandas as pd
from loguru import logger
from utils.checks import *
from data.datautils.missings import MissingDataHandler

class ImputationMixin:
    def to_imp_dfs(self, datasets=None, impute=True, impute_method='linear'):
        """
        Impute missing values for all series in the provided datasets, grouped by frequency.

        Parameters:
            datasets (dict, optional): {'QE': df, 'ME': df, 'D': df}
            impute (bool): Whether to impute missing values.
            impute_method (str): Method used for imputation (default = 'linear').

        Returns:
            dict: Dictionary of imputed DataFrames.
        """

        imp_dfs = {
            "QE": pd.DataFrame(), 
            "ME": pd.DataFrame(), 
            "D": pd.DataFrame()
        }

        for freq_key, df in datasets.items():
            if df is None or df.empty:
                logger.warning(f"{self.name}: No dataset with {freq_key} Frequency provided for component {self.name}")
                continue

            self._validate_df(df, "raw", "transformations")
            imp_df = {}

            for series in df.columns:
                s = df[series]
                if impute:
                    s, imputed = self._impute_inner_missing(s, impute_method)
                    imp_df[series] = s
                    self.meta[series].imputed = imputed

            imp_dfs[freq_key] = pd.DataFrame(imp_df)

        for freq, df in imp_dfs.items():
            df.attrs["transformations"] = "raw, imputed"

        self.imp_df_q = imp_dfs["QE"]
        self.imp_df_m = imp_dfs["ME"]
        self.imp_df_d = imp_dfs["D"]
        self.imp_dfs = imp_dfs

        self._update_meta_df()

        return imp_dfs
    
    def _impute_inner_missing(self, series, impute_method='linear'):
        s = series.copy()
        first = s.first_valid_index()
        last = s.last_valid_index()

        if first is not None and last is not None and first != last and s.loc[first:last].isna().any():
            s.loc[first:last] = s.loc[first:last].interpolate(impute_method=impute_method, limit_direction='both')
            s.loc[first:last] = s.loc[first:last].round(5)
            logger.info(f"{self.name}: Imputed inner missing values for {s.name} from {first} to {last} using '{impute_method}'")
            return s, True
        return s, False



