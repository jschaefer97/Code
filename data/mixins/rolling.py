import numpy as np
import pandas as pd

class RollingMixin:
    
    def get_fwr_idx_dict(self, dataset, start_date, nowcast_start, end_date):
        """
        Generate rolling train/test splits by stepping one index position ahead per iteration.
        Assumes df has a quarterly DateTimeIndex.
        """

        self._validate_df(
            dataset,
            expected_value="raw, imputed, mq_freq, blocked, stationary, filtered, lagged, sampled",
            attr_key="transformations"
        )

        # self._validate_df(
        #     dataset,
        #     expected_value="raw, imputed, mq_freq,stationary, blocked, filtered, lagged, sampled",
        #     attr_key="transformations"
        # )

        df = dataset.copy()
        df.index = pd.to_datetime(df.index)

        # Check quarterly frequency
        inferred = pd.infer_freq(df.index) 
        if inferred != "QE-DEC":
            raise ValueError(f"DataFrame index must be quarterly. Inferred: {inferred}")

        # Ensure index is sorted and unique
        df = df.loc[~df.index.duplicated()].sort_index()

        if start_date not in df.index:
            raise ValueError(f"Start date {start_date.date()} not in index.")
        if end_date not in df.index:
            raise ValueError(f"End date {end_date.date()} not in index.")
        if nowcast_start not in df.index:
            raise ValueError(f"Nowcast start {nowcast_start.date()} not in index.")

        fwr_idx = {}

        start_pos = df.index.get_loc(start_date)
        nowcast_pos = df.index.get_loc(nowcast_start)
        end_pos = df.index.get_loc(end_date)

        for test_pos in range(nowcast_pos, end_pos + 1):
            test_date = df.index[test_pos]
            train_idx = df.index[start_pos:test_pos].tolist()
            test_idx = [test_date]

            fwr_idx[test_date] = {
                "train_idx": train_idx,
                "test_idx": test_idx
            }

        self.fwr_idx = fwr_idx

        return fwr_idx