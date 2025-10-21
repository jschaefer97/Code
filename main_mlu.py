# %%
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from pipeline.nowmlupipeline import NOWMLUPipeline  
from IPython.display import display
from loguru import logger
logger.remove() 

#%%
# ------------------------------------------------------------------------- #
# ------------- Run Full Pipeline ----------------------------------------- #
# ------------------------------------------------------------------------- #

# Only change these parameters
file_path = "C:/Users/johan/Desktop/Coding/Master Thesis/FU_Master_Thesis/Code"
pipelines_to_run = ["nowdata"] # "nowdata"
mapping_name = "IfoCast" 
mapping_periods_name = "3p_v2" # 2p_v0, 6p_v0, 4p_v0 4p_v1 2p_v1
y_var_short_name = "GDP_pyenCheck"

nowcast_start = pd.Timestamp("2019-03-31")
no_lags = "nl_nc" # "nl_nc", "nl_c", "l_c" 
varselection_method = "pyentscv" # "pyen" pyentscv pyadal no_selection
alpha = 1
lambda_calc_q2_2020 =  0.198   

# Q22020: EN02: 0.344, EN05: 0.150, EN08: 0.122, LASSO: 0.099
# Q32020: EN02: 0.476, EN05: 0.039, EN08: 0.027, LASSO: 0.022 








# FIXED parameters
# --- Data ------------------------------------------#
impute = True
impute_method = 'linear'
transform_all = ""
confidence = 0.05
start_date = pd.Timestamp("2002-06-30") # 1999-06-30
end_date = pd.Timestamp("2024-12-31") # 2025-06-30
dropvarlist = []
umidas_model_lags = 4                   # NOTE: Do not go below 2
y_var = "de_gdp_total_ca_cop_sa"
y_var_lags = 4

# --- Varselect -------------------------------------#
tcv_splits = 5                        # NOTE: higher than 5 not possible
test_size = 10                        # NOTE: higher that 10 not possible
gap = 0
max_train_size = 91
cv = 5
alphas = 500 
max_iter = 1000000
random_state = 42
with_mean = True
with_std = True
fit_intercept = True                    
selection_rule = "cv_min" # "pt", "cv_min", "cv_se", "cv_1se"
se_factor = 0.1                      # NOTE: higer than 0.25 already gives missings for the LASSO
threshold_divisor = 5
coef_tol = 0                         # NOTE: Always 0
k_indicators = 40
lambda_fix = lambda_calc_q2_2020
window_quarters = 4                  # NOTE: usually 4
save_q_plots = False
group_type = "category" # "category", "subcategory", "all"
quarter_plots = [
    pd.Timestamp("2020-03-31"), 
    pd.Timestamp("2020-06-30"), 
    pd.Timestamp("2020-09-30"),
    pd.Timestamp("2020-12-31"),
    pd.Timestamp("2022-03-31"),
    pd.Timestamp("2022-06-30"),
]
remove_non_stat_fwrs = False          

#%%

pipeNOWMLUMidas = NOWMLUPipeline(
    file_path=file_path,
    pipelines_to_run=pipelines_to_run,

    # NOWData
    mapping_name=mapping_name,
    mapping_periods_name=mapping_periods_name,
    impute=impute,
    impute_method=impute_method,
    transform_all=transform_all,
    confidence=confidence,
    start_date=start_date,
    end_date=end_date,
    dropvarlist=dropvarlist,
    umidas_model_lags=umidas_model_lags,
    y_var=y_var,
    y_var_short_name=y_var_short_name,
    y_var_lags=y_var_lags,
    nowcast_start=nowcast_start,
    no_lags=no_lags,

    # VarSelect
    varselection_method=varselection_method,
    alpha=alpha,
    tcv_splits=tcv_splits,
    test_size=test_size,
    gap=gap,
    max_train_size=max_train_size,
    cv=cv,
    alphas=alphas,
    max_iter=max_iter,
    random_state=random_state,
    with_mean=with_mean,
    with_std=with_std,
    fit_intercept=fit_intercept,
    selection_rule=selection_rule,
    se_factor=se_factor,
    threshold_divisor=threshold_divisor,
    coef_tol=coef_tol,
    k_indicators=k_indicators,
    save_q_plots=save_q_plots,
    group_type=group_type,
    remove_non_stat_fwrs=remove_non_stat_fwrs,
    quarter_plots=quarter_plots,
    window_quarters=window_quarters,
    lambda_fix=lambda_fix,
)

pipeNOWMLUMidas.run()

# %%

pool = "mseweight"          # or "avg"
branch = "selected"     
criterion = "bic"  

#%%
NOWData = pipeNOWMLUMidas.pipeNOWData

meta_df = NOWData.meta_df
fwr_idx_dict = NOWData.fwr_idx_dict
full_sample_df = NOWData.full_sample_df
series_model_dataframes = NOWData.series_model_dataframes
release_periods_dict = NOWData.release_periods_dict

results_dict = pipeNOWMLUMidas.results_dict

oof_all_periods_plots = pipeNOWMLUMidas.oof_all_periods_plots

fig_all = oof_all_periods_plots[pool][branch][criterion]
display(fig_all)

#%%


















