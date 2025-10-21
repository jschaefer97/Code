#%%%

import pandas as pd
from collections import OrderedDict
from loguru import logger
import time

from data.datautils.extract import Extract
from utils.checks import *
from data.seriesdataclass import Source, Series, GroupSeries

from data.mixins.meta import MetaMixin
from data.mixins.raggededgesimul import RaggedEdgeSimulMixin
from data.mixins.imputation import ImputationMixin
from data.mixins.validation import ValidationMixin
from data.mixins.blocking import BlockingMixin
from data.mixins.stationarity import StationarityMixin
from data.mixins.filtering import FilteringMixin
from data.mixins.lagging import LaggingMixin
from data.mixins.sample import SampleMixin
from data.mixins.rolling import RollingMixin
from data.mixins.dataoutput import DataOutputMixin

#%%
class NOWData(MetaMixin, RaggedEdgeSimulMixin, ImputationMixin, ValidationMixin, BlockingMixin, StationarityMixin, FilteringMixin, LaggingMixin, SampleMixin, RollingMixin, DataOutputMixin): 
    def __init__(self, name):
        """
        Initialize a NOWData object for managing time series data and metadata.

        Parameters:
            name (str): The name of the NOWData object/component.
        """
        self.name = name
        self.meta = OrderedDict()  # Stores metadata for all series
        self._meta_df = None  # Internal attribute for metadata DataFrame
        self.series_dataframes = {}  # Dictionary to store individual series DataFrames
        self.series_release_values_dataframes = {}  # Dictionary to store series release values DataFrames
        self.blocked_series_release_values_dataframes = {}
        self.series_model_dataframes = {}  # Dictionary to store series DataFrames for modeling
        self.series_release_periods = {}  # Dictionary to store series release periods
        self.same_freq = None  # Placeholder for DataFrame with all series at the same frequency
        self._add_counter = 0

    def __repr__(self) -> str:
        """
        Returns a string representation of the NOWData object.

        Returns:
            str: Description of the NOWData object.
        """
        return f"NOWModule class for {self.name}"

    def add(self, series_or_group):
        """
        Add a time series or group of series to the NOWData object.

        Parameters:
            series_or_group (Series or GroupSeries): Series object with metadata, 
                                                    or GroupSeries containing multiple Series.
        """

        # Handle GroupSeries
        if isinstance(series_or_group, GroupSeries):
            for name, (variable, transformation) in series_or_group.series_dict.items():
                series = Series(
                    name=name,
                    source=Source(data=series_or_group.source_data, variable=variable),
                    component=series_or_group.component,
                    category=series_or_group.category,
                    subcategory=series_or_group.subcategory,
                    transformation=transformation or "",  # fallback to empty string
                )
                self.add(series)  # Recursively add each Series
            return  # Prevent the rest of the logic from running on GroupSeries

        # Handle individual Series
        series = series_or_group  # Rename for clarity

        # Store metadata
        self.meta[series.name] = series

        # Extract and store data
        extractor = Extract(series)

        series_df = extractor.get_series_df()
        self.series_dataframes[series.name] = series_df

        release_values_df = extractor.get_series_release_values_df()
        self.series_release_values_dataframes[series.name] = release_values_df

        # Fill in missing metadata
        if not series.freq:
            series.freq = extractor.get_series_freq()
        if not series.unit:
            series.unit = extractor.get_series_unit()
        if not series.description:
            series.description = extractor.get_series_title()
        if not series.component:
            series.component = self.name
        if not series.stock_flow:
            series.stock_flow = extractor.get_series_stockflow()

        series.start_date = series_df.index[0] if not series_df.empty else None
        series.end_date = series_df.index[-1] if not series_df.empty else None

        self._add_counter += 1
        if self._add_counter % 20 == 0:
            logger.info(f"{self.name}: Added {self._add_counter} series, taking a short break to avoid overload.")
            time.sleep(2)

    def to_raw_dfs(self):
        """
        Combine all series DataFrames into separate DataFrames by frequency.

        Returns:
            dict: Dictionary with keys 'QE', 'ME', 'D', each containing a DataFrame of series at that frequency.
        """
        # Initialize empty DataFrames for each frequency
        raw_dfs = {
            "QE": pd.DataFrame(),
            "ME": pd.DataFrame(),
            "D": pd.DataFrame(),
        }

        # Iterate through the series metadata and collect DataFrames by frequency
        for series in self.meta.values():
            series_df = self.series_dataframes.get(series.name)
            if series_df is not None and not series_df.empty:
                if series.freq == "QE":
                    raw_dfs["QE"] = pd.concat([raw_dfs["QE"], series_df], axis=1)
                    logger.info(f"{self.name}: Added {series.name} to quarterly raw DataFrame.")
                elif series.freq == "ME":
                    raw_dfs["ME"] = pd.concat([raw_dfs["ME"], series_df], axis=1)
                    logger.info(f"{self.name}: Added {series.name} to monthly raw DataFrame.")
                elif series.freq == "D":
                    raw_dfs["D"] = pd.concat([raw_dfs["D"], series_df], axis=1)
                    logger.info(f"{self.name}: Added {series.name} to daily raw DataFrame.")
                else:
                    logger.warning(f"{self.name}: Unknown frequency '{series.freq}' for series '{series.name}'.")
            else:
                logger.warning(f"{self.name}: The series '{series.name}' is empty or not found in the series_dataframes.")

        for freq, df in raw_dfs.items():
            df.attrs["transformations"] = "raw"

        # Store the DataFrames as attributes for convenience
        self.raw_df_q = raw_dfs["QE"]
        self.raw_df_m = raw_dfs["ME"]
        self.raw_df_d = raw_dfs["D"]
        self.raw_dfs = raw_dfs  

        return raw_dfs
    
   

# %%
