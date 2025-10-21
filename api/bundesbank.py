#%%

import time
import warnings
from collections import OrderedDict
import pandas as pd
import requests
import json
from loguru import logger
import xml.etree.ElementTree as ET

#%%

def parse_xml(xml_data):

    # Parse XML
    root = ET.fromstring(xml_data)

    # Define namespaces
    namespaces = {
        'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
        'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common',
        'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'
    }

    # Extract time series data
    time_series_data = []

    for obs in root.findall('.//generic:Obs', namespaces):
        try:
            obs_date = obs.find('generic:ObsDimension', namespaces).attrib['value']
            obs_value = obs.find('generic:ObsValue', namespaces).attrib['value']
            diff_element = obs.find('generic:Attributes/generic:Value[@id="BBK_DIFF"]', namespaces)
            obs_diff = diff_element.attrib['value'] if diff_element is not None else None
            time_series_data.append({'Date': obs_date, 'Value': obs_value, 'Difference': obs_diff})
        except Exception: pass

    # Convert to DataFrame
    time_series_df = pd.DataFrame(time_series_data)

    return time_series_df
 
@logger.catch
def extract(series,url,start):

    s = time.time()

    # draw data
    exp_container = []
    imp_container = []

    for key in series.keys():
        s_ex = series[key]["ex"]
        s_im = series[key]["im"]

        url_ex = url.format(series=s_ex)
        tmp_ex = parse_xml(requests.get(url_ex).text).rename(columns={"Value":key})
        tmp_ex.Date = pd.to_datetime(tmp_ex.Date)
        tmp_ex.set_index("Date",inplace=True)
        exp_container.append(tmp_ex.loc[:,[key]])

        tmp_im = parse_xml(requests.get(url.format(series=s_im)).text).rename(columns={"Value":key})
        tmp_im.Date = pd.to_datetime(tmp_im.Date)
        tmp_im.set_index("Date",inplace=True)
        imp_container.append(tmp_im.loc[:,[key]])

    exp = pd.concat(exp_container, axis=1).apply(lambda x:pd.to_numeric(x, errors="coerce"), axis=0)
    exp["Restposten"] = exp.Total - exp.iloc[:,1:].sum(axis=1)
    imp = pd.concat(imp_container, axis=1).apply(lambda x:pd.to_numeric(x, errors="coerce"), axis=0)
    imp["Restposten"] = imp.Total - imp.iloc[:,1:].sum(axis=1)

    exp = exp.loc[start:]
    imp = imp.loc[start:]

    return exp, imp

exp,imp = extract(dl_series, 'https://api.statistiken.bundesbank.de/rest/data/BBFBOPV/{series}', start="1999")