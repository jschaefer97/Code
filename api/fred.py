#%%

import os 
import pandas_datareader.data as web

from utils.utils import log_function_name_and_time

#%%

FRED_API_KEY = os.environ.get("FRED_API")

@log_function_name_and_time
def load_fred(series, start, end):
    # error catch block
    try:
        # load series data (note that series can be list and string)
        df = web.DataReader(series, "fred", start, end, retry_count=50, api_key=FRED_API_KEY)
    # catch exception
    except Exception as e:
        return f'The following exception was thrown: {e}'
    # if no exception is raised, return dataframe
    else:
        return df
    
    