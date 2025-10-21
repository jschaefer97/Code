
#%%
# ------------------------------------------------------------------------- #
# ------------- Test Bench ------------------------------------------------ #
# ------------------------------------------------------------------------- #

import sys
import os

from sympy import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import statsmodels.api as sm
from loguru import logger

from data.nowdatapipeline import NOWDataPipeline
from utils.getdata import _save_object, _load_object

from loguru import logger
logger.remove()   

#%%

# --- Data -----------------------------------------#
mapping_periods_name = "3p_v2"
file_path = "C:/Users/johan/Desktop/Coding/Master Thesis/FU_Master_Thesis/Code"
nowpipeline_file = f"{file_path}/cache/datacache"
nowdata_file = f"{file_path}/cache/pipelinecache"
mapping_name = "NDv5"
impute = True
impute_method = 'linear'
transform_all = ""
confidence = 0.05
start_date = pd.Timestamp("2002-06-30")
end_date = pd.Timestamp("2024-12-31")
dropvarlist = []
no_lags = "nl_c" # "nl_nc", "nl_c", "l_c"
umidas_model_lags = 4 # NOTE: Do not go below 2
y_var = "de_gdp_total_ca_cop_sa"
y_var_lags = 4
y_var_short_name = "GDP"
nowcast_start = pd.Timestamp("2019-12-31")

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

# STEPTest 1.0. Load the data and check the meta

meta_df = NOWData.meta_df

# STEPTest 1.1. Check raw dataframes

raw_dfs = NOWData.raw_dfs
release_calendar_plot = NOWData.release_calendar_plot

# STEPTest 1.2. Check imputed dataframes

imp_dfs = NOWData.imp_dfs

# STEPTest 1.3. Check trasforming from daily to monthly frequency and blocked DataFrame

mq_freq_dfs = NOWData.mq_freq_dfs
blocked_df = NOWData.blocked_df

# STEPTest 1.4. Check stationarized DataFrame

stat_df = NOWData.stat_df

# STEPTest 1.5. Check filtered DataFrame

filtered_df = NOWData.filtered_df

# STEPTest 1.6. Check lagged DataFrame and series model dataframes

lagged_df = NOWData.lagged_df
series_model_dataframes = NOWData.series_model_dataframes

# STEPTest 1.7. Check the sample dataframes

full_sample_df = NOWData.full_sample_df
in_sample_df = NOWData.in_sample_df
out_sample_df = NOWData.out_sample_df

# STEPTest 1.7. Check FWR index and variable periods dictionary

fwr_idx_dict = NOWData.fwr_idx_dict
release_periods_dict = NOWData.release_periods_dict

meta = NOWData.meta

#%%

clean_calendar_plot = NOWData.clean_calendar_plot   

#%%

_save_object(NOWData, nowdata_file, "NOWDataPipeline.pkl")
#%%

NOWData = _load_object(nowdata_file, "NOWDataPipeline.pkl")

#%%

full_sample_df = NOWData.full_sample_df
fwr_idx_dict = NOWData.fwr_idx_dict
release_periods_dict = NOWData.release_periods_dict
meta_df = NOWData.meta_df
release_periods_dict = NOWData.release_periods_dict
series_model_dataframes = NOWData.series_model_dataframes
release_latest_block_dict = NOWData.release_latest_block_dict
raw_dfs = NOWData.raw_dfs
filtered_df = NOWData.filtered_df
lagged_df = NOWData.lagged_df   
stat_df = NOWData.stat_df   
blocked_df = NOWData.blocked_df

#%%

fwr_idx_dict_test = fwr_idx_dict[nowcast_start]

train_idx = fwr_idx_dict[nowcast_start]["train_idx"]
test_idx = fwr_idx_dict[nowcast_start]["test_idx"]


#%%
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error

class BenchmarkAR2:
    def __init__(self, y_var, train_data, test_data):
        self.y_var = y_var
        self.train_data = train_data.copy()
        self.test_data = test_data.copy()

        # Require at least two lag columns
        if self.train_data.shape[1] < 3 or self.test_data.shape[1] < 3:
            raise ValueError(
                "Need at least two feature columns (lags). "
                "Expected: y + 2 lag columns."
            )

        # Keep exactly the first two feature columns
        self.train_feats = list(self.train_data.columns[1:3])
        self.test_feats = list(self.test_data.columns[1:3])

        if self.train_feats != self.test_feats:
            raise ValueError(
                "Train/Test feature columns differ for AR(2).\n"
                f"Train AR(2) features: {self.train_feats}\n"
                f"Test  AR(2) features: {self.test_feats}"
            )

    def _to_yX_pd(self, df):
        y = df.iloc[:, 0]          # target (Series, keeps name)
        X = df.iloc[:, 1:3].copy() # first two lag columns (DataFrame with names)
        return y, X

    def fit(self):
        y, X_2 = self._to_yX_pd(self.train_data)
        X_2c = sm.add_constant(X_2, has_constant='add')  # const labeled 'const'
        model = sm.OLS(y, X_2c).fit()
        model_summary = model.summary()  # shows 'const' + two lag names
        return model, model_summary

    def predict(self, model):
        X_test_2 = self.test_data.iloc[:, 1:3].copy()
        X_test_2c = sm.add_constant(X_test_2, has_constant='add')

        prediction = model.get_prediction(X_test_2c)
        summary = prediction.summary_frame(alpha=0.05)  # DataFrame
        # If you want the callable and the evaluated frame, keep both:
        summary_full_df = prediction.summary_frame(alpha=0.05)

        # Evaluate first test observation (your original behavior)
        y_actual = self.test_data.iloc[0, 0]
        y_pred = summary['mean'].iloc[0]
        mse = mean_squared_error([y_actual], [y_pred])

        return y_actual, y_pred, mse, summary, summary_full_df
    
y_var_quarter_df = series_model_dataframes[y_var]["full_model_df"]

train_data_ar4 = y_var_quarter_df.loc[train_idx]
test_data_ar4  = y_var_quarter_df.loc[test_idx]

ar4_model_inst = BenchmarkAR2(
    y_var=y_var,
    train_data=train_data_ar4,
    test_data=test_data_ar4,
)

ar4_model, model_summary = ar4_model_inst.fit()

y_actual_ar4, y_pred_ar4, mse_ar4, summary_ar4, summary_full= ar4_model_inst.predict(ar4_model)

#%%

import statsmodels.api as sm
from sklearn.metrics import mean_squared_error

class BenchmarkAR2:
    def __init__(self, y_var, train_data, test_data):
        self.y_var = y_var
        self.train_data = train_data
        self.test_data = test_data

    def to_yX_np(self, df):
        y = df.iloc[:, 0].to_numpy()
        X = df.iloc[:, 1:3].to_numpy()
        return y, X

    def fit(self):
        y, X_all = self.to_yX_np(self.train_data)
        X_train = sm.add_constant(X_all, has_constant='add')
        model = sm.OLS(y, X_train).fit()
        return model

    def predict(self, model):
        X_test = self.test_data.iloc[:, 1:3].to_numpy()
        X_test = sm.add_constant(X_test, has_constant='add')

        prediction = model.get_prediction(X_test)
        summary = prediction.summary_frame(alpha=0.05)

        y_actual = self.test_data.iloc[0, 0]
        y_pred = summary['mean'].iloc[0]
        mse = mean_squared_error([y_actual], [y_pred])

        return y_actual, y_pred, mse
    
train_data_ar4 = y_var_quarter_df.loc[train_idx]
test_data_ar4  = y_var_quarter_df.loc[test_idx]

ar4_model_inst = BenchmarkAR2(
    y_var=y_var,
    train_data=train_data_ar4,
    test_data=test_data_ar4,
)

ar4_model, model_summary = ar4_model_inst.fit()

y_actual_ar4, y_pred_ar4, mse_ar4 = ar4_model_inst.predict(ar4_model)

#%%

print(model_summary)

#%%









#%%

import matplotlib.pyplot as plt

category_counts = meta_df.loc[meta_df["Filtered"] == False, "Category"].value_counts()

plt.figure(figsize=(10, 6))
category_counts.plot(kind="bar")
plt.xlabel("Category")
plt.ylabel("Count")
plt.title("Counts of Different Values in meta_df['Category'] (Filtered == False)")
plt.tight_layout()
plt.show()


#%%

a = series_model_dataframes["de_ip_total_sa"]

b = series_model_dataframes["de_ip_total_sa"]["m3_period"]

c = raw_dfs["ME"]["de_ip_total_sa"]

# [x]: m1_model
# [x]: m1_period_lag1
# [x]: m1_period_lag2
# [x]: m1_period_lag3


# [x]: m2_period
# [x]: m2_period_lag1
# [x]: m2_period_lag2
# [x]: m2_period_lag3

# [x]: m3_period
# [x]: m3_period_lag1
# [x]: m3_period_lag2
# [x]: m3_period_lag3
# [x]: m3_period_lag4

#%%

import matplotlib.pyplot as plt
import seaborn as sns

corr_matrix = full_sample_df.corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, cmap="coolwarm", center=0, annot=False)
plt.title("Cross Correlation Matrix (full_sample_df)")
plt.tight_layout()
plt.show()


#%%


























































#%%
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
from utils.checks import Checks
from data.datautils.statistics import Statistics

confidence = 0.1

non_stationary_series = []
stationary_series = []
non_stationary_quarters = []
stationary_quarters = []



# make sure we can .loc-slice cleanly (convert PeriodIndex → quarter-end Timestamps)
_df = full_sample_df.copy()
if isinstance(_df.index, pd.PeriodIndex):
    _df.index = _df.index.to_timestamp(how="end")

for q in _df.loc[nowcast_start:].index:
    train_df = _df.loc[:q, :]
    logger.debug(
        f"Quarter {q}: Testing stationarity on data from {train_df.index.min()} to {train_df.index.max()} with shape {train_df.shape}."
    )

    for series in train_df.columns:
        stat_result = Statistics.check_stationarity_s(train_df[series], confidence)
        if not stat_result:
            non_stationary_series.append((series, q))
            non_stationary_quarters.append(q)
        else:
            stationary_series.append((series, q))
            stationary_quarters.append(q)

#%%
# Build records: (meta_name, quarter) for every non-stationary series occurrence
ns_records = [
    {"MetaName": Checks.get_series_meta_name(series), "Quarter": q}
    for series, q in non_stationary_series
]

# Create the counts table (rows: meta names, cols: quarters)
ns_df = pd.DataFrame(ns_records)

quarters_sorted = sorted(fwr_idx_dict.keys())

if ns_df.empty:
    meta_series_table = pd.DataFrame(index=pd.Index([], name="MetaName"),
                         columns=quarters_sorted).fillna(0).astype(int)
else:
    meta_series_table = (
        ns_df.assign(count=1)
             .pivot_table(index="MetaName", columns="Quarter", values="count", aggfunc="sum", fill_value=0)
             .reindex(columns=quarters_sorted)  # ensure all quarters appear in sorted order
    )
    # Sort meta names by total non-stationary count (optional)
    meta_series_table = meta_series_table.loc[meta_series_table.sum(axis=1).sort_values(ascending=False).index]

# --- Add totals ---
meta_series_table["Total"] = meta_series_table.sum(axis=1)           # column with row totals
total_row = meta_series_table.sum(axis=0).to_frame().T   # single-row DataFrame
total_row.index = ["Total"]                  # name the row
meta_series_table = pd.concat([meta_series_table, total_row])        # append totals row

#%%
# --- Bar plot: number of non-stationary series per quarter ---
quarter_totals = meta_series_table.loc["Total", quarters_sorted]

fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(range(len(quarters_sorted)), quarter_totals.values)

ax.set_xticks(range(len(quarters_sorted)))
ax.set_xticklabels(quarters_sorted, rotation=45, ha="right")

ax.set_xlabel("Quarter")
ax.set_ylabel("Number of Non-Stationary Series")
ax.set_title(f"Non-Stationary Series per Quarter (confidence={confidence})")

# Add value labels on top of bars
for i, y in enumerate(quarter_totals.values):
    ax.text(i, y, str(int(y)), ha="center", va="bottom")

plt.tight_layout()
plt.show()


#%%


import pandas as pd

# Build records: (SeriesName, Quarter) for every non-stationary series occurrence
ns_records = [
    {"SeriesName": series, "Quarter": q}
    for series, q in non_stationary_series
]

# Create the counts table (rows: full series names, cols: quarters)
ns_df = pd.DataFrame(ns_records)

quarters_sorted = sorted(fwr_idx_dict.keys())

if ns_df.empty:
    table = pd.DataFrame(index=pd.Index([], name="SeriesName"),
                         columns=quarters_sorted).fillna(0).astype(int)
else:
    table = (
        ns_df.assign(count=1)
             .pivot_table(index="SeriesName", columns="Quarter", values="count",
                          aggfunc="sum", fill_value=0)
             .reindex(columns=quarters_sorted)  # ensure all quarters appear
    )
    # Sort by total non-stationary count (optional)
    table = table.loc[table.sum(axis=1).sort_values(ascending=False).index]

# --- Add totals ---
table["Total"] = table.sum(axis=1)           # row totals
total_row = table.sum(axis=0).to_frame().T   # one row with column totals
total_row.index = ["Total"]
table = pd.concat([table, total_row])        # append totals row

print(table)

















#%%

# --- count per quarter ---
non_stationary_counts = Counter(non_stationary_quarters)
stationary_counts = Counter(stationary_quarters)

quarters = sorted(fwr_idx_dict.keys())
data = {
    "Quarter": quarters,
    "Non-Stationary": [non_stationary_counts.get(q, 0) for q in quarters],
    "Stationary": [stationary_counts.get(q, 0) for q in quarters],
}
df_counts = pd.DataFrame(data)

# --- plot ---
fig, ax = plt.subplots(figsize=(10, 6))
width = 0.35
x = range(len(df_counts))

ax.bar([i - width/2 for i in x], df_counts["Non-Stationary"], width=width, label="Non-Stationary")
ax.bar([i + width/2 for i in x], df_counts["Stationary"], width=width, label="Stationary")

ax.set_xticks(x)
ax.set_xticklabels(df_counts["Quarter"], rotation=45)
ax.set_ylabel("Number of Variables")
ax.set_xlabel("Quarter")
ax.set_title(f"Stationarity of Variables per Quarter (confidence={confidence})")
ax.legend()

plt.tight_layout()
plt.show()



#%%

#%%

import pandas as pd

# Build records: (SeriesName, Quarter) for every non-stationary series occurrence
ns_records = [
    {"SeriesName": series, "Quarter": q}
    for series, q in non_stationary_series
]

# Create the counts table (rows: full series names, cols: quarters)
ns_df = pd.DataFrame(ns_records)

quarters_sorted = sorted(fwr_idx_dict.keys())

if ns_df.empty:
    table = pd.DataFrame(index=pd.Index([], name="SeriesName"),
                         columns=quarters_sorted).fillna(0).astype(int)
else:
    table = (
        ns_df.assign(count=1)
             .pivot_table(index="SeriesName", columns="Quarter", values="count",
                          aggfunc="sum", fill_value=0)
             .reindex(columns=quarters_sorted)  # ensure all quarters appear
    )
    # Sort by total non-stationary count (optional)
    table = table.loc[table.sum(axis=1).sort_values(ascending=False).index]

# --- Add totals ---
table["Total"] = table.sum(axis=1)           # row totals
total_row = table.sum(axis=0).to_frame().T   # one row with column totals
total_row.index = ["Total"]
table = pd.concat([table, total_row])        # append totals row

print(table)


#%%






print(f"Non-stationary series: {len(non_stationary_series)}")
print(f"Stationary series: {len(stationary_series)}")
print(f"Non-stationary quarters: {len(set(non_stationary_quarters))}")
print(f"Stationary quarters: {len(set(stationary_quarters))}")

#%%
from collections import Counter
print("Non-stationary quarters frequency:")
for q, count in Counter(non_stationary_quarters).items():
    print(f"{q}: {count}")

print("\nStationary quarters frequency:")
for q, count in Counter(stationary_quarters).items():
    print(f"{q}: {count}")

#%%

# Non-stationary series frequency (count per series across all quarters)
print("Non-stationary series frequency (by series):")
ns_counts = Counter(s for s, _ in non_stationary_series)
for series, count in ns_counts.most_common():
    print(f"{series}: {count}")

#%%

print("\nStationary series frequency (by series):")
st_counts = Counter(s for s, _ in stationary_series)
for series, count in st_counts.most_common():
    print(f"{series}: {count}")

#%%



from data.datautils.statistics import Statistics

confidence = 0.05

non_stationary_series = []
stationary_series = []
non_stationary_quarters = []
stationary_quarters = []

dataset = full_sample_df
print(f"dataset = {dataset.__name__ if hasattr(dataset, '__name__') else [k for k,v in locals().items() if v is dataset][0]}")
shape = dataset.shape
print(f"shape: {shape}")
for series in dataset.columns:
    stat_result = Statistics.check_stationarity_s(dataset[series], confidence)
    if not stat_result:
        non_stationary_series.append((series))
    else:
        stationary_series.append((series))


print(f"Non-stationary series: {len(non_stationary_series)}")
print(f"Stationary series: {len(stationary_series)}")
print(f"Non-stationary quarters: {len(set(non_stationary_quarters))}")
print(f"Stationary quarters: {len(set(stationary_quarters))}")

#%%
from collections import Counter
print("Non-stationary quarters frequency:")
for q, count in Counter(non_stationary_quarters).items():
    print(f"{q}: {count}")

print("\nStationary quarters frequency:")
for q, count in Counter(stationary_quarters).items():
    print(f"{q}: {count}")

#%%

# Non-stationary series frequency (count per series across all quarters)
print("Non-stationary series frequency (by series):")
ns_counts = Counter(s for s, _ in non_stationary_series)
for series, count in ns_counts.most_common():
    print(f"{series}: {count}")

#%%

print("\nStationary series frequency (by series):")
st_counts = Counter(s for s, _ in stationary_series)
for series, count in st_counts.most_common():
    print(f"{series}: {count}")


#%%
from data.datautils.statistics import Statistics

confidence = 0.05

non_stationary_series = []
stationary_series = []
non_stationary_quarters = []
stationary_quarters = []
series = "de_ifo_bs_building_bus_expect_6m_sa_m3"
for q in fwr_idx_dict.keys():
    
    train_idx = fwr_idx_dict[q]["train_idx"]

    full_sample_df_q = full_sample_df.loc[train_idx, :]

    stat_result = Statistics.check_stationarity_s(full_sample_df_q[series], confidence)
    if not stat_result:
        non_stationary_series.append((series, q))
        non_stationary_quarters.append(q)
    else:
        stationary_series.append((series, q))
        stationary_quarters.append(q)

print(f"Non-stationary series: {len(non_stationary_series)}")
print(f"Stationary series: {len(stationary_series)}")
print(f"Non-stationary quarters: {len(set(non_stationary_quarters))}")
print(f"Stationary quarters: {len(set(stationary_quarters))}")

from collections import Counter
print("Non-stationary quarters frequency:")
for q, count in Counter(non_stationary_quarters).items():
    print(f"{q}: {count}")

#%%
import re

def _get_mlag_block(series: str) -> str:
    """
    Extract the 'm' block (e.g., '_m1', '_m2') from blocked or lagged series names.

    Examples:
        'gdp_m1'                → 'm1'
        'ifocast_ip_tot_m2_lag1' → 'm2'
        'sales_lag2'            → ''   (no m-block)
    """
    match = re.search(r"_lag(\d+)$", series)
    return match.group(0).lstrip("_") if match else ""


series = "de_ifo_bs_building_bus_expect_6m_sa_m3_lag1"

m_block = _get_mlag_block(series)
print(f"Extracted 'm' block: {m_block}")


#%%


import pandas as pd
from utils.checks import Checks
import pandas as pd
from utils.checks import Checks

def make_ns_indicator_table_for_series(target_series_name):
    """
    Returns a 0/1 table:
      rows   = all series names sharing the meta name of target_series_name
      cols   = quarters (sorted)
      cell   = 1 if (series, quarter) is non-stationary, else 0
    Adds a 'Total' column (row sums) and a bottom 'Total' row (column sums).
    """
    target_meta = Checks.get_series_meta_name(target_series_name)

    # Collect all series with the same meta name (from both lists)
    candidate_series = set()
    for s, _q in non_stationary_series:
        if Checks.get_series_meta_name(s) == target_meta:
            candidate_series.add(s)
    for s, _q in stationary_series:
        if Checks.get_series_meta_name(s) == target_meta:
            candidate_series.add(s)

    quarters_sorted = sorted(fwr_idx_dict.keys())
    # Build a fast lookup for non-stationary hits
    ns_set = set(non_stationary_series)  # set of (series, quarter)

    # Initialize a 0/1 indicator table
    index = pd.Index(sorted(candidate_series), name="SeriesName")
    series_table = pd.DataFrame(0, index=index, columns=quarters_sorted, dtype=int)

    # Mark 1 where non-stationary
    for s in index:
        for q in quarters_sorted:
            if (s, q) in ns_set:
                series_table.at[s, q] = 1

    # Add totals
    series_table["Total"] = series_table.sum(axis=1)
    total_row = series_table.sum(axis=0).to_frame().T
    total_row.index = ["Total"]
    series_table = pd.concat([series_table, total_row], axis=0)

    return series_table


series = "de_ifo_bs_machinery_labour_bottle_yn"

series_table = make_ns_indicator_table_for_series(series)
#%%


























































































#%%
# --- Split df into y (first col) and X (rest), make Lasso coefficient paths + CV ---
import numpy as np
import pandas as pd

raw_df_m = raw_dfs['ME']

series_component = meta.get("ifocast_ip_tot").component

#%%

# 0) Assume you already have df
y = raw_df_m.iloc[:, 0].to_numpy()
X = raw_df_m.iloc[:, 1:].copy()

# Ensure numeric, drop all-NaN cols, impute remaining NaNs
X = X.apply(pd.to_numeric, errors="coerce")
X = X.loc[:, X.notna().any(axis=0)]
X = X.fillna(X.mean(numeric_only=True))

#%%

# 1) Standardize predictors (Lasso is scale-sensitive)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_std = scaler.fit_transform(X)

# 2) Center y for the path computation (since lasso_path has no intercept handling)
y_centered = y - np.mean(y)

# 3) Compute full Lasso path (like glmnet coefficient paths)
from sklearn.linear_model import lasso_path
alphas, coefs, _ = lasso_path(
    X_std,
    y_centered,
    max_iter=10000,
    # no fit_intercept here; lasso_path doesn't support it
    # positive=False  # (optional) uncomment if you need non-negative coefficients
)

# 4) Plot coefficient shrinkage curves vs log(alpha)
import matplotlib.pyplot as plt

plt.figure(figsize=(9, 6))
for i, name in enumerate(X.columns):
    plt.plot(np.log(alphas), coefs[i, :], linewidth=1)
plt.xlabel("log(alpha)")
plt.ylabel("Coefficient value")
plt.title("Lasso coefficient paths")
plt.tight_layout()
plt.savefig("lasso_paths_py.png", dpi=150)
plt.close()

# 5) Cross-validated Lasso to pick alpha (this *does* fit an intercept internally)
from sklearn.linear_model import LassoCV
cv = LassoCV(cv=10, n_alphas=100, max_iter=20000, random_state=0)
cv.fit(X_std, y)  # pass uncentered y; LassoCV handles intercept

alpha_min = cv.alpha_
mse_path = cv.mse_path_.mean(axis=1)   # mean CV error per alpha (shape matches cv.alphas_)
alphas_cv = cv.alphas_

# Plot CV curve (MSE vs log(alpha)), mark chosen alpha
plt.figure(figsize=(9, 6))
plt.plot(np.log(alphas_cv), mse_path, linewidth=2)
plt.axvline(np.log(alpha_min), linestyle="--")
plt.xlabel("log(alpha)")
plt.ylabel("Mean CV MSE")
plt.title(f"LassoCV: selected alpha = {alpha_min:.4g}")
plt.tight_layout()
plt.savefig("cv_mse_py.png", dpi=150)
plt.close()

# 6) Coefficients at chosen alpha (mapped back to feature names)
coef_series = pd.Series(cv.coef_, index=X.columns, name="coef_alpha_min").sort_values(
    key=lambda s: s.abs(), ascending=False
)
print(coef_series.head(20))

print("\nSaved plots:")
print(" - lasso_paths_py.png   (coefficient shrinkage paths)")
print(" - cv_mse_py.png        (cross-validation curve)")

# %%


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import enet_path, ElasticNetCV

# --- Split df into y (first col) and X (rest) ---
y = full_sample_df.iloc[:, 0].to_numpy()
X = full_sample_df.iloc[:, 1:].copy()

# Ensure numeric, drop all-NaN cols, impute remaining NaNs
X = X.apply(pd.to_numeric, errors="coerce")
X = X.loc[:, X.notna().any(axis=0)]
X = X.fillna(X.mean(numeric_only=True))

# Standardize predictors (important for Elastic Net/Lasso)
scaler = StandardScaler()
X_std = scaler.fit_transform(X)

# Center y for the path computation
y_centered = y - np.mean(y)

# --- Elastic Net path (like glmnet coefficient paths) ---
l1_ratio = 0.5  # choose ratio between L1 (lasso) and L2 (ridge)
alphas, coefs, _ = enet_path(
    X_std, y_centered,
    l1_ratio=l1_ratio,
    n_alphas=100,
    max_iter=10000
)

# Plot coefficient shrinkage curves
plt.figure(figsize=(9, 6))
for i, name in enumerate(X.columns):
    plt.plot(np.log(alphas), coefs[i, :], label=name, linewidth=1)
plt.xlabel("log(alpha)")
plt.ylabel("Coefficient value")
plt.title(f"Elastic Net coefficient paths (l1_ratio={l1_ratio})")
plt.tight_layout()
plt.savefig("enet_paths_py.png", dpi=150)
plt.close()

# --- Cross-validated Elastic Net ---
cv = ElasticNetCV(
    l1_ratio=l1_ratio,    # you can also pass a list, e.g. [0.1, 0.5, 0.9]
    cv=10,
    n_alphas=100,
    max_iter=20000,
    random_state=0
)
cv.fit(X_std, y)  # (ElasticNetCV handles intercept)

alpha_min = cv.alpha_
mse_path = cv.mse_path_.mean(axis=1)
alphas_cv = cv.alphas_

# CV curve plot
plt.figure(figsize=(9, 6))
plt.plot(np.log(alphas_cv), mse_path, linewidth=2)
plt.axvline(np.log(alpha_min), linestyle="--")
plt.xlabel("log(alpha)")
plt.ylabel("Mean CV MSE")
plt.title(f"ElasticNetCV: selected alpha = {alpha_min:.4g}, l1_ratio={l1_ratio}")
plt.tight_layout()
plt.savefig("cv_mse_enet_py.png", dpi=150)
plt.close()

# --- Coefficients at chosen alpha ---
coef_series = pd.Series(cv.coef_, index=X.columns, name="coef_alpha_min").sort_values(
    key=lambda s: s.abs(), ascending=False
)
print(coef_series.head(20))

print("\nSaved plots:")
print(" - enet_paths_py.png   (elastic net coefficient shrinkage paths)")
print(" - cv_mse_enet_py.png  (cross-validation curve)")

# %%

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

# X: your features-only DataFrame (not including y)
corr = X.corr().abs()

# Convert correlation to a distance (0 = identical, 1 = uncorrelated)
dist = 1 - corr

# Condensed vector required by linkage
dist_vec = squareform(dist.values, checks=False)

# Linkage on the distance matrix; 'average' or 'complete' both work well
Z = linkage(dist_vec, method='average')

# Choose the minimum correlation to regard variables as "in the same group"
min_corr = 0.8
# Cut the dendrogram at distance = 1 - min_corr
cluster_labels = fcluster(Z, t=1 - min_corr, criterion='distance')

# Collect variables by cluster
groups = {}
for col, lab in zip(corr.columns, cluster_labels):
    groups.setdefault(lab, []).append(col)

# Only show clusters with at least 2 variables (i.e., “groups”)
grouped = [g for g in groups.values() if len(g) >= 2]
print(f"Found {len(grouped)} groups with correlation ≥ {min_corr}:")
for i, g in enumerate(grouped, 1):
    print(f"Group {i}: {g}")


# %%

from statsmodels.stats.outliers_influence import variance_inflation_factor

import pandas as pd
X_std = (X - X.mean()) / X.std()  # standardize
vif_data = pd.DataFrame()
vif_data["feature"] = X_std.columns
vif_data["VIF"] = [variance_inflation_factor(X_std.values, i) 
                   for i in range(X_std.shape[1])]
print(vif_data.sort_values("VIF", ascending=False).head(20))


# %%

import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram

corr = X.corr().abs()

# Hierarchical clustering
linked = linkage(corr, method='ward')

plt.figure(figsize=(10, 5))
dendrogram(linked, labels=corr.columns, leaf_rotation=90)
plt.title("Hierarchical clustering of variables (based on correlation)")
plt.show()

# Heatmap with clustered rows/cols
sns.clustermap(corr, cmap="coolwarm", center=0, figsize=(12, 12))


# %%

import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram

plt.figure(figsize=(12, 6))
dendrogram(Z, labels=corr.columns, leaf_rotation=90)
plt.title("Dendrogram of variables (correlation-based)")
plt.show()


# %%

import seaborn as sns

sns.clustermap(corr, cmap="coolwarm", center=0, figsize=(12, 12))


# %%

from sklearn.manifold import MDS
import matplotlib.pyplot as plt

# correlation-based distance
dist = 1 - X.corr().abs().values
mds = MDS(dissimilarity="precomputed", random_state=0)
coords = mds.fit_transform(dist)

plt.figure(figsize=(8, 6))
plt.scatter(coords[:, 0], coords[:, 1], s=40, alpha=0.7)

show_names = True  # <-- toggle here

if show_names:
    for i, name in enumerate(X.columns):
        plt.text(coords[i, 0], coords[i, 1], name, fontsize=8)

plt.title("MDS embedding of variables (based on correlation)")
plt.show()


# %%

plt.scatter(coords[:, 0], coords[:, 1], s=40, alpha=0.7)
# no plt.text() here


# %%

import plotly.express as px
import pandas as pd
df_plot = pd.DataFrame(coords, columns=["x", "y"])
df_plot["variable"] = X.columns

fig = px.scatter(
    df_plot, x="x", y="y", text=None, hover_name="variable",
    title="MDS embedding of variables (hover to see name)",
    width=1200, height=1200
        # wider and taller figure
)
fig.show()


# %%
from sklearn.cluster import KMeans

k = 8  # number of clusters you want
km = KMeans(n_clusters=k, random_state=0).fit(coords)
labels = km.labels_

plt.figure(figsize=(8,6))
plt.scatter(coords[:,0], coords[:,1], c=labels, cmap="tab10", s=40, alpha=0.8)
plt.title("MDS embedding colored by clusters")
plt.show()

# %%

import plotly.express as px
from sklearn.cluster import KMeans
import pandas as pd

# Run clustering
k = 8
km = KMeans(n_clusters=k, random_state=0).fit(coords)
labels = km.labels_

# Dataframe for Plotly
df_plot = pd.DataFrame(coords, columns=["x", "y"])
df_plot["cluster"] = labels.astype(str)   # cast to str → treated as categorical
df_plot["variable"] = X.columns

# Plotly scatter
fig = px.scatter(
    df_plot,
    x="x", y="y",
    color="cluster",                # categorical coloring
    hover_name="variable",
    title="MDS embedding colored by clusters",
    color_discrete_sequence=px.colors.qualitative.Set1,  # or Plotly's tab10: px.colors.qualitative.T10
    width=1200, height=1200
)

fig.show()


# %%

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.checks import Checks
from collections import Counter
import seaborn as sns

# coords: (n_vars, 2) from your MDS
# X.columns: variable names
df_plot = pd.DataFrame(coords, columns=["x", "y"])
df_plot["variable"] = X.columns

def get_component_safe(var):
    meta_var = Checks.get_series_meta_name(var)
    m = meta.get(meta_var)              # may be None, object, or dict
    if m is None:
        return "Unknown"
    # try attribute first
    comp = getattr(m, "category", None)
    # if not attribute, try dict-style
    if comp is None and isinstance(m, dict):
        comp = m.get("category")
    return comp if comp is not None else "Unknown"

df_plot["component"] = [get_component_safe(v) for v in df_plot["variable"]]
df_plot["component"] = df_plot["component"].astype(str)

# quick sanity check: how many unknowns?
n_unknown = (df_plot["component"] == "Unknown").sum()
print(f"Components assigned. Unknown: {n_unknown} / {len(df_plot)}")

# Base scatter colored by component
fig = px.scatter(
    df_plot,
    x="x", y="y",
    color="component",              # categorical colors
    hover_name="variable",
    title="MDS embedding colored by component",
    color_discrete_sequence=px.colors.qualitative.Set3  # or px.colors.qualitative.T10 / Plotly / Set2
)
# OPTIONAL: overlay centroids per component
add_centroids = True
if add_centroids:
    centroids = df_plot.groupby("component", as_index=False)[["x", "y"]].mean()
    fig.add_trace(go.Scatter(
        x=centroids["x"], y=centroids["y"],
        mode="markers+text",
        text=centroids["component"],
        textposition="top center",
        marker=dict(size=14, symbol="x"),
        name="component centroid",
        showlegend=False
    ))

fig.update_layout(
    width=1400,
    height=1400,
    plot_bgcolor="black",
    paper_bgcolor="black",
    font_color="white",
    xaxis_showgrid=False,
    yaxis_showgrid=False
)
fig.show()

# %%
