
#%%
# ------------------------------------------------------------------------- #
# ------------- Test Bench ------------------------------------------------ #
# ------------------------------------------------------------------------- #

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import statsmodels.api as sm
from loguru import logger
from data.nowdatapipeline import NOWDataPipeline

from varselect.methods.elasticnet import ElasticNetVariableSelector
from utils.getdata import _save_object, _load_object
from IPython.display import display

import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from mlumidas.mixins.mlumidas import MLUMidasMixin
from mlumidas.mixins.mlumidasoutput import MLUMidasOutputMixin
from mlumidas.mixins.mlumidascache import MLUMidasCacheMixin
from mlumidas.mixins.mlumidassavingplots import MLUMidasSavingPlotsMixin


from mlumidas.mlumidaspipeline import MLUMidasPipeline

from utils.checks import Checks
from utils.utils import get_formatted_date

from pipeline.mixins.summary import SummaryMixin
import webbrowser

# from loguru import logger
# logger.remove()   

#%%

# --- Data -----------------------------------------#
mapping_periods_name = "4p_v0"
file_path = "C:/Users/johan/Desktop/Coding/Master Thesis/FU_Master_Thesis/Code"
nowpipeline_file = f"{file_path}/cache/datacache"
nowdata_file = f"{file_path}/cache/pipelinecache"
mapping_name = "IfoCast"
impute = True
impute_method = 'linear'
transform_all = ""
confidence = 0.1
start_date = pd.Timestamp("2006-06-30")
end_date = pd.Timestamp("2024-12-31")
dropvarlist = []
no_lags = False
umidas_model_lags = 7 # NOTE: Do not go below 2
y_var = "de_gdp_total_ca_cop_sa"
y_var_lags = 4
y_var_short_name = "GDP"
nowcast_start = pd.Timestamp("2018-03-31")

# --- Varselect -------------------------------------#
varselection_method = "pyencv"

alpha = 0.5
tcv_splits = 10
test_size = 1
gap = 0
max_train_size = 91
cv = 5
alphas = 500
max_iter = 1000000
random_state = 42
with_mean = True
with_std = True
fit_intercept = True
selection_rule = "pt"
se_factor = 0.5
threshold_divisor = 20.0
coef_tol = 0
save_q_plots = True
group_type = "category"  

formatted_start_date = get_formatted_date(start_date)
formatted_end_date   = get_formatted_date(end_date)

if varselection_method in ["pyencv"]:
    spec_name = f"{mapping_name}_{mapping_periods_name}_{formatted_start_date}_{formatted_end_date}_{y_var_short_name}_{umidas_model_lags}lags_{varselection_method}_a{alpha}_{selection_rule}"
    if selection_rule == "cv_se":
        spec_name += f"{se_factor}"
    if coef_tol > 0:
        spec_name += f"_ct{coef_tol}"
    if selection_rule == "pt":
        spec_name += f"_td{threshold_divisor}"

elif varselection_method == "no_selection": 
    spec_name = f"{mapping_name}_{mapping_periods_name}_{formatted_start_date}_{formatted_end_date}_{y_var_short_name}_{varselection_method}"


#%%

NOWData = NOWDataPipeline(
    file_path=file_path,
    mapping_name=mapping_name,
    mapping_periods_name=mapping_periods_name,
    impute=impute,
    impute_method=impute_method,
    transform_all=transform_all,
    confidence=confidence,
    start_date=start_date,
    end_date=end_date,
    dropvarlist=dropvarlist,
    no_lags=no_lags,
    umidas_model_lags=umidas_model_lags,
    y_var=y_var,
    y_var_lags=y_var_lags,
    nowcast_start=nowcast_start
)

NOWData.run()


#%%
_save_object(NOWData, nowpipeline_file, "NOWDataPipeline.pkl")

#%%
NOWData = _load_object(nowpipeline_file, "NOWDataPipeline.pkl")

meta = NOWData.meta
meta_df = NOWData.meta_df
release_latest_block_dict = NOWData.release_latest_block_dict
release_periods_dict = NOWData.release_periods_dict
series_model_dataframes = NOWData.series_model_dataframes
fwr_idx_dict = NOWData.fwr_idx_dict
full_sample_df = NOWData.full_sample_df

#%%

MLUMidas = MLUMidasPipeline(
    file_path=file_path,
    varselection_method=varselection_method,
    fwr_idx_dict=fwr_idx_dict,
    release_periods_dict=release_periods_dict,
    y_var=y_var,

    full_sample_df=full_sample_df,
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

    series_model_dataframes=series_model_dataframes,
    release_latest_block_dict=release_latest_block_dict,
    meta=meta,
    umidas_model_lags=umidas_model_lags,
    start_date=start_date,
    end_date=end_date,

    spec_name=spec_name,
    save_q_plots=save_q_plots,
    group_type=group_type
)

MLUMidas.run()

#%%

pool = "avg"          # or "median"
branch = "latest"     # or "selected"
criterion = "aic"
period = "p4"
quarter = pd.Timestamp("2020-06-30")

oof_plots = MLUMidas.oof_plots
oof_all_periods_plots = MLUMidas.oof_all_periods_plots
oof_single_quarter_plots = MLUMidas.oof_single_quarter_plots

plot = oof_plots[pool][branch][criterion][period]
display(plot)

fig = oof_single_quarter_plots[pool][branch][criterion][quarter]
display(fig)

#%%
fig_all = oof_all_periods_plots[pool][branch][criterion]
display(fig_all)


#%%







































































#%%

from mlumidas.utils.modelgrid import get_model_grid_dict

model_grid = get_model_grid_dict()
n_specs = len(model_grid["monthly_grid"])

#%%

NOWData = NOWDataPipeline(
    file_path=file_path,
    mapping_name=mapping_name,
    mapping_periods_name=mapping_periods_name,
    impute=impute,
    impute_method=impute_method,
    transform_all=transform_all,
    confidence=confidence,
    start_date=start_date,
    end_date=end_date,
    dropvarlist=dropvarlist,
    no_lags=no_lags,
    umidas_model_lags=umidas_model_lags,
    y_var=y_var,
    y_var_lags=y_var_lags,
    nowcast_start=nowcast_start
)

NOWData.run()

#%%

_save_object(NOWData, nowpipeline_file, "NOWDataPipeline.pkl")

#%%
    
NOWData = _load_object(nowpipeline_file, "NOWDataPipeline.pkl")

#%%
meta = NOWData.meta
meta_df = NOWData.meta_df
release_latest_block_dict = NOWData.release_latest_block_dict
release_periods_dict = NOWData.release_periods_dict
series_model_dataframes = NOWData.series_model_dataframes
fwr_idx_dict = NOWData.fwr_idx_dict
full_sample_df = NOWData.full_sample_df

#%%

file_path_modelcache = f"{file_path}/cache/mlumidascache"
mlcache = MLUMidasCacheMixin()

model_cache = mlcache.load_or_compute_model_cache(
            umidas_model_lags=umidas_model_lags,
            file_path_modelcache=file_path_modelcache,
            start_date=start_date,
            end_date=end_date,
            y_var=y_var,
            fwr_idx_dict=fwr_idx_dict,
            series_model_dataframes=series_model_dataframes,
            meta=meta
        )

#%%


file_path_output = f"{file_path}/output/mlumidas"

varselection_method = "pyencv"

# --- Varselect -------------------------------------#
alpha = 0.5
tcv_splits = 10
test_size = 1
gap = 0
max_train_size = 91
cv = 5
alphas = 500
max_iter = 1000000
random_state = 42
with_mean = True
with_std = True
fit_intercept = True
selection_rule = "cv_se"
se_factor = 0.5

threshold_divisor = 5.0
coef_tol = 0

save_q_plots = True

formatted_start_date = get_formatted_date(start_date)
formatted_end_date   = get_formatted_date(end_date)

if varselection_method in ["pyencv", "pyeaaic"]:
    spec_name = f"{mapping_name}_{formatted_start_date}_{formatted_end_date}_{y_var_short_name}_{umidas_model_lags}lags_{varselection_method}_a{alpha}_{selection_rule}_ct{coef_tol}"
elif varselection_method == "no_selection": 
    spec_name = f"{mapping_name}_{formatted_start_date}_{formatted_end_date}_{y_var_short_name}_{varselection_method}"

mlu = MLUMidasMixin()

results_dict = mlu.get_results_dict(
    varselection_method=varselection_method,
    fwr_idx_dict=fwr_idx_dict,
    release_periods_dict=release_periods_dict,
    y_var=y_var,

    full_sample_df=full_sample_df,
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

    series_model_dataframes=series_model_dataframes,
    release_latest_block_dict=release_latest_block_dict,
    meta=meta,
    umidas_model_lags=umidas_model_lags,
    start_date=start_date,
    end_date=end_date,

    model_cache=model_cache,
)
#%%

output = MLUMidasOutputMixin()
plots = output.get_oof_plots(results_dict, title=spec_name)
plots_all_periods = output.get_oof_all_periods_plots(results_dict, title=spec_name)

#%%

group_type = "category"
plots_single_quarter = output.get_oof_single_quarter_plots(results_dict, group_by=group_type, title=spec_name)

#%%

safe = MLUMidasSavingPlotsMixin()

safe.save_plots(plots, file_path_output)
safe.save_plots(plots_all_periods, file_path_output)
safe.save_plots(plots_single_quarter, file_path_output)

#%%

pool = "avg"          # or "median"
branch = "latest"     # or "selected"
criterion = "aic"
period = "p4"
quarter = pd.Timestamp("2020-06-30")

# plot
plot = plots[pool][branch][criterion][period]
display(plot)

fig = plots_single_quarter[pool][branch][criterion][quarter]
display(fig)

# All periods overlay (this is already a Figure; no further indexing)
fig_all = plots_all_periods[pool][branch][criterion]
display(fig_all)

#%%

smixin = SummaryMixin()

summary = smixin.get_spec_summary(
        results_dict=results_dict,
        spec_name=spec_name,
        mapping_periods_name=mapping_periods_name,
        mapping_name=mapping_name,
        start_date=start_date,
        nowcast_start=nowcast_start,
        end_date=end_date,
        y_var=y_var,
        y_var_short_name=y_var_short_name,

        impute=impute,
        impute_method=impute_method,
        transform_all=transform_all,
        confidence=confidence,
        dropvarlist=dropvarlist,
        no_lags=no_lags,
        umidas_model_lags=umidas_model_lags,
        y_var_lags=y_var_lags,

        varselection_method=varselection_method,
        alpha=alpha,
        cv=cv,
        alphas=alphas,
        max_iter=max_iter,
        random_state=random_state,
        with_mean=with_mean,
        with_std=with_std,
        fit_intercept=fit_intercept,
        coef_tol=coef_tol, 

        tcv_splits=tcv_splits,
        test_size=test_size,
        gap=gap,
        max_train_size=max_train_size,

        save_q_plots=save_q_plots,

        output_path=file_path_output
)


#%%
import webbrowser; webbrowser.open(summary)


#%%

# period details (DataFrame for this quarter & period)
period_details = results_dict["model"]["periods_details"][branch][criterion]
detail_result = period_details[quarter][period]  # DataFrame

# selected variables at (quarter, period)
# For the 'selected' branch, the DataFrame index are the raw selected names (e.g., 'm2_lag2')
# For the 'latest' branch, they’re meta series names.
idx = detail_result.index
selected_rows = [i for i in idx if i not in ("Average", "Median")]

if branch == "selected":
    selected_vars_raw_pq = selected_rows
    selected_vars_meta_pq = [Checks.get_series_meta_name(s) for s in selected_rows]
else:  # branch == "latest"
    selected_vars_meta_pq = selected_rows
    selected_vars_raw_pq = None  # raw-with-lag not tracked for 'latest'

period_model_results_avg_dfs_dict = results_dict["model"]["periods_avg"] 

period_model_results_avg_dfs_dict_spec = period_model_results_avg_dfs_dict[branch][criterion][period]

#%%














































































































#%%














output = MLUMidasOutputMixin()

# Per-period plots (same as before)
plots = output.get_oof_plots(results_dict)

# All-periods-on-one-figure plots
all_periods_plots = output.get_oof_all_periods_plots(results_dict)

pool = "avg"          # or "median"
branch = "selected"     # or "selected"
criterion = "aic"
period = "p1"
quarter = pd.Timestamp("2020-09-30")

# Single period plot
fig_single = plots[pool][branch][criterion][period]
display(fig_single)

# All periods overlay (this is already a Figure; no further indexing)
fig_all = all_periods_plots[pool][branch][criterion]
display(fig_all)

# If you want to loop all criteria:
# for crit, fig in all_periods_plots[pool][branch].items():
#     print(crit)
#     display(fig)

#%%

# build the plots dict
output = MLUMidasOutputMixin()
single_q_plots = output.get_oof_single_quarter_plots(results_dict)

# --- Option A: if you know the quarter ---
import pandas as pd
from IPython.display import display


pool = "avg"        # or "median"
branch = "latest"   # or "selected"
criterion = "bic"   # "aic" / "adj_r2" also valid
q = pd.Timestamp("2024-09-30")





#%%

X = full_sample_df.to_numpy()
tscv = TimeSeriesSplit(n_splits=10, test_size=1, gap=0, max_train_size=91) 
print(tscv)
for i, (train_index, test_index) in enumerate(tscv.split(X)):
    print(f"Fold {i}:")
    print(f"  Train: index={train_index}")
    print(f"  Test:  index={test_index}")

#%%

#%%


#%%





























































































































# %%

period_model_results_avg_dfs = results_dict["model"]["periods_avg"]

# %%
criterion = "bic"
period = "p4"
quarter = pd.Timestamp("2020-09-30")

#%%

p4_results = period_model_results_avg_dfs[criterion][period]

import matplotlib.pyplot as plt

df_plot = p4_results[['y_actual', 'y_pred']].sort_index().dropna()

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(df_plot.index, df_plot['y_actual'], label='Actual')
ax.plot(df_plot.index, df_plot['y_pred'],   label='Predicted')

ax.set_title('Actual vs Predicted')
ax.set_xlabel('Quarter')
ax.set_ylabel('Value')
ax.legend()
ax.grid(True, alpha=0.3)
fig.autofmt_xdate()
plt.tight_layout()
plt.show()

# %%

period_details_dfs = results_dict["model"]["periods_details"]["periods_model_results_df"]

detail_result = period_details_dfs[criterion][quarter][period]

# %%
from collections import defaultdict
from mlumidas.models.umidas import UMidas

series = "ifocast_ip_tot"

latest_period = release_latest_block_dict[series][period]
series_model_period_df = series_model_dataframes[series][latest_period]

train_idx = fwr_idx_dict[quarter]["train_idx"]
test_idx  = fwr_idx_dict[quarter]["test_idx"]
train_data = series_model_period_df.loc[train_idx]
test_data  = series_model_period_df.loc[test_idx]

freq = meta.get(series).freq
model_grid_dict = get_model_grid_dict(umidas_model_lags=umidas_model_lags)
model_grid = model_grid_dict["quarterly_grid"] if freq == "QE" else model_grid_dict["monthly_grid"]

umindas_model = UMidas(
    y_var=y_var,
    train_data=train_data,
    test_data=test_data,
    model_grid=model_grid,
)

best_models_by_criterion = umindas_model.get_best()

# nested dict: crit -> period -> series -> metrics
period_series_model_results_dict = defaultdict(lambda: defaultdict(dict))
from collections import defaultdict

# nested dict: crit -> period -> series -> metrics (+ summary)
period_series_model_results_dict = defaultdict(lambda: defaultdict(dict))

for crit, obj in best_models_by_criterion.items():
    spec = obj["spec"]
    if spec is None:
        continue

    model = umindas_model.fit(spec)
    y_actual, y_pred, mse = umindas_model.predict(model, spec)

    # statsmodels Summary (choose one)
    summary_txt  = model.summary().as_text()
    # summary_html = model.summary().as_html()

    period_series_model_results_dict[crit][period][series] = {
        "y_actual": y_actual,
        "y_pred": y_pred,
        "mse": mse,
        "summary": summary_txt,        # or "summary_html": summary_html
    }

# optional: convert defaultdicts to plain dicts
period_series_model_results_dict = {k: dict(v) for k, v in period_series_model_results_dict.items()}

# later
series_result = period_series_model_results_dict[criterion][period][series]
print(series_result["summary"])  # text table
# or display HTML in a notebook:
# from IPython.display import HTML; HTML(series_result["summary_html"])


# per-criterion fitted model summary (text)
for crit, obj in best_models_by_criterion.items():
    if obj["model"] is None:
        continue
    print(f"\n=== {crit.upper()} best spec {obj['spec']} ===")
    print(obj["summary_text"])


from joblib import load
from collections import Counter
from utils.utils import get_formatted_date

# Point to an actual cache you created             # e.g., "./cache_test"
file_path_modelcache = f"{file_path}/cache/mlumidascache"

formatted_start_date = get_formatted_date(start_date)
formatted_end_date = get_formatted_date(end_date)
top_level_key = f"{formatted_start_date}_to_{formatted_end_date}_{y_var}_lags_{umidas_model_lags}"

file_path_modelcache = f"{file_path}/cache/mlumidascache/model_cache_{top_level_key}.pkl"

raw = load(file_path_modelcache)

# Normalize to a dict[(tlk,q,f,s,period_type,crit)] -> payload
def to_dict(obj):
    if isinstance(obj, dict):
        return obj
    out = {}
    if isinstance(obj, (list, tuple)):
        for item in obj:
            if isinstance(item, tuple):
                if len(item) == 2 and isinstance(item[0], tuple):
                    k, v = item
                    out[k] = v
                elif len(item) == 7:  # legacy: (tlk,q,f,s,period,crit,payload)
                    k = tuple(item[:6])
                    v = item[6]
                    out[k] = v
    return out

cache = to_dict(model_cache)

print(f"Total entries: {len(cache)}")

# Show a few sample keys
print("\nSample keys:")
for i, k in enumerate(cache.keys()):
    print(k)
    if i >= 9:
        break

# What criterion labels are actually present?
crit_counts = Counter(k[-1] for k in cache.keys())
print("\nCriterion labels and counts:")
for crit, cnt in crit_counts.most_common():
    print(f"  {crit!r}: {cnt}")

# Optional: frequency and period_type shape
freq_counts = Counter(k[2] for k in cache.keys())   # 'QE' or 'ME'
period_counts = Counter(k[4] for k in cache.keys())  # e.g. 'm1_period', 'q_period_lag1'
print("\nFreq counts:", dict(freq_counts))
print("Period_type counts (top 10):", dict(period_counts.most_common(10)))




# pick pool/branch/criterion to test
pool = "avg"            # or "median"
branch = "latest"       # or "selected"
crit = "bic"            # e.g., "bic", "aic", "adj_r2"

periods_dict = results_dict["model"][f"periods_{pool}"][branch][crit]

# pooled yearly MSE across ALL periods (ground truth used by all-periods figure)
mse_concat = []
for p, df in periods_dict.items():
    if isinstance(df, pd.DataFrame) and not df.empty and "mse" in df.columns:
        idx = df.index.to_timestamp() if isinstance(df.index, pd.PeriodIndex) else pd.to_datetime(df.index)
        mse_concat.append(pd.Series(pd.to_numeric(df["mse"], errors="coerce").values, index=idx.year))
mse_by_year_all = (pd.concat(mse_concat).groupby(level=0).mean().sort_index()
                   if mse_concat else pd.Series(dtype=float))
display(mse_by_year_all.to_frame("avg_mse_all_periods"))

# cross-check: simple average of each period's per-year averages (may differ if periods have unequal counts)
avg_mse_y_concat = []
for p, df in periods_dict.items():
    if isinstance(df, pd.DataFrame) and "avg_mse_y" in df.columns:
        idx = df.index.to_timestamp() if isinstance(df.index, pd.PeriodIndex) else pd.to_datetime(df.index)
        s = pd.Series(df["avg_mse_y"].values, index=idx.year).groupby(level=0).first()
        avg_mse_y_concat.append(s)
avg_of_period_means = (pd.concat(avg_mse_y_concat, axis=1).mean(axis=1).sort_index()
                       if avg_mse_y_concat else pd.Series(dtype=float))
display(avg_of_period_means.to_frame("mean_of_period_means"))

# difference (should be ~0 if each period contributes equally per year)
display((mse_by_year_all - avg_of_period_means).to_frame("diff"))
