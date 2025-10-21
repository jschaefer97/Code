#%%

import pandas as pd
import numpy as np
from loguru import logger

from data.datautils.statistics import Statistics

#%%
# [ ]: Add checks for other frequencies. 

# List of possible transformations
TRANSFORMATIONS = [
    'lin',  # No transformation (levels)
    'chg',  # First difference: x_t - x_{t-1}
    'ch1',  # Year-over-year difference: x_t - x_{t-12}
    'pch',  # Percent change: (x_t / x_{t-1} - 1) * 100
    'pc1',  # Year-over-year percent change: (x_t / x_{t-12} - 1) * 100
    'log',  # Natural logarithm: ln(x)
    'cch',  # Continuously compounded change: ln(x_t / x_{t-1})
    'cca',  # Continuously compounded annual change: (1/1) * ln(x_t / x_{t-12})
]

class Transform: 

    @staticmethod  
    def unit_q(series, transformation):
        """
        Transforms a Pandas Series assuming quarterly frequency.

        Supported transformations:
            'lin'  = No transformation (levels)
            'chg'  = First difference: x_t - x_{t-1}
            'ch1'  = Year-over-year difference: x_t - x_{t-4}
            'pch'  = Percent change: (x_t / x_{t-1} - 1) * 100
            'pc1'  = Year-over-year percent change: (x_t / x_{t-4} - 1) * 100
            'log'  = Natural logarithm: ln(x)
            'cch'  = Continuously compounded change: ln(x_t / x_{t-1})
            'cca'  = Continuously compounded annual change: ln(x_t / x_{t-4})

        Parameters:
            series (pd.Series): Input quarterly time series (with a DatetimeIndex).
            transformation (str): Transformation type.

        Returns:
            pd.Series: Transformed series with the same index, NaNs dropped.
        """

        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a Pandas Series.")

        if transformation == 'lin':
            transformed = series.copy()
        elif transformation == 'chg':
            transformed = series.diff()
        elif transformation == 'ch1':
            transformed = series.diff(4)
        elif transformation == 'pch':
            transformed = series.pct_change(fill_method=None) * 100
        elif transformation == 'pc1':
            transformed = series.pct_change(4, fill_method=None) * 100
        elif transformation == 'log':
            transformed = np.log(series)
        elif transformation == 'cch':
            transformed = np.log(series / series.shift(1))
        elif transformation == 'cca':
            transformed = np.log(series / series.shift(4))
        else:
            raise ValueError(f"{transformation}: Unknown transformation type.")

        return transformed.dropna()


    @staticmethod  
    def unit_m(series, transformation):
        """
        Transforms a Pandas Series assuming monthly frequency.

        Supported transformations:
            'lin'  = No transformation (levels)
            'chg'  = First difference: x_t - x_{t-1}
            'ch1'  = Year-over-year difference: x_t - x_{t-12}
            'pch'  = Percent change: (x_t / x_{t-1} - 1) * 100
            'pc1'  = Year-over-year percent change: (x_t / x_{t-12} - 1) * 100
            'log'  = Natural logarithm: ln(x)
            'cch'  = Continuously compounded change: ln(x_t / x_{t-1})
            'cca'  = Continuously compounded annual change: ln(x_t / x_{t-12})

        Parameters:
            series (pd.Series): Input monthly time series (with a DatetimeIndex).
            transformation (str): Transformation type.

        Returns:
            pd.Series: Transformed series with the same index, NaNs dropped.
        """

        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a Pandas Series.")

        if transformation == 'lin':
            transformed = series.copy()
        elif transformation == 'chg':
            transformed = series.diff()
        elif transformation == 'ch1':
            transformed = series.diff(12)
        elif transformation == 'pch':
            transformed = series.pct_change(fill_method=None) * 100
        elif transformation == 'pc1':
            transformed = series.pct_change(12, fill_method=None) * 100
        elif transformation == 'log':
            transformed = np.log(series)
        elif transformation == 'cch':
            transformed = np.log(series / series.shift(1))
        elif transformation == 'cca':
            transformed = np.log(series / series.shift(12))
        else:
            raise ValueError(f"{transformation}: Unknown transformation type.")

        return transformed.dropna()
    
    # @staticmethod # NOTE: Not needed because daily data is first converted to monthly frequency
    # def unit_d(series, transformation):
    #     """
    #     Transforms a Pandas Series assuming daily frequency.

    #     Supported transformations:
    #         'lin'  = No transformation (levels)
    #         'chg'  = First difference: x_t - x_{t-1}
    #         'ch1'  = Year-over-year difference: x_t - x_{t-252}
    #         'pch'  = Percent change: (x_t / x_{t-1} - 1) * 100
    #         'pc1'  = Year-over-year percent change: (x_t / x_{t-252} - 1) * 100
    #         'log'  = Natural logarithm: ln(x)
    #         'cch'  = Continuously compounded change: ln(x_t / x_{t-1})
    #         'cca'  = Continuously compounded annual change: ln(x_t / x_{t-252})

    #     Parameters:
    #         series (pd.Series): Input daily time series (with a DatetimeIndex).
    #         transformation (str): Transformation type.

    #     Returns:
    #         pd.Series: Transformed series with the same index, NaNs dropped.
    #     """

    #     if not isinstance(series, pd.Series):
    #         raise ValueError("Input must be a Pandas Series.")

    #     if transformation == 'lin':
    #         transformed = series.copy()
    #     elif transformation == 'chg':
    #         transformed = series.diff()
    #     elif transformation == 'ch1':
    #         transformed = series - series.shift(1, freq='Y')
    #     elif transformation == 'pch':
    #         transformed = series.pct_change() * 100
    #     elif transformation == 'pc1':
    #         transformed = (series / series.shift(1, freq='Y') - 1) * 100
    #     elif transformation == 'log':
    #         transformed = np.log(series)
    #     elif transformation == 'cch':
    #         transformed = np.log(series / series.shift(1))
    #     elif transformation == 'cca':
    #         transformed = np.log(series / series.shift(1, freq='Y'))
    #     else:
    #         raise ValueError(f"{transformation}: Unknown transformation type.")

    #     return transformed.dropna()

    @staticmethod
    def create_lags(dataset, Y, m, q):

        data = pd.DataFrame(index=dataset.index)
        X_vars = dataset.columns.drop(Y).tolist() 

        # Lags for Y (autoregressive terms)
        for i in range(1, m + 1):
            data[f'Y_lag_{i}'] = dataset[Y].shift(i)
        
        # Lags for each X variable
        for var in X_vars:
            for i in range(1, q + 1):
                data[f'{var}_lag_{i}'] = dataset[var].shift(i)
        
        data['Y_t'] = dataset[Y]
        return data.dropna()

    @staticmethod
    def freq_m_to_q(series, stock_flow):
        """
        Aggregates a monthly time series to quarterly using a single 'stock_flow' descriptor.
        
        Parameters:
        - series (pd.Series): Monthly time series with a DatetimeIndex.
        - stock_flow (str): One of the following:
            'level_stock', 'level_flow', 'cumulative_stock', 'growth_flow'
        
        Returns:
        - pd.Series: Quarterly aggregated series.
        """
        
        # Ensure the input is a Pandas Series
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a Pandas Series.")

        if stock_flow == "level_stock": # I(0) stock
            # Snapshot value → use end-of-quarter value
            return series.resample("QE").last()

        elif stock_flow == "level_flow": # I(0) flow
            # Monthly flow → average over quarter
            return series.resample("QE").mean()

        elif stock_flow == "cumulative_stock": # I(1) stock
            # Accumulated value → sum over quarter
            return series.resample("QE").sum()

        elif stock_flow == "growth_flow": # I(0) flow
            # Growth rates → weighted moving average (5 months)
            weights = np.array([1/3, 2/3, 1.0, 2/3, 1/3])
            weighted = series.rolling(5).apply(
                lambda x: np.dot(weights, x) if len(x) == 5 else np.nan, raw=True
            )
            return weighted.resample("QE").last()

        else:
            raise ValueError(
                f"Invalid 'stock_flow' value: {stock_flow}. Must be one of "
                "'level_stock', 'level_flow', 'cumulative_stock', 'growth_flow'."
            )

    @staticmethod
    def freq_d_to_m(series, stock_flow):
        """
        Aggregates a daily time series to monthly using a 'stock_flow' descriptor.

        Parameters:
        - series (pd.Series): Daily time series with a DatetimeIndex.
        - stock_flow (str): One of the following:
            'level_stock'        : Use end-of-month value (snapshot).
            'level_flow'         : Average value over the month.
            'cumulative_stock'   : Sum over the month (accumulated value).

        Returns:
        - pd.Series: Monthly aggregated series.

        Note:
        'growth_flow' is not supported for daily-to-monthly aggregation.
        """
        # Ensure the input is a Pandas Series
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a Pandas Series.")

        if stock_flow == "level_stock":
            # Snapshot value → use end-of-month value
            logger.info(f"Converted daily series '{series.name}' to monthly frequency using end-of-month value.")
            return series.resample("ME").last()

        elif stock_flow == "level_flow":
            # Daily flow → average over month
            logger.info(f"Converted daily series '{series.name}' to monthly frequency using average value.")
            return series.resample("ME").mean()

        elif stock_flow == "cumulative_stock":
            # Accumulated value → sum over month
            logger.info(f"Converted daily series '{series.name}' to monthly frequency using cumulative sum.")
            return series.resample("ME").sum()
        
        else:
            raise ValueError(
                f"Invalid 'stock_flow' value: {stock_flow}. Must be one of "
                "'level_stock', 'level_flow', 'cumulative_stock'. It cannot be 'growth_flow' for daily frequency series."
            )

    @staticmethod
    def freq_q_to_m(series, stock_flow):

        """
        Expands a quarterly time series to monthly frequency by backward-filling each quarter's value
        into its corresponding months.

        Parameters:
        - series (pd.Series): Quarterly time series with a DatetimeIndex.
        - stock_flow (str): Not used, included for API consistency.

        Returns:
        - pd.Series: Monthly frequency series with values filled from the quarterly series.
        """
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a Pandas Series.")

        # Convert to monthly frequency, backward-fill each quarter's value to its months
        series = series.resample("ME").bfill()
        return series
    
    @staticmethod
    def skip_sampling_to_q(series, freq):
        """
        For a monthly or quarterly series, return a DataFrame with quarterly frequency:
        - Quarterly series: single column, unchanged.
        - Monthly series: three columns per variable, each column is the value for month 1, 2, or 3 in the quarter.

        Parameters:
            series (pd.Series): Time series with a DatetimeIndex.
            freq (str): "ME" for monthly, "QE" for quarterly.

        Returns:
            pd.DataFrame: DataFrame indexed by quarter-end DatetimeIndex, columns for each month position (monthly) or single column (quarterly).
        """
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a Pandas Series.")

        s = series.copy().sort_index()

        if freq == "ME":
            df = pd.DataFrame({series.name: s})
            df['month_pos'] = ((df.index.month - 1) % 3) + 1
            df['qdate'] = pd.PeriodIndex(df.index.to_period('Q'))
            # Pivot to get each month in its own column per quarter
            blocked_df = df.pivot_table(index='qdate', columns='month_pos', values=series.name, aggfunc='first')
            blocked_df.columns = [f"{series.name}_m{int(m)}" for m in blocked_df.columns]
            # Set index to quarter end as DatetimeIndex, normalized to 00:00:00
            blocked_df.index = blocked_df.index.to_timestamp(how='end').normalize()

            logger.info(f"Converted monthly series '{series.name}' to quarterly frequency with monthly blocks.")

            return blocked_df

        elif freq == "QE":
            df = pd.DataFrame({series.name: s})
            df['qdate'] = pd.PeriodIndex(df.index.to_period('Q'))
            blocked_df = df.groupby('qdate')[series.name].first().to_frame()
            # Set index to quarter end as DatetimeIndex, normalized to 00:00:00
            blocked_df.index = blocked_df.index.to_timestamp(how='end').normalize()

            logger.info(f"Series '{series.name}' is already at quarterly frequency. Added to blocked DataFrame as is.")

            return blocked_df

        else:
            raise ValueError("freq must be 'ME' (monthly) or 'QE' (quarterly)")
    
                   

# %%
