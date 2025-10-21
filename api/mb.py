#%%
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine
from loguru import logger

import win32com.client
c = win32com.client.Dispatch("Macrobond.Connection")
d = c.Database

from macrobond_api_constants import SeriesFrequency as f
from macrobond_api_constants import SeriesWeekdays as wk

from utils.utils import log_function_name_and_time

#%%

@log_function_name_and_time
def load_mb_series(series):
    """
    Load a single Macrobond series as a pandas DataFrame, resampled to its frequency.
    
    Args:
        series (str): The Macrobond series code.
    
    Returns:
        tuple: (DataFrame of the series, frequency string, series title)
    """
    try:
        # Load series
        s = d.FetchOneSeries(series)
        
        # Create dataframe
        series_df = pd.DataFrame(s.Values, columns=[s.Title], index = [dt.datetime(e.year,e.month,e.day) for e in s.DatesAtStartOfPeriod])
        
        # Determine frequency
        if s.Frequency == 6: # monthly data
            freq = "ME"
        if s.Frequency == 4: # quarterly data
            freq = "QE"
        if s.Frequency == 8: # quarterly data
            freq = "D"
        if s.Frequency == 1: # quarterly data
            freq = "Y"

        # Get series title
        title = s.Title

        # Get metadata
        m = s.Metadata

        # Get unit
        unit = m.GetFirstValue("DisplayUnit")
        
        # Get stock/flow
        stockflow = m.GetFirstValue("Class")

        # Prepare series DataFrame
        series_df = series_df.resample(freq).mean()

        return series_df, freq, title, unit, stockflow

    except Exception as e:
        
        logger.error(f"Error in {series}: {e}")

def load_mb_bulk(lst, prefix="", flags=False, series_names=False, date_check=None): 
    """
    Load multiple Macrobond series in bulk as a single DataFrame, resampled to their frequencies.
    
    Args:
        lst (list): List of Macrobond series codes.
        prefix (str, optional): Prefix to add to each series code.
        flags (bool, optional): Not used.
        series_names (bool, optional): If True, use series codes as column names.
        date_check (str or pd.Timestamp, optional): If provided, checks if all series are up to date.
    
    Returns:
        DataFrame: Combined DataFrame of all series.
    """
    if date_check:
        date_check = pd.to_datetime(date_check)

    lst = [prefix+e for e in lst]
    listOfSeries = d.FetchSeries(lst)
    container = []
    container_lst = []
    check_container = []

    for i,s in enumerate(listOfSeries):
        
        try:

            # create dataframe
            series_df = pd.DataFrame(s.Values, 
                                        columns=[s.Title], 
                                        index = [dt.datetime(e.year,e.month,e.day) for e in s.DatesAtStartOfPeriod])

            # determin frequency

            if s.Frequency == 6: # monthly data
                freq = "ME"
            if s.Frequency == 4: # quarterly data
                freq = "QE"
            if s.Frequency == 8: # quarterly data
                freq = "D"
            if s.Frequency == 1: # quarterly data
                freq = "Y"
                
            series_df = series_df.resample(freq).mean()

            container.append(series_df)
            container_lst.append(lst[i])
            
            # get date 
            lastmod = s.Metadata.GetFirstValue("LastModifiedTimeStamp")
            lastmod = pd.to_datetime(lastmod.strftime("%Y-%m-%d %H:%M:%S"))
            check_container.append(lastmod)
            
        except Exception as e:
            
            logger.error(f"Error in {s}: {e}")

    df_out = pd.concat(container,axis=1)

    if date_check:
        
        checkframe = pd.DataFrame(dict(zip(lst,check_container)), index=["lastmod"]).T
        checkframe["check"] = checkframe.lastmod >= date_check
        
        if checkframe.check.sum() != checkframe.shape[0]:
            logger.error(checkframe)
            assert False, "Data not up to date!!"
            
    if series_names:
        df_out.columns = container_lst
            
    return df_out

def load_mb_next_release(series): 
    """
    Get the next release date for a given Macrobond series.
    
    Args:
        series (str): The Macrobond series code.
    
    Returns:
        datetime.datetime: The next release date, or None if not available.
    """
    try:
        # load series
        s = d.FetchOneSeries(series)
            
        releaseName = s.Metadata.GetFirstValue("Release")
        if (releaseName is not None):
            r = d.FetchOneEntity(releaseName)

            nrt = r.Metadata.GetFirstValue("NextReleaseEventTime")

            if nrt.year is not None:

                # next release time
                date_out = dt.datetime(nrt.year,nrt.month,nrt.day)

            else:
                date_out = dt.datetime(nrt.month,nrt.day)

        return date_out

    except Exception as e:
        
        logger.error(f"Error in {series}: {e}")

def load_mb_release_dates(series):
    """
    Returns a DataFrame with the release dates for a given Macrobond series.

    Args:
        series (str): The Macrobond series code.

    Returns:
        pd.DataFrame: DataFrame with a single column 'release_date' containing the release dates.
    """
    def getRevisionTimestamp(m):
        if m is None:
            return None
        return m.GetFirstValue("RevisionTimestamp")

    s = d.FetchOneSeriesWithRevisions(series)
    firstReleaseSeries = s.GetNthRelease(0)
    firstReleaseDates = [
        getRevisionTimestamp(vm) for vm in firstReleaseSeries.ValuesMetadata
    ]
    # Convert to datetime and filter out None
    date_list = [
        dt.datetime(date.year, date.month, date.day)
        for date in firstReleaseDates if date is not None
    ]

    df = pd.DataFrame({'release_date': date_list})
    return df



# %%
