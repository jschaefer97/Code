# %%

import time
import functools
import pandas as pd

#%%

def log_function_name_and_time(func):
    @functools.wraps(func)  # This is to preserve the metadata of the original function.
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if func.__name__ != "wrapper":
            print(f"Computing: {func.__name__} (took {elapsed_time:.4f})")
        return result
    return wrapper

def get_formatted_date(date: pd.Timestamp):
    return f"Q{date.quarter}_{date.year}"

def get_formatted_date_spec(date: pd.Timestamp):
    return f"{date.year}Q{date.quarter}"



