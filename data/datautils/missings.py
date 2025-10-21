import pandas as pd
from loguru import logger

class MissingDataHandler:

    @staticmethod    
    def impute_inner_missing(objectname, series, impute_method='linear'):
        """
        Impute missing values only between the first and last non-missing values of a pandas Series.
        Values before the first and after the last non-missing value remain missing.

        Args:
            series (pd.Series): Input series with missing values.
            impute_method (str): Imputation method for pandas.Series.interpolate (default: 'linear').

        Returns:
            pd.Series: Series with inner missing values imputed and rounded.
        """
        s = series.copy()
        first = s.first_valid_index()
        last = s.last_valid_index()

        if (
            first is not None and last is not None and first != last and
            s.loc[first:last].isna().any()
        ):
            s.loc[first:last] = s.loc[first:last].interpolate(impute_method=impute_method, limit_direction='both')
            s.loc[first:last] = s.loc[first:last].round(5)
            logger.info(f"{objectname}: Imputed inner missing values for {s.name} from {first} to {last} using impute_method '{impute_method}' and rounded the results")
            imputed = True
        else:
            imputed = False

        return s, imputed