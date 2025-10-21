#%%

import pandas as pd
import numpy as np
import datetime as dt
import re

#%%
class Checks: 

    @staticmethod
    def get_series_meta_name(series):
        """
        Extract the base series name from blocked or lagged series names.

        Examples:
            'gdp_m1'         → 'gdp'
            'ifocast_ip_tot_m2_lag1' → 'ifocast_ip_tot'
            'sales_lag2'     → 'sales'
        """
        series_meta_name = re.sub(r'(_m\d+)?(_lag\d+)?$', '', series)

        return series_meta_name
    
    @staticmethod
    def sorted_periods(periods):
        def key(p):
            if isinstance(p, str) and p.startswith("p") and p[1:].isdigit():
                return (0, int(p[1:]))
            return (1, str(p))
        return sorted(periods, key=key)

# %%


#     def _get_m_block(self, series: str) -> str:
#         """
#         Extract the 'm' block (e.g., '_m1', '_m2') from blocked or lagged series names.

#         Examples:
#             'gdp_m1'                → 'm1'
#             'ifocast_ip_tot_m2_lag1' → 'm2'
#             'sales_lag2'            → ''   (no m-block)
#         """
#         match = re.search(r'_m\d+', series)
#         return match.group(0).lstrip("_") if match else ""
