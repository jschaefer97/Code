import logging
import pandas as pd
import datetime as dt   
from loguru import logger
from collections import OrderedDict
import os
import matplotlib.pyplot as plt

from utils.getdata import *
from mappings.periods import period_mappings

# from loguru import logger
# logger.remove()   

class NOWDataPipeline:
    """
    Pipeline for processing multiple NOWData mappings and combining the results.
    """
    def __init__(self, 
                    file_path = str, 
                    mapping_name = str, 
                    mapping_periods_name = str,
                    impute = True, 
                    impute_method="linear",
                    transform_all = str, 
                    confidence = float, 
                    start_date = pd.Timestamp, 
                    end_date = pd.Timestamp, 
                    dropvarlist = list, 
                    no_lags = str, 
                    umidas_model_lags = int, 
                    y_var = str,  
                    y_var_lags = int,
                    nowcast_start = pd.Timestamp
        ):

        # ------------------------------------------------------ #
        # Inputs for NOWDataPipeline --------------------------- #
        # ------------------------------------------------------ #

        # ----- Input paths -------------------------------------#
        self.file_path = file_path

        # ----- Input and output path ---------------------------#
        self.file_path_nowdata_object = f"{file_path}/dataset/obj_nowdata"

        # ----- Input parameters --------------------------------#
        # --------------- Step 1.0 ------------------------------#
        self.mapping_name = mapping_name

        # --------------- Step 1.1 ------------------------------#
        if mapping_periods_name not in period_mappings:
                raise ValueError(f"Unknown mapping name: {mapping_periods_name}")
        self.mapping_periods_name = mapping_periods_name
        self.mapping_periods = period_mappings[mapping_periods_name]

        # --------------- Step 1.2 ------------------------------#
        self.impute = impute
        self.impute_method = impute_method

        # --------------- Step 1.3 ------------------------------#

        # --------------- Step 1.4 ------------------------------#
        self.transform_all = transform_all
        self.confidence = confidence

        # --------------- Step 1.5 ------------------------------#
        self.start_date = start_date
        self.end_date = end_date
        self.dropvarlist = dropvarlist
        self.umidas_model_lags = umidas_model_lags
        self.y_var = y_var
        self.y_var_lags = y_var_lags    

        # --------------- Step 1.6 ------------------------------#
        # self.y_var = y_var
        # self.y_var_lags = y_var_lags  
        self.no_lags = no_lags

        # --------------- Step 1.7 ------------------------------#
        # self.start_date = start_date
        # self.end_date = end_date
        self.nowcast_start = nowcast_start 

        # --------------- Step 1.8 ------------------------------#
        # self.start_date = start_date
        # self.nowcast_start = nowcast_start 
        # self.end_date = end_date

        # --------------- Step 1.9 ------------------------------#

        # ------------------------------------------------------ #
        # Outputs from NOWDataPipeline ------------------------- #
        # ------------------------------------------------------ #

        # ----- Output paths
        self.file_path_blocked_df = f"{file_path}/dataset/csv_blocked_df"
        self.file_path_meta = f"{file_path}/dataset/xlsx_meta"
        self.file_path_train_varselect = f"{file_path}/dataset/csv_varselect/train"
        self.file_path_test_varselect = f"{file_path}/dataset/csv_varselect/test"

        # ----- Dictionaries ------------------------------------#
        self.raw_dfs = {}
        self.imp_dfs = {}
        self.mq_freq_dfs = {}
        self.sample_dfs = {}
        self.fwr_idx_dict = {}
        self.release_periods_dict = {}

        # ----- DataFrames --------------------------------------#
        self.blocked_df = pd.DataFrame()
        self.stat_df = pd.DataFrame()
        self.check_stationarity_df = pd.DataFrame()
        self.filtered_df = pd.DataFrame()
        self.lagged_df = pd.DataFrame()
        self.series_model_dataframes = {}
        self.full_sample_df = pd.DataFrame()
        self.in_sample_df = pd.DataFrame()  
        self.out_sample_df = pd.DataFrame()
        self.meta_df = pd.DataFrame()
        self.meta = OrderedDict()  

    def process_mapping(self):

        logger.info(f"-------------------------------------------------------------------------------------")
        logger.info(f"-------------------------------------------------------------------------------------")
        logger.info(f"-------------------------------------------------------------------------------------")
        logger.info(f"start_date={self.start_date}")
        logger.info(f"end_date={self.end_date}")
        logger.info(f"lags={self.umidas_model_lags}")
        logger.info(f"confidence={self.confidence}")
        logger.info(f"transform_all={self.transform_all}")
        logger.info(f"impute={self.impute}")
        logger.info(f"impute_method={self.impute_method}")
        logger.info(f"-------------------------------------------------------------------------------------")
        logger.info(f"-------------------------------------------------------------------------------------")
        logger.info(f"-------------------------------------------------------------------------------------")
        
        if self.umidas_model_lags < 4:
            logger.error(f"ERROR: UMidas Model length too short to construct the model dataframes. Chose a lag lenght > 4.")
            return
            
        # STEP 1.0: Load the Nowdataset from the mapping.

        self.NOWData = Getdata.mapping(self.file_path_nowdata_object, self.mapping_name)

        # STEP 1.1: Get raw_dfs, release periods and the release calendar plot

        self.NOWData.get_release_periods(mapping_periods=self.mapping_periods)
        self.raw_dfs = self.NOWData.to_raw_dfs()

        # STEP 1.2: Impute missing values

        self.imp_dfs = self.NOWData.to_imp_dfs(
            self.raw_dfs, 
            impute=self.impute, 
            impute_method=self.impute_method
        )
    
        # STEP 1.3: Bring daily series to monthly frequency and construct a blocked DataFrame

        self.mq_freq_dfs = self.NOWData.to_mq_freq_dfs(self.imp_dfs)
        self.blocked_df = self.NOWData.to_blocked_df(self.mq_freq_dfs)

        # STEP 1.4: Stationarize the blocked DataFrame

        self.stat_df = self.NOWData.to_stat_df(
            self.blocked_df, 
            transform_all=self.transform_all, 
            confidence=self.confidence,
            start_date=self.start_date, 
            end_date=self.nowcast_start # NOTE: Changed this! was end_date=self.end_date before
        )

        # STEP 1.5: Filter the DataFrame based on metadata and other criteria
                
        self.filtered_df = self.NOWData.to_filtered_df(
            self.stat_df,
            start_date=self.start_date,
            end_date=self.end_date,
            dropvarlist=self.dropvarlist,
            lags=self.umidas_model_lags, 
            umidas_model_lags=self.umidas_model_lags,
            y_var=self.y_var,
            y_var_lags=self.y_var_lags
        )

        # self.release_calendar_plot, ax = self.NOWData.get_release_calendar_plot(y_var=self.y_var, mapping_periods=self.mapping_periods) 

        # self.clean_calendar_plot, ax = self.NOWData.get_release_calendar_plot_clean(
        #     y_var=self.y_var,
        #     mapping_periods=self.mapping_periods,
        #     color_m1="#88B9EE",
        #     color_m2="#244A7F",
        #     color_m3="#9239AE",
        #     color_q="#D66B35",          # optional; used only if include_quarterly=True
        # )

        # try:
        #     self.release_calendar_plot.canvas.manager.set_window_title(f"Q2 Release Calendar — {self.y_var}")
        # except Exception:
        #     pass

        # plt.show(block=True)   
        # plt.close(self.release_calendar_plot)         

        # user_input = input(
        #     "Do you want to use this specification of release periods to run the pipeline? (yes/no) "
        # ).strip().lower()

        # if user_input not in ("yes", "y"):
        #     logger.info("Exiting as per user request.")
        #     return 


        # STEP 1.6: Construct lagged DataFrames

        self.series_model_dataframes = self.NOWData.get_model_dfs(
            self.filtered_df, 
            y_var=self.y_var, 
            umidas_model_lags=self.umidas_model_lags,
            y_var_lags=self.y_var_lags,
        )
        
        if self.no_lags == "nl_nc":
            self.lagged_df = self.NOWData.to_zero_lagged_df(
                self.filtered_df,
                y_var=self.y_var,
                lags=0,
                y_var_lags=self.y_var_lags,
            )

            self.release_periods_dict = self.NOWData.get_release_periods_dict_nc()
        elif self.no_lags == "nl_c":
            self.lagged_df = self.NOWData.to_zero_lagged_df(
                self.filtered_df,
                y_var=self.y_var,
                lags=0,
                y_var_lags=self.y_var_lags,
            )

            self.release_periods_dict = self.NOWData.get_release_periods_dict()

        elif self.no_lags == "l_c":    
            self.lagged_df = self.NOWData.to_lagged_df(
                self.filtered_df,
                y_var=self.y_var,
                lags=self.umidas_model_lags,
                y_var_lags=self.y_var_lags,
            )

            self.release_periods_dict = self.NOWData.get_release_periods_dict()

        else:
            logger.error(f"ERROR: no_lags parameter not recognized. Choose from 'nl_nc', 'nl_c', 'l_c'.")
            return

        # STEP 1.7: Construct sample DataFrames

        self.sample_dfs = self.NOWData.to_sample_dfs(
            self.lagged_df,
            start_date=self.start_date,
            end_date=self.end_date,
            nowcast_start=self.nowcast_start
        )

        self.full_sample_df = self.sample_dfs["Full-Sample"]
        self.in_sample_df = self.sample_dfs["In-Sample"]
        self.out_sample_df = self.sample_dfs["Out-of-Sample"]

        # STEP 1.8: Map the periods and the forward rolling window

        self.fwr_idx_dict = self.NOWData.get_fwr_idx_dict(
            dataset=self.full_sample_df,
            start_date=self.start_date,
            nowcast_start=self.nowcast_start,
            end_date=self.end_date
        )

        self.release_latest_block_dict = self.NOWData.get_release_latest_block_dict() # NOTE: Not used anymore, kept for now

        # STEP 1.9: Get the meta data DataFrame

        self.meta_df = self.NOWData.meta_df
        self.meta = self.NOWData.meta

    def run(self):

       self.process_mapping()







