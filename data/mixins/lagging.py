import pandas as pd
from loguru import logger
from utils.checks import Checks


class LaggingMixin:
    # ===========================
    # Public: build model frames
    # ===========================
    def get_model_dfs(self, dataset=None, y_var=None, umidas_model_lags=4, y_var_lags=None):
        """
        1) Plan feasible layouts + exact raw lags needed per meta series
        2) Build a compact lagged_df (helper) that includes ONLY the lags required for those layouts
        3) Slice lagged_df to construct series-specific model DataFrames

        Returns:
            (series_model_dataframes: dict, y_lag_depth: int, needed_raw_lags: dict)
        """
        if dataset is None or dataset.empty:
            logger.warning(f"{self.name}: No dataset provided.")
            return {}, 0, {}

        self._validate_df(
            dataset,
            expected_value="raw, imputed, mq_freq, blocked, stationary, filtered",
            attr_key="transformations"
        )

        # self._validate_df(
        #     dataset,
        #     expected_value="raw, imputed, mq_freq, stationary, blocked, filtered",
        #     attr_key="transformations"
        # )

        if y_var is None or y_var not in dataset.columns:
            raise ValueError(f"{self.name}: Valid y_var must be provided and present in dataset.")

        # 1) PLAN: needed lags and feasible layouts (single helper)
        needed_raw_lags, chosen_layouts, me_base_layouts, me_ext_layouts, qe_layouts = \
            self._plan_needed_lags(dataset=dataset, y_var=y_var, umidas_model_lags=umidas_model_lags)

        # y-lag depth: explicit or fallback to global
        y_lag_depth = y_var_lags if y_var_lags is not None else umidas_model_lags

        # 2) Build a compact lagged_df *for models* (only what's required to build the planned layouts)
        lagged_df = self._to_model_lagged_df(
            dataset=dataset,
            y_var=y_var,
            y_var_lags=y_lag_depth,
            series_lag_plan=needed_raw_lags
        )

        # 3) Build model DataFrames from that compact lagged_df
        y_cols = [y_var] + [f"{y_var}_lag{i}" for i in range(1, y_lag_depth + 1)]
        y_only = lagged_df[y_cols].dropna()
        self.series_model_dataframes = {y_var: {"full_model_df": y_only}}
        logger.info(f"{self.name}: Constructed model_dict for dependent variable '{y_var}'")

        for meta_name, layouts in chosen_layouts.items():
            meta = self.meta.get(meta_name)
            if meta is None:
                continue

            freq = meta.freq
            related = [c for c in lagged_df.columns if Checks.get_series_meta_name(c) == meta_name]

            model_dict = {}
            # keep simple: y + all related columns we have in the compact lagged_df
            full_cols = y_cols + related
            model_dict["full_model_df"] = lagged_df[full_cols].dropna()

            # build a period dataframe, rename predictors to mlag*/qlag*
            def build_period(tokens, out_key, rename_prefix):
                cols = y_cols[:]
                if freq in {"ME", "D"}:
                    # tokens like 'm1', 'm2_lag3' -> "{meta_name}_{token}"
                    for t in tokens:
                        full = f"{meta_name}_{t}"
                        if full in lagged_df.columns:
                            cols.append(full)
                else:  # "QE"
                    for t in tokens:
                        if t == 'q':
                            full = meta_name
                        else:
                            lag_n = int(t.split("_lag")[1])  # 'q_lagN' -> N
                            full = f"{meta_name}_lag{lag_n}"
                        if full in lagged_df.columns:
                            cols.append(full)

                if len(cols) == len(y_cols):
                    return  # nothing to add
                df = lagged_df[cols].dropna()
                n_pred = len(cols) - len(y_cols)
                df.columns = y_cols + [f"{meta_name}_{rename_prefix}{i+1}" for i in range(n_pred)]
                model_dict[out_key] = df

            if freq in {"ME", "D"}:
                for key, tokens in me_base_layouts.items():
                    if key in layouts:
                        build_period(tokens, key, "mlag")
                for key, tokens in me_ext_layouts.items():
                    if key in layouts:
                        build_period(tokens, key, "mlag")
            elif freq == "QE":
                for key, tokens in qe_layouts.items():
                    if key in layouts:
                        build_period(tokens, key, "qlag")

            self.series_model_dataframes[meta_name] = model_dict
            logger.info(f"{self.name}: Constructed model_dict for '{meta_name}'")

        return self.series_model_dataframes

    # ====================================================
    # Public: minimal lagged dataframe (NOWCAST/preview)
    #         — scales with chosen_layouts and respects per-block selection
    # ====================================================
    def to_lagged_df(self, dataset, y_var, lags=4, y_var_lags=None):
        """
        Build a *minimal* lagged dataframe that follows the feasible lag periods
        AND only includes block lags that are actually referenced by layouts.

          - Always include `y_var` with `y_var_lags` lags.
          - For ME/D (blocked) series:
              * For each meta series, compute K_m1, K_m2, K_m3 where
                K_mi = max K s.t. layout 'mi_period_lagK' is present in chosen_layouts[meta].
              * Add lags 1..K_m1 to *_m1, 1..K_m2 to *_m2, 1..K_m3 to *_m3.
                (If only m3_period_lag1 exists, you'll get only *_m3_lag1 — no m1/m2 lags.)
          - For QE (quarterly) series:
              * Compute K_q = max K s.t. 'q_period_lagK' in chosen_layouts[meta].
              * Add q_lag1..q_lagK (i.e., '{meta}_lag1..K') to the base quarterly column.

        Params:
            dataset (pd.DataFrame)
            y_var (str)
            y_var_lags (int)
            chosen_layouts (dict): output of _plan_needed_lags()[1]

        Returns:
            pd.DataFrame
        """
        if dataset is None or dataset.empty:
            logger.warning(f"{self.name}: No dataset provided.")
            return pd.DataFrame()

        self._validate_df(
            dataset,
            expected_value="raw, imputed, mq_freq, blocked, stationary, filtered",
            attr_key="transformations"
        )

        # self._validate_df(
        #     dataset,
        #     expected_value="raw, imputed, mq_freq, stationary, blocked, filtered",
        #     attr_key="transformations"
        # )

        if y_var not in dataset.columns:
            logger.warning(f"{self.name}: y_var '{y_var}' not found in dataset.")
            return dataset.copy()

        # 1) PLAN: needed lags and feasible layouts (single helper)
        needed_raw_lags, chosen_layouts, me_base_layouts, me_ext_layouts, qe_layouts = \
            self._plan_needed_lags(dataset=dataset, y_var=y_var, umidas_model_lags=lags)

        # ---------- derive per-series per-block / quarterly lag depths from chosen_layouts ----------
        # For each meta series, store required depths per block:
        # {meta_name: {"m1": K1, "m2": K2, "m3": K3}}
        me_required = {}
        # For each meta series, store required quarterly depth:
        # {meta_name: Kq}
        qe_required = {}

        for meta_name, layouts in chosen_layouts.items():
            # ME/D per-block depths
            K_m1 = K_m2 = K_m3 = 0
            for name in layouts.keys():
                if name.startswith("m1_period_lag"):
                    try:
                        K_m1 = max(K_m1, int(name.split("_period_lag")[1]))
                    except Exception:
                        pass
                elif name.startswith("m2_period_lag"):
                    try:
                        K_m2 = max(K_m2, int(name.split("_period_lag")[1]))
                    except Exception:
                        pass
                elif name.startswith("m3_period_lag"):
                    try:
                        K_m3 = max(K_m3, int(name.split("_period_lag")[1]))
                    except Exception:
                        pass
            if any((K_m1, K_m2, K_m3)):
                me_required[meta_name] = {"m1": K_m1, "m2": K_m2, "m3": K_m3}

            # QE depth
            K_q = 0
            for name in layouts.keys():
                if name.startswith("q_period_lag"):
                    try:
                        K_q = max(K_q, int(name.split("_period_lag")[1]))
                    except Exception:
                        pass
            if K_q > 0:
                qe_required[meta_name] = K_q

        # ---------- build the minimal lagged df ----------
        lagged_df = dataset.copy()
        ordered_cols = []

        for col in dataset.columns:
            ordered_cols.append(col)

            if col == y_var:
                depth = max(0, int(y_var_lags))
                for k in range(1, depth + 1):
                    lag_col = f"{col}_lag{k}"
                    lagged_df[lag_col] = lagged_df[col].shift(k)
                    ordered_cols.append(lag_col)
                logger.info(f"{self.name}: Created {depth} y-lags for '{col}'.")
                continue

            meta_name = Checks.get_series_meta_name(col)
            meta = self.meta.get(meta_name)
            freq = getattr(meta, "freq", None)

            if freq in {"ME", "D"}:
                # Add only the lags for blocks explicitly required by chosen_layouts
                req = me_required.get(meta_name)
                if req:
                    # Determine which block this column is
                    block = None
                    if col.endswith("_m1"):
                        block = "m1"
                    elif col.endswith("_m2"):
                        block = "m2"
                    elif col.endswith("_m3"):
                        block = "m3"

                    if block:
                        K = int(req.get(block, 0))
                        for k in range(1, K + 1):
                            lag_col = f"{col}_lag{k}"
                            lagged_df[lag_col] = lagged_df[col].shift(k)
                            ordered_cols.append(lag_col)
                        if K > 0:
                            logger.info(f"{self.name}: Created {K} lags for '{col}' (block {block} from plan).")

            elif freq == "QE":
                # Add q_lag1..K only if plan says so
                K = int(qe_required.get(meta_name, 0))
                if K > 0 and col == meta_name:
                    for k in range(1, K + 1):
                        lag_col = f"{col}_lag{k}"
                        lagged_df[lag_col] = lagged_df[col].shift(k)
                        ordered_cols.append(lag_col)
                    logger.info(f"{self.name}: Created {K} q-lags for '{col}' (from plan).")

            else:
                logger.info(f"{self.name}: No minimal lags created for '{col}' (freq={freq}).")

        lagged_df = lagged_df[ordered_cols]
        lagged_df.attrs["transformations"] = "raw, imputed, mq_freq, blocked, stationary, filtered, lagged"
        # lagged_df.attrs["transformations"] = "raw, imputed, mq_freq, stationary, blocked, filtered, lagged"
        self.lagged_df = lagged_df
        return lagged_df
    
    def to_zero_lagged_df(self, dataset=None, y_var=None, lags=0, y_var_lags=1):
        """
        Add lagged columns for each variable, placing them directly after their source column.

        Parameters:
            dataset (pd.DataFrame): Input dataframe.
            y_var (str): Name of the dependent variable.
            y_var_lags (int): Number of lags for the y_var.
            lags (int): Number of lags for all other variables.

        Returns:
            pd.DataFrame: DataFrame with lagged features.
        """
        if dataset is None or dataset.empty:
            logger.warning(f"{self.name}: No dataset provided.")
            return pd.DataFrame()

        self._validate_df(
            dataset,
            expected_value="raw, imputed, mq_freq, blocked, stationary, filtered",
            attr_key="transformations"
        )

        # self._validate_df(
        #     dataset,
        #     expected_value="raw, imputed, mq_freq, stationary, blocked, filtered",
        #     attr_key="transformations"
        # )

        if y_var not in dataset.columns:
            logger.warning(f"{self.name}: y_var '{y_var}' not found in dataset.")
            return dataset.copy()

        y_lags_final = max(y_var_lags, lags)
        lagged_df = dataset.copy()
        ordered_cols = []

        for col in dataset.columns:
            ordered_cols.append(col)

            # Determine how many lags to create
            num_lags = y_lags_final if col == y_var else lags

            for lag in range(1, num_lags + 1):
                lagged_col = f"{col}_lag{lag}"
                lagged_df[lagged_col] = lagged_df[col].shift(lag)
                ordered_cols.append(lagged_col)
            logger.info(f"{self.name}: Created {num_lags} lags for '{col}'.")

        # Reorder columns to insert lagged ones after their base
        lagged_df = lagged_df[ordered_cols]

        lagged_df.attrs["transformations"] = "raw, imputed, mq_freq, blocked, stationary, filtered, lagged"
        # lagged_df.attrs["transformations"] = "raw, imputed, mq_freq, stationary, blocked, filtered, lagged" 
        self.lagged_df = lagged_df

        return lagged_df
    
    
    def _plan_needed_lags(self, dataset, y_var, umidas_model_lags):
        """
        Decide:
          - needed_raw_lags: { meta_name: N } (max _lagN actually referenced by *feasible* layouts)
          - chosen_layouts: { meta_name: { layout_name: tokens[] } } (layouts feasible at global lag depth)

        Also returns the layout dicts so the caller can reuse them.
        """
        me_base_layouts = {
            "m3_period": ['m3', 'm2', 'm1', 'm3_lag1', 'm2_lag1', 'm1_lag1',
                          'm3_lag2', 'm2_lag2', 'm1_lag2', 'm3_lag3', 'm2_lag3', 'm1_lag3'],
            "m2_period": ['m2', 'm1', 'm3_lag1', 'm2_lag1', 'm1_lag1',
                          'm3_lag2', 'm2_lag2', 'm1_lag2', 'm3_lag3', 'm2_lag3', 'm1_lag3', 'm3_lag4'],
            "m1_period": ['m1', 'm3_lag1', 'm2_lag1', 'm1_lag1',
                          'm3_lag2', 'm2_lag2', 'm1_lag2', 'm3_lag3', 'm2_lag3', 'm1_lag3', 'm3_lag4', 'm2_lag4'],
        }
        me_ext_layouts = {
            "m3_period_lag1": ['m3_lag1','m2_lag1','m1_lag1','m3_lag2','m2_lag2','m1_lag2','m3_lag3','m2_lag3','m1_lag3','m3_lag4','m2_lag4','m1_lag4'],
            "m2_period_lag1": ['m2_lag1','m1_lag1','m3_lag2','m2_lag2','m1_lag2','m3_lag3','m2_lag3','m1_lag3','m3_lag4','m2_lag4','m1_lag4','m3_lag5'],
            "m1_period_lag1": ['m1_lag1','m3_lag2','m2_lag2','m1_lag2','m3_lag3','m2_lag3','m1_lag3','m3_lag4','m2_lag4','m1_lag4','m3_lag5','m2_lag5'],

            "m3_period_lag2": ['m3_lag2','m2_lag2','m1_lag2','m3_lag3','m2_lag3','m1_lag3','m3_lag4','m2_lag4','m1_lag4','m3_lag5','m2_lag5','m1_lag5'],
            "m2_period_lag2": ['m2_lag2','m1_lag2','m3_lag3','m2_lag3','m1_lag3','m3_lag4','m2_lag4','m1_lag4','m3_lag5','m2_lag5','m1_lag5','m3_lag6'],
            "m1_period_lag2": ['m1_lag2','m3_lag3','m2_lag3','m1_lag3','m3_lag4','m2_lag4','m1_lag4','m3_lag5','m2_lag5','m1_lag5','m3_lag6','m2_lag6'],

            "m3_period_lag3": ['m3_lag3','m2_lag3','m1_lag3','m3_lag4','m2_lag4','m1_lag4','m3_lag5','m2_lag5','m1_lag5','m3_lag6','m2_lag6','m1_lag6'],
            "m2_period_lag3": ['m2_lag3','m1_lag3','m3_lag4','m2_lag4','m1_lag4','m3_lag5','m2_lag5','m1_lag5','m3_lag6','m2_lag6','m1_lag6','m3_lag7'],
            "m1_period_lag3": ['m1_lag3','m3_lag4','m2_lag4','m1_lag4','m3_lag5','m2_lag5','m1_lag5','m3_lag6','m2_lag6','m1_lag6','m3_lag7','m2_lag7'],

            "m3_period_lag4": ['m3_lag4','m2_lag4','m1_lag4','m3_lag5','m2_lag5','m1_lag5','m3_lag6','m2_lag6','m1_lag6','m3_lag7','m2_lag7','m1_lag7'],
            "m2_period_lag4": ['m2_lag4','m1_lag4','m3_lag5','m2_lag5','m1_lag5','m3_lag6','m2_lag6','m1_lag6','m3_lag7','m2_lag7','m1_lag7','m3_lag8'],
            "m1_period_lag4": ['m1_lag4','m3_lag5','m2_lag5','m1_lag5','m3_lag6','m2_lag6','m1_lag6','m3_lag7','m2_lag7','m1_lag7','m3_lag8','m2_lag8'],
        }
        qe_layouts = {
            "q_period":      ['q', 'q_lag1', 'q_lag2', 'q_lag3'],
            "q_period_lag1": ['q_lag1', 'q_lag2', 'q_lag3', 'q_lag4'],
            "q_period_lag2": ['q_lag2', 'q_lag3', 'q_lag4', 'q_lag5'],
            "q_period_lag3": ['q_lag3', 'q_lag4', 'q_lag5', 'q_lag6'],
            "q_period_lag4": ['q_lag4', 'q_lag5', 'q_lag6', 'q_lag7'],
        }

        def max_lag_in(tokens):
            m = 0
            for t in tokens:
                if "_lag" in t:
                    m = max(m, int(t.split("_lag")[1]))
            return m

        needed_raw_lags = {}
        chosen_layouts = {}
        seen = set()

        for base_col in dataset.columns:
            if base_col == y_var or base_col.startswith(f"{y_var}_lag"):
                continue

            meta_name = Checks.get_series_meta_name(base_col)
            if meta_name in seen:
                continue
            seen.add(meta_name)

            meta = self.meta.get(meta_name)
            if meta is None:
                logger.warning(f"{self.name}: No metadata for '{meta_name}'. Skipping.")
                continue

            freq = meta.freq
            chosen_layouts[meta_name] = {}

            if freq in {"ME", "D"}:
                # base periods (need up to lag4)
                for k, tokens in me_base_layouts.items():
                    if max_lag_in(tokens) <= umidas_model_lags:
                        chosen_layouts[meta_name][k] = tokens
                # extended periods
                for k, tokens in me_ext_layouts.items():
                    if max_lag_in(tokens) <= umidas_model_lags:
                        chosen_layouts[meta_name][k] = tokens
            elif freq == "QE":
                for k, tokens in qe_layouts.items():
                    if max_lag_in(tokens) <= umidas_model_lags:
                        chosen_layouts[meta_name][k] = tokens

            # per-series max raw lag actually needed
            max_needed = 0
            for tokens in chosen_layouts[meta_name].values():
                max_needed = max(max_needed, max_lag_in(tokens))
            needed_raw_lags[meta_name] = max_needed

        return needed_raw_lags, chosen_layouts, me_base_layouts, me_ext_layouts, qe_layouts

    def _to_model_lagged_df(self, dataset, y_var, y_var_lags, series_lag_plan):
        """
        Build a lagged dataframe for model construction that includes:
          - y_var lags up to y_var_lags
          - per meta series, lags up to series_lag_plan[meta_name] (applies to *all* its columns)

        Columns are placed right after each base column.
        """
        lagged_df = dataset.copy()
        ordered_cols = []

        for col in dataset.columns:
            ordered_cols.append(col)

            if col == y_var:
                depth = max(0, int(y_var_lags))
            else:
                meta_name = Checks.get_series_meta_name(col)
                depth = int(series_lag_plan.get(meta_name, 0))

            for k in range(1, depth + 1):
                lag_col = f"{col}_lag{k}"
                lagged_df[lag_col] = lagged_df[col].shift(k)
                ordered_cols.append(lag_col)

            logger.info(f"{self.name}: Created {depth} lags for '{col}' (model).")

        lagged_df = lagged_df[ordered_cols]
        lagged_df.attrs["transformations"] = "raw, imputed, mq_freq, blocked, stationary, filtered, lagged_model"
        return lagged_df
 


























 
    # def to_test_lagged_df(self, dataset=None, y_var=None, lags=0, y_var_lags=1):
    #     """
    #     Add lagged columns for each variable, placing them directly after their source column.

    #     Parameters:
    #         dataset (pd.DataFrame): Input dataframe.
    #         y_var (str): Name of the dependent variable.
    #         y_var_lags (int): Number of lags for the y_var.
    #         lags (int): Number of lags for all other variables.

    #     Returns:
    #         pd.DataFrame: DataFrame with lagged features.
    #     """
    #     if dataset is None or dataset.empty:
    #         logger.warning(f"{self.name}: No dataset provided.")
    #         return pd.DataFrame()

    #     self._validate_df(
    #         dataset,
    #         expected_value="raw, imputed, mq_freq, blocked, sampled",
    #         attr_key="transformations"
    #     )

    #     if y_var not in dataset.columns:
    #         logger.warning(f"{self.name}: y_var '{y_var}' not found in dataset.")
    #         return dataset.copy()

    #     y_lags_final = max(y_var_lags, lags)
    #     lagged_df = dataset.copy()
    #     ordered_cols = []

    #     for col in dataset.columns:
    #         ordered_cols.append(col)

    #         # Determine how many lags to create
    #         num_lags = y_lags_final if col == y_var else lags

    #         for lag in range(1, num_lags + 1):
    #             lagged_col = f"{col}_lag{lag}"
    #             lagged_df[lagged_col] = lagged_df[col].shift(lag)
    #             ordered_cols.append(lagged_col)
    #         logger.info(f"{self.name}: Created {num_lags} lags for '{col}'.")

    #     # Reorder columns to insert lagged ones after their base
    #     lagged_df = lagged_df[ordered_cols]

    #     lagged_df.attrs["transformations"] = "raw, imputed, mq_freq, blocked, sampled, lagged"
        
    #     self.lagged_df = lagged_df

    #     return lagged_df