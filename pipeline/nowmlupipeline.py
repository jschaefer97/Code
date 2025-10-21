from collections import OrderedDict
from typing import List, Dict, Any, Optional, Set
import pandas as pd
import os
import matplotlib.pyplot as plt
from loguru import logger

from utils.utils import get_formatted_date_spec

from pipeline.mixins.caching import CachingMixin
from pipeline.mixins.saving import SavingMixin
from pipeline.mixins.summary import SummaryMixin

from data.nowdatapipeline import NOWDataPipeline
from mlumidas.mlumidaspipeline import MLUMidasPipeline

from utils.getdata import _save_xlsx, _save_object


class NOWMLUPipeline(CachingMixin, SavingMixin, SummaryMixin):
    """
    Orchestrator with per-stage behavior:
      - ONLY the NOWDATA STAGE is cached.
        • If 'nowdata' is not explicitly requested, it will be loaded from cache if present;
          otherwise it runs once and is cached.
        • The cache stores both key outputs AND the NOWDataPipeline instance itself, so
          self.pipeNOWData is available even when loaded from cache.
      - VARSELECT and MODEL STAGES ALWAYS RUN (no caching).
      - Each stage runs at most once per process (in-memory guards).
    """

    def __init__(
        self,
        file_path: str,
        pipelines_to_run: List[str],

        # NOWData
        mapping_name: str,
        mapping_periods_name: Dict[str, Any],
        impute: bool,
        impute_method: str,
        transform_all: str,
        confidence: float,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        dropvarlist: list,
        umidas_model_lags: int,
        y_var: str,
        y_var_short_name: str,
        y_var_lags: int,
        nowcast_start: pd.Timestamp,
        no_lags: str,

        # MLU Midas VarSelect
        varselection_method: Optional[str],
        alpha: float,
        tcv_splits: int,
        test_size: int,
        gap: int,
        max_train_size: int,
        cv: int,
        alphas: int,
        max_iter: int,
        random_state: int,
        with_mean: bool,
        with_std: bool,
        fit_intercept: bool,
        selection_rule: str,
        se_factor: float,
        threshold_divisor: float,
        remove_non_stat_fwrs: bool,
        coef_tol: float,
        k_indicators: int,
        save_q_plots: bool,
        group_type: str,
        quarter_plots: Optional[List[pd.Timestamp]] = None,
        window_quarters=int,
        lambda_fix=float,

        run_cache_only: bool = False,
    ):
        # ------------------------------------------------------ #
        # Outputs/Input Paths ---------------------------------- #
        # ------------------------------------------------------ #
        self.file_path = file_path
        self.file_path_pipelinecache = f"{file_path}/cache/mlupipelinecache"

        # ---- For naming -------------------------------------- #
        self.y_var_short_name = y_var_short_name

        # ------------------------------------------------------ #
        # Pipelines to run ------------------------------------- #
        # ------------------------------------------------------ #
        # Only 'nowdata' is meaningful for caching control.
        valid: Set[str] = {"nowdata"} # NOTE: For now only nowdata. Extend for creating more caches later. 
        self.pipelines_to_run: Set[str] = set(pipelines_to_run or [])
        unknown = self.pipelines_to_run - valid
        if unknown:
            raise ValueError(f"Unknown pipelines_to_run entries: {sorted(unknown)}. Valid: {sorted(valid)}")

        # ------------------------------------------------------ #
        # NOWData params --------------------------------------- #
        # ------------------------------------------------------ #
        self.mapping_name = mapping_name
        self.mapping_periods_name = mapping_periods_name
        self.impute = impute
        self.impute_method = impute_method
        self.transform_all = transform_all
        self.confidence = confidence
        self.start_date = start_date
        self.end_date = end_date
        self.dropvarlist = dropvarlist
        self.umidas_model_lags = umidas_model_lags
        self.y_var = y_var
        self.y_var_lags = y_var_lags
        self.nowcast_start = nowcast_start
        self.no_lags = no_lags

        # ------------------------------------------------------ #
        # VarSelect params ------------------------------------- #
        # ------------------------------------------------------ #
        self.varselection_method = varselection_method
        self.alpha = alpha
        self.tcv_splits = tcv_splits
        self.test_size = test_size
        self.gap = gap
        self.max_train_size = max_train_size
        self.cv = cv
        self.alphas = alphas
        self.max_iter = max_iter
        self.random_state = random_state
        self.with_mean = with_mean
        self.with_std = with_std
        self.fit_intercept = fit_intercept
        self.selection_rule = selection_rule
        self.se_factor = se_factor
        self.k_indicators = k_indicators
        self.threshold_divisor = threshold_divisor
        self.remove_non_stat_fwrs = remove_non_stat_fwrs
        self.window_quarters = window_quarters  
        # self.confidence = confidence
        self.coef_tol = coef_tol
        self.save_q_plots = save_q_plots
        self.group_type = group_type
        self.quarter_plots = quarter_plots or []
        self.lambda_fix = lambda_fix

        # ------------------------------------------------------ #
        # Stage objects (kept) --------------------------------- #
        # ------------------------------------------------------ #
        self.pipeNOWData: Optional[NOWDataPipeline] = None
        self.pipeMLUMidas: Optional[MLUMidasPipeline] = None

        # ------------------------------------------------------ #
        # Cross-stage artifacts -------------------------------- #
        # ------------------------------------------------------ #
        # ---- NOWData -> NOWVarSelect ------------------------- #
        self.run_cache_only = run_cache_only # Whether to only load from cache or run the full pipeline 
        self.release_periods_dict: Optional[Dict[str, Any]] = None
        self.full_sample_df: Optional[pd.DataFrame] = None
        self.series_model_dataframes: Optional[Dict[str, Any]] = None
        self.release_latest_block_dict: Optional[Dict[str, Any]] = None
        self.meta: Optional[OrderedDict] = None
        self.fwr_idx_dict: Optional[Dict[str, Any]] = None

        # ------------------------------------------------------ #
        # Per-process guards ----------------------------------- #
        # ------------------------------------------------------ #
        self._done = {
            "nowdata": False,
            "varselect": False,
        }

        # ------------------------------------------------------ #
        # Outputs ---------------------------------------------- #
        # ------------------------------------------------------ #
        formatted_start_date = get_formatted_date_spec(self.start_date)
        formatted_end_date   = get_formatted_date_spec(self.end_date)

        if self.varselection_method in ["pyentscv"]:
            self.spec_name = f"{self.mapping_name}_{self.mapping_periods_name}_{formatted_start_date}_{formatted_end_date}_{self.y_var_short_name}_{self.varselection_method}_tcv{self.tcv_splits}on{self.test_size}_a{self.alpha}_qw{self.window_quarters}"
            if self.selection_rule == "cv_se":
                self.spec_name += f"{self.se_factor}"
            if self.coef_tol > 0:
                self.spec_name += f"_ct{self.coef_tol}"
            if self.selection_rule == "pt":
                self.spec_name += f"_td{self.threshold_divisor}"
            if self.no_lags:
                self.spec_name += f"_{self.no_lags}"
            if self.selection_rule == "k_ic":
                self.spec_name += f"{self.k_indicators}"

            self.spec_name_short = f"{self.varselection_method}_a{self.alpha}"

        elif self.varselection_method == "no_selection":
            self.spec_name = f"{self.mapping_name}_{self.mapping_periods_name}_{formatted_start_date}_{formatted_end_date}_{self.y_var_short_name}_nsel_qw{self.window_quarters}"
            if self.no_lags:
                self.spec_name += f"_{self.no_lags}"
            
            self.spec_name_short = f"{self.varselection_method}"

        elif self.varselection_method in ["pyen"]:
            self.spec_name = f"{self.mapping_name}_{self.mapping_periods_name}_{formatted_start_date}_{formatted_end_date}_{self.y_var_short_name}_{self.varselection_method}_a{self.alpha}_lam{self.lambda_fix}_qw{self.window_quarters}"
            if self.selection_rule == "cv_se":
                self.spec_name += f"{self.se_factor}"
            if self.coef_tol > 0:
                self.spec_name += f"_ct{self.coef_tol}"
            if self.selection_rule == "pt":
                self.spec_name += f"_td{self.threshold_divisor}"
            if self.no_lags:
                self.spec_name += f"_{self.no_lags}"
            if self.selection_rule == "k_ic":
                self.spec_name += f"{self.k_indicators}"

            self.spec_name_short = f"{self.varselection_method}_a{self.alpha}_l{self.lambda_fix}"

    
        # elif self.varselection_method in ["pyadal"]:
        #     self.spec_name = f"{self.mapping_name}_{self.mapping_periods_name}_{formatted_start_date}_{formatted_end_date}_{self.y_var_short_name}_{self.umidas_model_lags}lags_{self.varselection_method}_qw{self.window_quarters}"

        # elif self.varselection_method in ["pyhardt"]:
        #     self.spec_name = f"{self.mapping_name}_{self.mapping_periods_name}_{formatted_start_date}_{formatted_end_date}_{self.y_var_short_name}_hardt_tr_qw{self.window_quarters}"
        #     if self.k_indicators > 0:
        #         self.spec_name += f"_k_ic{self.k_indicators}"
        
        # if self.varselection_method in ["pyencv"]:
        #     self.spec_name = f"{self.mapping_name}_{self.mapping_periods_name}_{formatted_start_date}_{formatted_end_date}_{self.y_var_short_name}_{self.umidas_model_lags}lags_{self.varselection_method}_a{self.alpha}_qw{self.window_quarters}_{self.selection_rule}"
        #     if self.selection_rule == "cv_se":
        #         self.spec_name += f"{self.se_factor}"
        #     if self.coef_tol > 0:
        #         self.spec_name += f"_ct{self.coef_tol}"
        #     if self.selection_rule == "pt":
        #         self.spec_name += f"_td{self.threshold_divisor}"
        #     if self.no_lags:
        #         self.spec_name += f"_{self.no_lags}"
        #     if self.selection_rule == "k_ic":
        #         self.spec_name += f"{self.k_indicators}"

        self.file_path_output = f"{file_path}/output/mlumidas/{self.spec_name}"
        self.file_path_results = f"{file_path}/output/results/{self.spec_name}"
        self.file_path_results_dfs = f"{file_path}/output/results/{self.spec_name}/dfs"

        logger.add(f"{self.file_path_output}/log_{self.spec_name}.txt", rotation="10 MB")

        self.results_dict = {}
        self.oof_plots = {}
        self.oof_all_periods_plots = {}
        self.oof_single_quarter_plots = {}
        self.selected_vars_quarters_df_dict = {}
        self.selected_vars_quarters_periods_df_dict = {}

    def _stage_nowdata(self) -> None:
        if self._done["nowdata"]:
            return

        stage = "nowdata"
        explicit_run = stage in self.pipelines_to_run

        if not explicit_run:
            cached = self._load_stage_cache(stage)
            if cached is not None:
                # Restore pipeline instance AND its outputs
                self.pipeNOWData = cached.get("pipeNOWData")

                self.release_periods_dict = cached.get("release_periods_dict")
                self.full_sample_df = cached.get("full_sample_df")
                self.series_model_dataframes = cached.get("series_model_dataframes")
                self.release_latest_block_dict = cached.get("release_latest_block_dict")
                self.meta = cached.get("meta")
                self.meta_df = cached.get("meta_df")
                self.fwr_idx_dict = cached.get("fwr_idx_dict")

                self._done["nowdata"] = True
                return
            # else: fall through to run and create cache

        # RUN once (either explicitly or to populate cache)

        self.pipeNOWData = NOWDataPipeline(
            file_path=self.file_path,
            mapping_name=self.mapping_name,
            mapping_periods_name=self.mapping_periods_name,
            impute=self.impute,
            impute_method=self.impute_method,
            transform_all=self.transform_all,
            confidence=self.confidence,
            start_date=self.start_date,
            end_date=self.end_date,
            dropvarlist=self.dropvarlist,
            no_lags=self.no_lags,
            umidas_model_lags=self.umidas_model_lags,
            y_var=self.y_var,
            y_var_lags=self.y_var_lags,
            nowcast_start=self.nowcast_start
        )
        self._run_stage_obj(self.pipeNOWData)

        # Wire outputs
        self.release_periods_dict = getattr(self.pipeNOWData, "release_periods_dict", None)
        self.full_sample_df = getattr(self.pipeNOWData, "full_sample_df", None)
        self.series_model_dataframes = getattr(self.pipeNOWData, "series_model_dataframes", None)
        self.release_latest_block_dict = getattr(self.pipeNOWData, "release_latest_block_dict", None)
        self.meta = getattr(self.pipeNOWData, "meta", None)
        self.meta_df = getattr(self.pipeNOWData, "meta_df", None)
        self.fwr_idx_dict = getattr(self.pipeNOWData, "fwr_idx_dict", None)

        # Cache the instance + outputs
        self._save_stage_cache(stage, {
            "pipeNOWData": self.pipeNOWData,  # cache the instance itself
            "release_periods_dict": self.release_periods_dict,
            "full_sample_df": self.full_sample_df,
            "series_model_dataframes": self.series_model_dataframes,
            "release_latest_block_dict": self.release_latest_block_dict,
            "meta": self.meta,
            "fwr_idx_dict": self.fwr_idx_dict,
        })
        self._done["nowdata"] = True

    def _stage_varselect(self) -> None:
        if self._done["varselect"]:
            return

        # Ensure dependency exists (load/run nowdata if needed)
        self._stage_nowdata()

        # Optional guard if a method is required by implementation
        if not self.varselection_method:
            raise RuntimeError(
                "VarSelect stage requires `varselection_method` to be provided."
            )

        # ALWAYS RUN, NO CACHING
        self.pipeMLUMidas = MLUMidasPipeline(
            file_path=self.file_path,
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

            series_model_dataframes=self.series_model_dataframes,
            release_latest_block_dict=self.release_latest_block_dict,
            meta=self.meta,
            umidas_model_lags=self.umidas_model_lags,
            start_date=self.start_date,
            end_date=self.end_date,
            confidence=self.confidence,
            remove_non_stat_fwrs=self.remove_non_stat_fwrs,
            window_quarters=self.window_quarters,
            lambda_fix=self.lambda_fix,

            spec_name=self.spec_name,
            save_q_plots=self.save_q_plots,
            group_type=self.group_type,
            quarter_plots=self.quarter_plots,

            run_cache_only=self.run_cache_only
        )
        self._run_stage_obj(self.pipeMLUMidas)

        if not self.run_cache_only:
            # Pull outputs into orchestrator
            self.results_dict = getattr(self.pipeMLUMidas, "results_dict", None)
            self.oof_plots = getattr(self.pipeMLUMidas, "oof_plots", None)
            self.oof_all_periods_plots = getattr(self.pipeMLUMidas, "oof_all_periods_plots", None)
            self.oof_single_quarter_plots = getattr(self.pipeMLUMidas, "oof_single_quarter_plots", None)
            self.selected_vars_quarters_df_dict = getattr(self.pipeMLUMidas, "selected_vars_quarters_df_dict", None)
            self.selected_vars_quarters_periods_df_dict = getattr(self.pipeMLUMidas, "selected_vars_quarters_periods_df_dict", None)
            self._done["varselect"] = True

    def process_mapping(self) -> None:
        """
        Single-pass orchestration:
        - 'nowdata' uses cache (and stores/restores the pipeline instance too).
        - 'varselect' and 'model' ALWAYS RUN and are never cached.
        - Each stage guarded to run at most once in this process.
        """
        self._stage_nowdata()
        self._stage_varselect()
        
        if not self.run_cache_only:
            self.get_spec_summary(
                results_dict=self.results_dict,
                spec_name=self.spec_name,
                mapping_periods_name=self.mapping_periods_name,
                mapping_name=self.mapping_name,
                impute=self.impute,
                impute_method=self.impute_method,
                transform_all=self.transform_all,
                confidence=self.confidence,
                start_date=self.start_date,
                end_date=self.end_date,
                dropvarlist=self.dropvarlist,
                no_lags=self.no_lags,
                umidas_model_lags=self.umidas_model_lags,
                y_var=self.y_var,
                y_var_lags=self.y_var_lags,
                y_var_short_name=self.y_var_short_name,
                nowcast_start=self.nowcast_start,
                varselection_method=self.varselection_method,
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
                coef_tol=self.coef_tol,
                selection_rule=self.selection_rule,
                se_factor=self.se_factor,
                threshold_divisor=self.threshold_divisor,
                output_path=self.file_path_output, 
                window_quarters=self.window_quarters,
            )

            _save_xlsx(self.meta_df, self.file_path_results, f"MetaData_{self.spec_name_short}")
                    
            weights = ["periods_mseweight", "periods_avg"]
            for weight in weights:
                model_results = self.results_dict["model"][weight]["selected"]["bic"]
                for period in model_results.keys():
                    period_model_results = model_results[period]
                    _save_xlsx(period_model_results, self.file_path_results_dfs, f"df_{period}_{weight}_{self.spec_name_short}")

            _save_object(self.meta_df, self.file_path_results, f"meta_df_{self.spec_name}.pkl")
            _save_object(self.full_sample_df, self.file_path_results, f"full_sample_df_{self.spec_name}.pkl")
            _save_object(self.release_periods_dict, self.file_path_results, f"release_periods_dict_{self.spec_name}.pkl")
            _save_object(self.results_dict, self.file_path_results, f"results_dict_{self.spec_name}.pkl")
    
    def run(self) -> None:
        self.process_mapping()
