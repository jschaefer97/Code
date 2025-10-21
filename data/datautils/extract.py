#%%

import pandas as pd
import datetime as dt
import numpy as np

from api.mb import load_mb_bulk, load_mb_series, load_mb_release_dates

class Extract:
    def __init__(self, series):

        # Source information for downloading data
        self.source = series.source
        self.series = self.source.variable if hasattr(self.source, "variable") else None
        self.data = self.source.data if hasattr(self.source, "data") else None

        # Series information for naming
        self.name = series.name if hasattr(series, "name") else None

        self._mb_series_loaded = False
        self._series_release_dates_loaded = False

        self._series_df = None
        self._freq = None
        self._title = None
        self._unit = None
        self._stockflow = None
        self._series_release_dates_df = None

        if self.data == "mb" and self.series is not None:
            self._load_mb_series()
            self._load_mb_release_dates()

    def _load_mb_series(self):
        if not self._mb_series_loaded:
            self._series_df, self._freq, self._title, self._unit, self._stockflow = load_mb_series(self.series)
            self._mb_series_loaded = True

    def _load_mb_release_dates(self):
        if self.data == "mb" and self.series is not None:
            self._series_release_dates_df = load_mb_release_dates(self.series)
            self._series_release_dates_df.columns = [f"{self.name}_rd"]
            self._series_release_dates_loaded = True

    def get_series_df(self):
        if self.data == "mb":
            self._load_mb_series()
            self._series_df.columns = [self.name]
            return self._series_df
        return None

    def get_series_freq(self):
        if self.data == "mb":
            self._load_mb_series()
            return self._freq
        return None

    def get_series_title(self):
        if self.data == "mb":
            self._load_mb_series()
            return self._title
        return None

    def get_series_unit(self):
        if self.data == "mb":
            self._load_mb_series()
            return self._unit
        return None

    def get_series_stockflow(self):
        if self.data == "mb":
            self._load_mb_series()
            stockflow = self._stockflow
            if stockflow == "stock":
                stockflow = "level_flow"
            elif stockflow == "flow":
                stockflow = "cumulative_stock"
            return stockflow
        return None
    
    def get_series_release_values_df(self):
        if self.data == "mb":
            self._load_mb_series()
            self._load_mb_release_dates()
            if self._series_release_dates_df is not None:
                n = len(self._series_release_dates_df)
                # Get the last n rows of _series_df, keep their index
                series_df_tail = self._series_df.tail(n)
                # Reset index of release_dates_df to align by position
                release_dates_df = self._series_release_dates_df.reset_index(drop=True)
                # Concatenate, keeping the index from series_df_tail
                series_release_values_df = pd.concat(
                    [series_df_tail.reset_index(drop=True), release_dates_df], axis=1
                )
                # Set the index back to the original from series_df_tail
                series_release_values_df.index = series_df_tail.index
                return series_release_values_df
        return None


