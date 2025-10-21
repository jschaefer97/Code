import pandas as pd
from loguru import logger

class MetaMixin:
    def to_meta_df(self):
        """
        Convert all series metadata to a pandas DataFrame.

        Returns:
            pandas.DataFrame: DataFrame with metadata for all series.
        """
        rows = []
        for meta_obj in self.meta.values():
            # guard: skip anything that isn't your expected meta-like object
            # (pandas.Series etc. can sneak in if something assigns to self.meta by mistake)
            if isinstance(meta_obj, pd.Series):
                logger.error(f"{self.name}: Unexpected pandas.Series found in self.meta; skipping entry.")
                continue

            # safe getters with None defaults to avoid AttributeError on early stages
            rows.append({
                "Name": getattr(meta_obj, "name", None),
                "Start Date": getattr(meta_obj, "start_date", None),
                "End Date": getattr(meta_obj, "end_date", None),

                "Component": getattr(meta_obj, "component", None),
                "Category": getattr(meta_obj, "category", None),
                "Subcategory": getattr(meta_obj, "subcategory", None),

                "Datasource": getattr(getattr(meta_obj, "source", None), "data", None),
                "Original Variable Name": getattr(getattr(meta_obj, "source", None), "variable", None),
                "Description": getattr(meta_obj, "description", None),

                "Unit": getattr(meta_obj, "unit", None),
                "Frequency": getattr(meta_obj, "freq", None),
                "Stock/Flow": getattr(meta_obj, "stock_flow", None),

                "Imputed": getattr(meta_obj, "imputed", None),
                # "Stationarity": getattr(meta_obj, "stationarity", None),
                "Transformation Defined": getattr(meta_obj, "transformation", None),
                # "Transformation Applied": getattr(meta_obj, "transformation_applied", None),

                "M1 Period": getattr(meta_obj, "m1_period", None),
                "M2 Period": getattr(meta_obj, "m2_period", None),
                "M3 Period": getattr(meta_obj, "m3_period", None),
                "Q Period": getattr(meta_obj, "q_period", None),
                "M1 Lag1 Period": getattr(meta_obj, "m1_lag1_period", None),
                "M2 Lag1 Period": getattr(meta_obj, "m2_lag1_period", None),
                "M3 Lag1 Period": getattr(meta_obj, "m3_lag1_period", None),
                "Q Lag1 Period": getattr(meta_obj, "q_lag1_period", None),

                "M1 Period Stationarity": getattr(meta_obj, "stationarity_m1", None),
                "M2 Period Stationarity": getattr(meta_obj, "stationarity_m2", None),
                "M3 Period Stationarity": getattr(meta_obj, "stationarity_m3", None),
                "Q Period Stationarity": getattr(meta_obj, "stationarity_q", None),

                "M1 Period Lead": getattr(meta_obj, "transformation_m1", None),
                "M1 Period Transformation": getattr(meta_obj, "transformation_applied_m1", None),
                "M2 Period Transformation": getattr(meta_obj, "transformation_applied_m2", None),
                "M3 Period Transformation": getattr(meta_obj, "transformation_applied_m3", None),
                "Q Period Transformation": getattr(meta_obj, "transformation_applied_q", None),

                "Filtered": getattr(meta_obj, "filtered", None),
                "Additional Info": getattr(meta_obj, "add_info", None),
            })

        meta_df = pd.DataFrame(rows).reset_index(drop=True)
        meta_df.index += 1  # Start index at 1
        return meta_df

    def _update_meta_df(self):
        """
        Update the internal metadata DataFrame from the current metadata dictionary.
        """
        self._meta_df = self.to_meta_df()

    @property
    def meta_df(self):
        """
        Returns the current metadata as a pandas DataFrame.
        """
        return self.to_meta_df()
