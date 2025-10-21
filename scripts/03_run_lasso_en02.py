# %%
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from pipeline.nowmlupipeline import NOWMLUPipeline  
from loguru import logger
logger.remove() 

from main import FILE_PATH

#%%
# ------------------------------------------------------------------------- #
# ------------- LASSO (alpha = 1) with Q32020 en02 lambda ----------------- #
# ------------------------------------------------------------------------- #

# Only change these parameters
file_path = FILE_PATH
pipelines_to_run = ["nowdata"] # "nowdata"
mapping_name = "NDv5" 
mapping_periods_name = "3p_v2" # 2p_v0, 6p_v0, 4p_v0 4p_v1 2p_v1
y_var_short_name = "GDP"

nowcast_start = pd.Timestamp("2019-03-31")
no_lags = "nl_nc" # "nl_nc", "nl_c", "l_c" 
varselection_method = "pyen" # "pyen" pyentscv pyadal no_selection
alpha = 1 
lambda_calc_q2_2020 =  0.476 

run_cache_only = False











# FIXED parameters
# --- Data ------------------------------------------#
impute = True
impute_method = 'linear'
transform_all = ""
confidence = 0.05
start_date = pd.Timestamp("2002-06-30") 
end_date = pd.Timestamp("2024-12-31") 
dropvarlist = []
umidas_model_lags = 4                  
y_var = "de_gdp_total_ca_cop_sa"
y_var_lags = 4

# --- Varselect -------------------------------------#
tcv_splits = 5                       
test_size = 10                      
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
se_factor = 0.1                      
threshold_divisor = 5
coef_tol = 0                        
k_indicators = 40
lambda_fix = lambda_calc_q2_2020
window_quarters = 4                  
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

    run_cache_only=run_cache_only,
)

pipeNOWMLUMidas.run()



# %%
