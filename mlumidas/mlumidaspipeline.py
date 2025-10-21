import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from collections import OrderedDict, defaultdict
import time
from tqdm import tqdm
from loguru import logger
from typing import List, Dict, Any, Optional, Set

from utils.getdata import _load_object, list_filepaths_in_dir, extract_period, _save_xlsx, _save_object

from mlumidas.mixins.mlumidas import MLUMidasMixin # NOTE: Change back to without latest!! Did
from mlumidas.mixins.mlumidasoutput import MLUMidasOutputMixin
from mlumidas.mixins.mlumidascache import MLUMidasCacheMixin
from mlumidas.mixins.mlumidassavingplots import MLUMidasSavingPlotsMixin
from mlumidas.mixins.mlumidassavingtables import MLUMidasSavingTablesMixin

class MLUMidasPipeline(MLUMidasMixin, MLUMidasCacheMixin, MLUMidasOutputMixin, MLUMidasSavingPlotsMixin, MLUMidasSavingTablesMixin):
    def __init__(
        self,
        file_path=str,
        varselection_method=str,
        fwr_idx_dict=pd.DataFrame(),
        release_periods_dict=pd.DataFrame(),
        y_var=str,

        full_sample_df=pd.DataFrame(),
        alpha=float,
        tcv_splits=int,
        test_size=int,
        gap=int,
        max_train_size=int,
        cv=int,
        alphas=int,
        max_iter=int,
        random_state=int,
        with_mean=bool,
        with_std=bool,
        fit_intercept=bool,
        selection_rule=str,
        se_factor=float,
        threshold_divisor=float,
        coef_tol=float,
        k_indicators=int,
        lambda_fix=float,

        series_model_dataframes=pd.DataFrame(),
        release_latest_block_dict=dict(),
        meta=OrderedDict(),
        umidas_model_lags=int,
        start_date=pd.Timestamp,
        end_date=pd.Timestamp,
        remove_non_stat_fwrs=bool,
        confidence=float,

        window_quarters=int,

        spec_name=str,
        save_q_plots=bool,
        group_type=str,
        quarter_plots: Optional[List[pd.Timestamp]] = None,

        run_cache_only=bool
    ):

        # ------------------------------------------------------ #
        # Inputs for MLUMidasPipeline -------------------------- #
        # ------------------------------------------------------ #
        # ----- Cache orchestration -----------------------------#

        self.run_cache_only = run_cache_only

        # ----- Input paths -------------------------------------#
        self.file_path = file_path
        self.file_path_modelcache = f"{self.file_path}/cache/mlumidascache/"

        # --------------- Step 2.1 ------------------------------#
        self.meta = meta
        self.start_date = start_date
        self.end_date = end_date
        self.y_var = y_var

        # --------------- Step 2.2 ------------------------------#
        self.varselection_method = varselection_method
        self.fwr_idx_dict = fwr_idx_dict
    
        # --------------- Varselect Input parameters ------------#
        self.full_sample_df = full_sample_df
        self.release_periods_dict = release_periods_dict

        self.alpha = alpha
        self.alphas = alphas
        self.max_iter = max_iter
        self.random_state = random_state
        self.with_mean = with_mean
        self.with_std = with_std
        self.fit_intercept = fit_intercept
        self.selection_rule = selection_rule
        self.se_factor = se_factor
        self.threshold_divisor = threshold_divisor
        self.coef_tol = coef_tol
        self.k_indicators = k_indicators

        # ------------------ pyeacv -----------------------------#
        self.cv = cv

        # ------------------ pyeatscv ---------------------------#
        self.tcv_splits = tcv_splits
        self.test_size = test_size
        self.gap = gap
        self.max_train_size = max_train_size

        # ------------------ pyen -------------------------------#
        self.lambda_fix = lambda_fix

        # --------------- UMIDAS Input parameters ---------------#
        self.umidas_model_lags = umidas_model_lags
        self.release_latest_block_dict = release_latest_block_dict
        self.series_model_dataframes = series_model_dataframes
        self.remove_non_stat_fwrs = remove_non_stat_fwrs
        self.confidence = confidence
        self.window_quarters = window_quarters

        # --------------- Step 2.3 ------------------------------#
        self.spec_name = spec_name
        self.save_q_plots = save_q_plots
        self.group_type = group_type
        self.quarter_plots = quarter_plots or []

        # ------------------------------------------------------ #
        # Outputs from MLUMidasPipeline ------------------------ #
        # ------------------------------------------------------ #

        self.model_cache = {}
        self.results_dict = {}

        self.oof_plots = {}
        self.oof_all_periods_plots = {}
        self.oof_single_quarter_plots = {}

        self.selected_vars_quarters_df_dict = {}
        self.selected_vars_quarters_periods_df_dict = {}

        self.file_path_output_plots = f"{self.file_path}/output/mlumidas/{self.spec_name}/plots"
        self.file_path_output_tables = f"{self.file_path}/output/mlumidas/{self.spec_name}/selected_tables"

    def process_mapping(self):

        if self.run_cache_only:
            # STEP 2.1 Compute model cache
            
            self.model_cache, top_level_key = self.load_or_compute_model_cache(
                umidas_model_lags=self.umidas_model_lags,
                file_path_modelcache=self.file_path_modelcache,
                start_date=self.start_date,
                end_date=self.end_date,
                y_var=self.y_var,
                fwr_idx_dict=self.fwr_idx_dict,
                series_model_dataframes=self.series_model_dataframes,
                meta=self.meta
            )
        else:
            # STEP 2.1 Compute model cache
            self.model_cache, top_level_key = self.load_or_compute_model_cache(
                umidas_model_lags=self.umidas_model_lags,
                file_path_modelcache=self.file_path_modelcache,
                start_date=self.start_date,
                end_date=self.end_date,
                y_var=self.y_var,
                fwr_idx_dict=self.fwr_idx_dict,
                series_model_dataframes=self.series_model_dataframes,
                meta=self.meta
            )

            self.mse_history = self.load_or_compute_mse_history(
                file_path_modelcache=self.file_path_modelcache,
                top_level_key=top_level_key,
                model_cache=self.model_cache,
            )

            # STEP 2.2. Run MLUMidas and get the results
            self.results_dict = self.get_results_dict(
                varselection_method=self.varselection_method,
                fwr_idx_dict=self.fwr_idx_dict,
                release_periods_dict=self.release_periods_dict,
                y_var=self.y_var,

                full_sample_df=self.full_sample_df,
                alpha=self.alpha,
                tcv_splits=self.tcv_splits,
                test_size=self.test_size,
                gap=self.gap,
                max_train_size=self.max_train_size,
                cv=self.cv,
                alphas=self.alphas,
                max_iter=self.max_iter,
                random_state=self.random_state,
                with_mean=self.with_mean,
                with_std=self.with_std,
                fit_intercept=self.fit_intercept,
                selection_rule=self.selection_rule,
                se_factor=self.se_factor,
                threshold_divisor=self.threshold_divisor,
                coef_tol=self.coef_tol,
                k_indicators=self.k_indicators,
                lambda_fix=self.lambda_fix,

                series_model_dataframes=self.series_model_dataframes,
                release_latest_block_dict=self.release_latest_block_dict,
                meta=self.meta,
                umidas_model_lags=self.umidas_model_lags,
                start_date=self.start_date,
                end_date=self.end_date,
                remove_non_stat_fwr=self.remove_non_stat_fwrs,
                confidence=self.confidence,

                model_cache=self.model_cache,

                mse_history=self.mse_history,
                window_quarters=self.window_quarters,
            )

            # STEP 2.3. Generate output
            self.oof_plots = self.get_oof_plots(
                results_dict=self.results_dict,
                title=self.spec_name
            )

            self.oof_all_periods_plots = self.get_oof_all_periods_plots(
                results_dict=self.results_dict,
                title=self.spec_name
            )

            self.oof_single_quarter_plots = self.get_oof_single_quarter_plots(
                self.results_dict, group_by=self.group_type, 
                title=self.spec_name, 
                quarter_plots=self.quarter_plots
            )

            self.selected_vars_quarters_df_dict = self.results_dict["varselect"]["selected_vars_quarters"]
            self.selected_vars_quarters_periods_df_dict = self.results_dict["varselect"]["selected_vars_quarters_periods"]

            # STEP 2.3. Save output
            self.save_plots(self.oof_plots, self.file_path_output_plots)
            self.save_plots(self.oof_all_periods_plots, self.file_path_output_plots)
            if self.save_q_plots:
                self.save_plots(self.oof_single_quarter_plots, self.file_path_output_plots)

            self.save_selected_tables(self.selected_vars_quarters_df_dict, self.file_path_output_tables, self.spec_name)
            self.save_selected_tables(self.selected_vars_quarters_periods_df_dict, self.file_path_output_tables, self.spec_name)

    def run(self):
        self.process_mapping()
