#%%

from dataclasses import dataclass
import pandas as pd
from typing import Dict, Tuple, Optional

#%%

@dataclass
class Source:
    """
    Represents the source of a time series.
    """
    data: str  # The name of the data source
    variable: str  # The variable name in the data source

@dataclass
class Series:
    """
    Represents a time series with metadata.
    """
    name: str  # The name of the series
    source: Source  # The source of the series
    component: str = ""
    category: str = ""
    subcategory: str = ""  # Subcategory of the series
    description: str = ""  # A description of the series
    unit: str = ""  # The unit of the series
    stock_flow: str = "" # Indicates whether the series is a stock or flow variable
    freq: str = ""  # The frequency of the series
    start_date: pd.Timestamp = None  # The start date of the series
    end_date: pd.Timestamp = None  # The end date of the series

    imputed: bool = False  # Whether the series is imputed
    stationarity: bool = False  # Whether the series is stationary
    transformation: str = ""  # The transformation applied to the series to make it stationary
    transformation_applied: str = ""  # The transformation applied to the series
    add_info: str = ""  # Additional information about the series
    filtered: bool = False  # Whether the series has been dropped

    release_values_df: pd.DataFrame = None

    m1_period: str = "none"  # The M1 period of the series
    m2_period: str = "none"  # The M2 period of the series
    m3_period: str = "none"  # The M3 period of the series
    m1_lag1_period: str = "none"  # The M1 lagged period of the series
    m2_lag1_period: str = "none"  # The M2 lagged period
    m3_lag1_period: str = "none"  # The M3 lagged period
    q_period: str = "none"
    q_lag1_period: str = "none"  # The Q lagged period of the series

@dataclass
class GroupSeries:
    """
    Represents a group of series that share a common source and metadata.
    """
    series_dict: Dict[str, Tuple[str, Optional[str]]]  # series_name -> (variable, transformation)
    source_data: str  # Common data source name (e.g., 'mb')
    component: str = ""
    category: str = ""
    subcategory: str = ""




# %%
