#%%

#%%
import warnings
from statsmodels.tsa.stattools import adfuller, kpss
import pandas as pd
import numpy as np
import math
from collections import namedtuple
from scipy.signal import argrelmax
from scipy.stats import norm
import scipy.stats as stats

import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_white
from statsmodels.tsa.stattools import acf

#%%

def _check_convert_y(y): # [ ]: Put this into utils.checks.py

    assert not np.any(np.isnan(y)), "`y` should not have any nan values"
    if isinstance(y, (pd.Series, pd.DataFrame)):
        y = y.values.squeeze()
    assert y.ndim==1
    return y

def _check_stationary_adfuller(y, confidence, **kwargs):

    y = _check_convert_y(y)
    res = namedtuple("ADF_Test", ["stationary", "results"])
    result = adfuller(y, **kwargs)
    if result[1]>confidence:
        return res(False, result)
    else:
        return res(True, result)

class Statistics:
    @staticmethod
    def check_unit_root(y, confidence, adf_params={}):
        
        adf_params['regression'] = "c"
        return _check_stationary_adfuller(y, confidence, **adf_params)
    
    @staticmethod
    def check_stationarity_s(series, confidence=None):
        """
        Check if a single series is stationary using the ADF test.

        Parameters:
            series (pd.Series): Time series data.
            confidence (float, optional): Confidence level for ADF test.

        Returns:
            bool: True if stationary.
        """
        s = series.dropna()
        adf_result = Statistics.check_unit_root(s, confidence)
        return adf_result.stationary


# %%
