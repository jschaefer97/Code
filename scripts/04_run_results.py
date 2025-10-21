#%%

from utils.getdata import _load_object, _save_xlsx
from utils.resultsrender import save_period_rel_rmse_panels
from utils.resultsplotter import ResultsPlotter

from pathlib import Path
import re
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from main import FILE_PATH

#%%

###############################################################################
###############################################################################
######################### Result Outputs ######################################
###############################################################################
###############################################################################

file_path_inload = f"{FILE_PATH}/output/results/"
file_path_MA = f"{FILE_PATH}/output/results/MA/"

#%%

results_spec_nl_c = {
    # Baseline spec
    "LASSO": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a1_qw4_nl_nc",
    "ElasticNet_08": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a0.8_qw4_nl_nc",
    "ElasticNet_05": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a0.5_qw4_nl_nc",
    "ElasticNet_02": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a0.2_qw4_nl_nc",
    "NoSelection": "NDv5_3p_v2_2002Q2_2024Q4_GDP_nsel_qw4_nl_nc",

    # Lambda fix at Q2 2020 for EN02
    "LASSO_len02": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyen_a1_lam0.476_qw4_nl_nc",
    "ElasticNet_08_len02": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyen_a0.8_lam0.476_qw4_nl_nc",
    "ElasticNet_05_len02": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyen_a0.5_lam0.476_qw4_nl_nc",
    "ElasticNet_02_len02": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a0.2_qw4_nl_nc",

    # Lambda fix at 2CV of Q2 2020 for all methods
    # Individual CV for Q22020: EN02: 0.344, EN05: 0.150, EN08: 0.122, LASSO: 0.099
    "LASSO_l2cv": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyen_a1_lam0.198_qw4_nl_nc",
    "ElasticNet_08_l2cv": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyen_a0.8_lam0.244_qw4_nl_nc",
    "ElasticNet_05_l2cv": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyen_a0.5_lam0.3_qw4_nl_nc",
    "ElasticNet_02_l2cv": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyen_a0.2_lam0.688_qw4_nl_nc",
}

results_dictionaries = dict()
for method in results_spec_nl_c.keys():
    spec = results_spec_nl_c[method]
    results_dictionaries[method] = _load_object(f"{file_path_inload}/{spec}", f"results_dict_{spec}.pkl")

full_sample_df = _load_object(f"{file_path_inload}/NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a1_qw4_nl_nc", f"full_sample_df_NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a1_qw4_nl_nc.pkl")
meta_df = _load_object(f"{file_path_inload}/NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a1_qw4_nl_nc", f"meta_df_NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a1_qw4_nl_nc.pkl")
release_periods_dict = _load_object(f"{file_path_inload}/NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a1_qw4_nl_nc", f"release_periods_dict_NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a1_qw4_nl_nc.pkl")

_save_xlsx(full_sample_df, file_path_MA, f"full_sample_data_nl_nc")
_save_xlsx(meta_df, file_path_MA, f"meta_data_nl_nc")

#%%
###############################################################################
#------------------------ Outcome Plots (all methods) ------------------------#
###############################################################################

weights = ["periods_mseweight", "periods_avg"]
periods = ["p1", "p2", "p3"]

file_path_plots_period_stack = f"{file_path_MA}/gdp_nowcast_oof_period_plot"
plotter_methods = ResultsPlotter(output_dir=file_path_plots_period_stack, fmt="pdf", dpi=150)

method_label_map = {
    "LASSO": "LASSO",
    "ElasticNet_08": "EN08",
    "ElasticNet_05": "EN05",
    "ElasticNet_02": "EN02",
    "NoSelection": "NPS"
}

methods = ["LASSO", "ElasticNet_08", "ElasticNet_05", "ElasticNet_02", "NoSelection"]

all_methods_one_period_plot = {}

for weight in weights:
    all_methods_one_period_plot.setdefault(weight, {})
    for period in periods:
        filename = f"all_methods_{period}_{weight}_oos"
        fig = plotter_methods.plot_one_period_all_methods(
            results_dictionaries=results_dictionaries,
            methods=methods,
            weight=weight,
            period=period,
            filename=filename,
            method_label_map=method_label_map,
            oos_start=2019,
            oos_end=2024,
        )
        all_methods_one_period_plot[weight][period] = fig

#%%
###############################################################################
#------------------------ Relative RMSE Table Full Years ---------------------#
###############################################################################
file_path_era_rmse_tables = f"{file_path_MA}/relative_rmse_table"

weights = ["periods_mseweight", "periods_avg"]
pretty_cols = {"LASSO": "LASSO", 
                "ElasticNet_08": "EN08", 
                "ElasticNet_05": "EN05", 
                "ElasticNet_02": "EN02", 
                "NoSelection": "NPS"}
methods_order = ["LASSO", "ElasticNet_08", "ElasticNet_05", "ElasticNet_02", "NoSelection"] 
eras = ["covid", "post_covid", "all"]                   

covid_start = pd.Timestamp("2020-03-31")
covid_end   = pd.Timestamp("2021-03-31")
post_start  = pd.Timestamp("2021-06-30")
post_end    = pd.Timestamp("2024-12-31")

def period_to_h(s: str) -> str:
    s = str(s)
    m = re.fullmatch(r"p(\d+)", s, flags=re.IGNORECASE)
    if m: return f"h{int(m.group(1)) - 1}"
    m = re.fullmatch(r"h(\d+)", s, flags=re.IGNORECASE)
    if m: return f"h{int(m.group(1))}"
    return s

period_rel_rmse = {}

for weight in weights:
    tables_by_h = {}

    for p_label in ["p1", "p2", "p3"]:
        h_label = period_to_h(p_label)

        data = {era: [] for era in eras}

        for method in methods_order:
            df = results_dictionaries[method]["model"][weight]["selected"]["bic"][p_label]

            mask_all        = (df.index == df.index)
            mask_covid      = (df.index >= covid_start) & (df.index <= covid_end)
            mask_post_covid = (df.index >= post_start) & (df.index <= post_end)

            for era, mask in [("covid", mask_covid), ("post_covid", mask_post_covid), ("all", mask_all)]:
                df_e = df.loc[mask]
                if df_e.empty:
                    rel = np.nan
                else:
                    mse_y = pd.to_numeric(df_e["mse"], errors="coerce").mean() if "mse" in df_e.columns else np.nan
                    rmse_y = np.sqrt(mse_y) if np.isfinite(mse_y) else np.nan

                    if "mse_ar4" in df_e.columns:
                        mse_ar4 = pd.to_numeric(df_e["mse_ar4"], errors="coerce").mean()
                        rmse_ar4 = np.sqrt(mse_ar4) if (np.isfinite(mse_ar4) and mse_ar4 > 0) else np.nan
                    else:
                        rmse_ar4 = np.nan

                    rel = float(rmse_y / rmse_ar4) if (np.isfinite(rmse_y) and np.isfinite(rmse_ar4) and rmse_ar4 > 0) else np.nan

                data[era].append(rel)

        df_out = pd.DataFrame(data, index=[pretty_cols.get(m, m) for m in methods_order], columns=eras)
        tables_by_h[h_label] = df_out

    period_rel_rmse[weight] = {"tables_by_h": tables_by_h}

for weight in weights:
    if weight not in period_rel_rmse:
        print(f"[warn] No results for weight='{weight}', skipping.")
        continue

    tables_by_h = period_rel_rmse[weight].get("tables_by_h", {})
    if not tables_by_h:
        print(f"[warn] 'tables_by_h' missing for weight='{weight}', skipping.")
        continue

    for h in ("h0", "h1", "h2"):
        if h not in tables_by_h:
            print(f"[warn] Horizon '{h}' missing for weight='{weight}', skipping this sheet.")
            continue
        df_h = tables_by_h[h]
        _save_xlsx(df_h, file_path_era_rmse_tables, f"era_rmse_{h}_{weight}")

    label_suffix = weight.replace(":", "_").replace("-", "_")
    save_period_rel_rmse_panels(
        tables_by_h,
        path=f"{file_path_era_rmse_tables}/rel_rmse_three_panels_{weight}.tex",
        caption=f"Relative RMSE (method ÷ AR(4)) by era; panels show horizons h0–h2 — {weight}",
        label=f"tab:rel_rmse_panels_{label_suffix}",
        panel_titles={"h0": "Horizon h0", "h1": "Horizon h1", "h2": "Horizon h2"},
        era_order=["covid", "post_covid", "all"],
        method_labels={"LASSO": "LASSO", "Elastic Net": "Elastic Net", "No Selection": "No Selection"},
    )

#%%
###############################################################################
#------------------------ Selected Indicators --------------------------#
###############################################################################
file_path_selected_counts = f"{file_path_MA}/average_number_selected_indicators"

methods = ["LASSO", "ElasticNet_08", "ElasticNet_05", "ElasticNet_02"]
periods = ["p1", "p2", "p3"]

selected_indicator_methods_p = {}

for p in periods:
    selected_indicator_methods_p[p] = {}
    for m in methods:
        method_dictionary = results_dictionaries[m]
        selected_indicators_p = method_dictionary["varselect"]["selected_vars_quarters"]["selected"]["bic"][p]
        s = selected_indicators_p.loc["Selected_Count"]
        if isinstance(s.index, pd.PeriodIndex):
            s.index = s.index.to_timestamp()
        else:
            s.index = pd.to_datetime(s.index)
        s = pd.to_numeric(s, errors="coerce")
        selected_indicator_methods_p[p][m] = s

selected_counts_by_period = {}
for p in periods:
    df_counts = pd.DataFrame(selected_indicator_methods_p[p]).T
    df_counts = df_counts.reindex(columns=sorted(df_counts.columns))
    selected_counts_by_period[p] = df_counts

avg_counts = pd.DataFrame({
    p: selected_counts_by_period[p].mean(axis=1)
    for p in periods
})

avg_counts = avg_counts.reindex(methods)
_save_xlsx(avg_counts, file_path_selected_counts, f"average_number_selected_indicators")

#%%
###############################################################################
#------------------------ Elastic Net Perfomance Recovery Q3 2020 ------------#
###############################################################################

#------------------------ 1. Get the selected plots for Q3 2020 --------------#

file_path_grouping_effect_q3_2020 = f"{file_path_MA}/grouping_effect/q3_2020"

methods= ["LASSO", "ElasticNet_08", "ElasticNet_05", "ElasticNet_02"]
period = "p2"
quarter = pd.Timestamp("2020-09-30")

# Step 1: get the top mse of the quarter
no_selection_dict = results_dictionaries["NoSelection"]
model_results_details_p = no_selection_dict["model"]["periods_details"]["selected"]["bic"][quarter][period]
model_results_details_sorted_mse_p = model_results_details_p.sort_values(by="mse", ascending=True)
model_results_details_sorted_mse_p_row_names = [
    name for name in model_results_details_sorted_mse_p.index.tolist()
    if name not in ['Average', 'Median', 'ci_lower', 'ci_upper']
]

# Step 2: Get a list of selected indicators for each method at that quarter
selected_indicator_p_q = {}
for m in methods:
    d = results_dictionaries[m]
    df = d["varselect"]["selected_vars_quarters"]["selected"]["bic"][period]
    sel_idx = df[quarter]
    sel_idx = sel_idx[sel_idx.eq("X")].index
    selected_indicator_p_q[m] = pd.Index(sel_idx)

# Step 3: Create a matrix that shows the selected indicators ranked with the mse ranking
cols = list(model_results_details_sorted_mse_p_row_names)
selected_indicators_all_methods_mse_rank_p_q = pd.DataFrame("", index=methods, columns=cols)
for m, idx in selected_indicator_p_q.items():
    matched = pd.Index(cols).intersection(idx)
    selected_indicators_all_methods_mse_rank_p_q.loc[m, matched] = "X"

_save_xlsx(selected_indicators_all_methods_mse_rank_p_q, file_path_grouping_effect_q3_2020, f"mse_rank_{quarter.strftime('%Y%m%d')}")

#------------------------ 4. Get heatmap only for entire sample -------------#
# Step 4: Compute cross-correlation matrix for the filtered dataframe up to the selected quarter
filtered_full_sample_df = full_sample_df.loc[:,model_results_details_sorted_mse_p_row_names]
quarter_cc =  pd.Timestamp("2020-06-30") # Quarter of EN estimation
quarter_idx = filtered_full_sample_df.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df.iloc[0:0, :]

# Step 5: Plot cross-correlation matrix as a heatmap
cross_corr_matrix = filtered_full_sample_df_to_q.corr()
n = cross_corr_matrix.shape[0]
cell_inches = 0.16
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))
fig, ax = plt.subplots(figsize=(fig_size, fig_size))
sns.set_context("talk")
hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=False,
    yticklabels=False,
    rasterized=True,
    square=True
)

outdir = Path(file_path_grouping_effect_q3_2020)
outdir.mkdir(parents=True, exist_ok=True)
ax.set_title("Cross-Correlation Matrix (up to selected quarter)", pad=14)
plt.tight_layout()
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_full"
pdf_path = base.with_suffix(".pdf")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)

#------------------------ 3. Get heatmap only for EN02 -----------------------#
# Step 6: Filter the full sample df for the selected indicators of EN02
en02_row = selected_indicators_all_methods_mse_rank_p_q.loc["ElasticNet_02"]
en02_selected = en02_row[en02_row == "X"]
en02_selected_list = en02_selected.index.tolist()

# Step 4: Compute cross-correlation matrix only for the filtered dataframe up to the selected quarter
filtered_full_sample_df_en02 = full_sample_df.loc[:, en02_selected_list]
quarter_cc =  pd.Timestamp("2020-06-30")
quarter_idx = filtered_full_sample_df_en02.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[0:0, :]

# Step 5: Plot cross-correlation matrix as a heatmap
cross_corr_matrix = filtered_full_sample_df_to_q.corr()
n = cross_corr_matrix.shape[0]
cell_inches = 0.16
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))
fig, ax = plt.subplots(figsize=(fig_size, fig_size))
sns.set_context("talk")
hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=False,
    yticklabels=False,
    rasterized=True,
    square=True
)

outdir = Path(file_path_grouping_effect_q3_2020)
outdir.mkdir(parents=True, exist_ok=True)
ax.set_title("Cross-Correlation Matrix (up to selected quarter)", pad=14)
plt.tight_layout()
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_en02"
pdf_path = base.with_suffix(".pdf")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)
print("Saved:", pdf_path)

#%%
###############################################################################
#------------------------ Elastic Net Perfomance Recovery Q3 2020 (lamda en02)#
###############################################################################

#------------------------ 1. Get the selected plots for Q3 2020 --------------#

file_path_grouping_effect_len02 = f"{file_path_MA}/grouping_effect/q3_2020_len02"

methods= ["LASSO_len02", "ElasticNet_08_len02", "ElasticNet_05_len02", "ElasticNet_02_len02"]
period = "p2"
quarter = pd.Timestamp("2020-09-30")

# Step 1: get the top mse of the quarter
no_selection_dict = results_dictionaries["NoSelection"]
model_results_details_p = no_selection_dict["model"]["periods_details"]["selected"]["bic"][quarter][period]
model_results_details_sorted_mse_p = model_results_details_p.sort_values(by="mse", ascending=True)
model_results_details_sorted_mse_p_row_names = [
    name for name in model_results_details_sorted_mse_p.index.tolist()
    if name not in ['Average', 'Median', 'ci_lower', 'ci_upper']
]

# Step 2: Get a list of selected indicators for each method at that quarter
selected_indicator_p_q = {}
for m in methods:
    d = results_dictionaries[m]
    df = d["varselect"]["selected_vars_quarters"]["selected"]["bic"][period]
    sel_idx = df[quarter]
    sel_idx = sel_idx[sel_idx.eq("X")].index
    selected_indicator_p_q[m] = pd.Index(sel_idx)

# Step 3: Create a matrix that shows the selected indicators ranked with the mse ranking
cols = list(model_results_details_sorted_mse_p_row_names)
selected_indicators_all_methods_mse_rank_p_q = pd.DataFrame("", index=methods, columns=cols)
for m, idx in selected_indicator_p_q.items():
    matched = pd.Index(cols).intersection(idx)
    selected_indicators_all_methods_mse_rank_p_q.loc[m, matched] = "X"

_save_xlsx(selected_indicators_all_methods_mse_rank_p_q, file_path_grouping_effect_len02, f"mse_rank_{quarter.strftime('%Y%m%d')}")

#------------------------ 4. Get heatmap only for entire sample -------------#
# Step 4: Compute cross-correlation matrix for the filtered dataframe up to the selected quarter
filtered_full_sample_df = full_sample_df.loc[:,model_results_details_sorted_mse_p_row_names]
quarter_cc =  pd.Timestamp("2020-06-30")
quarter_idx = filtered_full_sample_df.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df.iloc[0:0, :]

# Step 5: Plot cross-correlation matrix as a heatmap
cross_corr_matrix = filtered_full_sample_df_to_q.corr()
n = cross_corr_matrix.shape[0]
cell_inches = 0.16
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))
fig, ax = plt.subplots(figsize=(fig_size, fig_size))
sns.set_context("talk")
hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=False,
    yticklabels=False,
    rasterized=True,
    square=True
)

outdir = Path(file_path_grouping_effect_len02)
outdir.mkdir(parents=True, exist_ok=True)
ax.set_title("Cross-Correlation Matrix (up to selected quarter)", pad=14)
plt.tight_layout()
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_full"
pdf_path = base.with_suffix(".pdf")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)
print("Saved:", pdf_path)

#------------------------ 3. Get heatmap only for EN02 -----------------------#
# Step 6: Filter the full sample df for the selected indicators of EN02
en02_row = selected_indicators_all_methods_mse_rank_p_q.loc["ElasticNet_02_len02"]
en02_selected = en02_row[en02_row == "X"]
en02_selected_list = en02_selected.index.tolist()

# Step 4: Compute cross-correlation matrix only for the filtered dataframe up to the selected quarter
filtered_full_sample_df_en02 = full_sample_df.loc[:, en02_selected_list]
quarter_cc =  pd.Timestamp("2020-06-30")
quarter_idx = filtered_full_sample_df_en02.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[0:0, :]

# Step 5: Plot cross-correlation matrix as a heatmap
cross_corr_matrix = filtered_full_sample_df_to_q.corr()
n = cross_corr_matrix.shape[0]
cell_inches = 0.16
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))
fig, ax = plt.subplots(figsize=(fig_size, fig_size))
sns.set_context("talk")
hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=False,
    yticklabels=False,
    rasterized=True,
    square=True
)

outdir = Path(file_path_grouping_effect_len02)
outdir.mkdir(parents=True, exist_ok=True)
ax.set_title("Cross-Correlation Matrix (up to selected quarter)", pad=14)
plt.tight_layout()
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_en02"
pdf_path = base.with_suffix(".pdf")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)
print("Saved:", pdf_path)

#------------------------ 3. Get heatmap only for EN02 (with labels) ---------
# Step 4: Filter to selected vars up to the selected quarter
filtered_full_sample_df_en02 = full_sample_df.loc[:, en02_selected_list]
quarter_cc = pd.Timestamp("2020-06-30")
quarter_idx = filtered_full_sample_df_en02.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[0:0, :]

# Step 5: Cross-correlation heatmap with labels kept at the edges
cross_corr_matrix = filtered_full_sample_df_to_q.corr()

n = cross_corr_matrix.shape[0]
cell_inches = 5
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))

fig, ax = plt.subplots(figsize=(fig_size, fig_size))

import seaborn as sns
sns.set_context("talk")

hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=True,
    yticklabels=True,
    rasterized=True,
    square=True,
    cbar=True,
)

ax.tick_params(axis="x", top=True, bottom=False, labeltop=True, labelbottom=False)
plt.setp(ax.get_xticklabels(), rotation=90, ha="center", va="bottom")
ax.tick_params(axis="y", left=True, right=False, labelleft=True, labelright=False)
plt.setp(ax.get_yticklabels(), rotation=0, ha="right", va="center")

ax.set_title("Cross-Correlation Matrix", pad=14)
plt.tight_layout(pad=0.5)

outdir = Path(file_path_grouping_effect_len02)
outdir.mkdir(parents=True, exist_ok=True)
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_en02_labeled_appendix"
pdf_path = base.with_suffix(".pdf")

plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)

#%%
###############################################################################
#------------------------ Elastic Net Perfomance Recovery Q2 2020 ------------#
###############################################################################

#------------------------ 1. Get the selected plots for Q2 2020 --------------#

file_path_grouping_effect_q2_2020 = f"{file_path_MA}/grouping_effect/q2_2020"

methods= ["LASSO", "ElasticNet_08", "ElasticNet_05", "ElasticNet_02"]
period = "p2"
quarter = pd.Timestamp("2020-06-30")

# Step 1: get the top mse of the quarter
no_selection_dict = results_dictionaries["NoSelection"]
model_results_details_p = no_selection_dict["model"]["periods_details"]["selected"]["bic"][quarter][period]
model_results_details_sorted_mse_p = model_results_details_p.sort_values(by="mse", ascending=True)
model_results_details_sorted_mse_p_row_names = [
    name for name in model_results_details_sorted_mse_p.index.tolist()
    if name not in ['Average', 'Median', 'ci_lower', 'ci_upper']
]

# Step 2: Get a list of selected indicators for each method at that quarter
selected_indicator_p_q = {}
for m in methods:
    d = results_dictionaries[m]
    df = d["varselect"]["selected_vars_quarters"]["selected"]["bic"][period]
    sel_idx = df[quarter]
    sel_idx = sel_idx[sel_idx.eq("X")].index
    selected_indicator_p_q[m] = pd.Index(sel_idx)

# Step 3: Create a matrix that shows the selected indicators ranked with the mse ranking
cols = list(model_results_details_sorted_mse_p_row_names)
selected_indicators_all_methods_mse_rank_p_q = pd.DataFrame("", index=methods, columns=cols)
for m, idx in selected_indicator_p_q.items():
    matched = pd.Index(cols).intersection(idx)
    selected_indicators_all_methods_mse_rank_p_q.loc[m, matched] = "X"

_save_xlsx(selected_indicators_all_methods_mse_rank_p_q, file_path_grouping_effect_q2_2020, f"mse_rank_{quarter.strftime('%Y%m%d')}")

#------------------------ 4. Get heatmap only for entire sample -------------#
# Step 4: Compute cross-correlation matrix for the filtered dataframe up to the selected quarter
filtered_full_sample_df = full_sample_df.loc[:,model_results_details_sorted_mse_p_row_names]
quarter_cc =  pd.Timestamp("2020-03-31")
quarter_idx = filtered_full_sample_df.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df.iloc[0:0, :]

# Step 5: Plot cross-correlation matrix as a heatmap
cross_corr_matrix = filtered_full_sample_df_to_q.corr()
n = cross_corr_matrix.shape[0]
cell_inches = 0.16
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))
fig, ax = plt.subplots(figsize=(fig_size, fig_size))
sns.set_context("talk")
hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=False,
    yticklabels=False,
    rasterized=True,
    square=True
)

outdir = Path(file_path_grouping_effect_q2_2020)
outdir.mkdir(parents=True, exist_ok=True)
ax.set_title("Cross-Correlation Matrix (up to selected quarter)", pad=14)
plt.tight_layout()
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_full"
pdf_path = base.with_suffix(".pdf")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)
print("Saved:", pdf_path)

#------------------------ 3. Get heatmap only for EN02 -----------------------#
# Step 6: Filter the full sample df for the selected indicators of EN02
en02_row = selected_indicators_all_methods_mse_rank_p_q.loc["ElasticNet_02"]
en02_selected = en02_row[en02_row == "X"]
en02_selected_list = en02_selected.index.tolist()

# Step 4: Compute cross-correlation matrix only for the filtered dataframe up to the selected quarter
filtered_full_sample_df_en02 = full_sample_df.loc[:, en02_selected_list]
quarter_cc =  pd.Timestamp("2020-03-31")
quarter_idx = filtered_full_sample_df_en02.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[0:0, :]

# Step 5: Plot cross-correlation matrix as a heatmap
cross_corr_matrix = filtered_full_sample_df_to_q.corr()
n = cross_corr_matrix.shape[0]
cell_inches = 0.16
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))
fig, ax = plt.subplots(figsize=(fig_size, fig_size))
sns.set_context("talk")
hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=False,
    yticklabels=False,
    rasterized=True,
    square=True
)

outdir = Path(file_path_grouping_effect_q2_2020)
outdir.mkdir(parents=True, exist_ok=True)
ax.set_title("Cross-Correlation Matrix (up to selected quarter)", pad=14)
plt.tight_layout()
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_en02"
pdf_path = base.with_suffix(".pdf")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)
print("Saved:", pdf_path)

#%%

#------------------------ 3. Get heatmap only for EN02 (with labels) ---------
# Step 4: Filter to selected vars up to the selected quarter
filtered_full_sample_df_en02 = full_sample_df.loc[:, en02_selected_list]
quarter_cc = pd.Timestamp("2020-03-31")
quarter_idx = filtered_full_sample_df_en02.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[0:0, :]

# Step 5: Cross-correlation heatmap with labels kept at the edges
cross_corr_matrix = filtered_full_sample_df_to_q.corr()

n = cross_corr_matrix.shape[0]
cell_inches = 5
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))

fig, ax = plt.subplots(figsize=(fig_size, fig_size))

import seaborn as sns
sns.set_context("talk")

hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=True,
    yticklabels=True,
    rasterized=True,
    square=True,
    cbar=True,
)

ax.tick_params(axis="x", top=True, bottom=False, labeltop=True, labelbottom=False)
plt.setp(ax.get_xticklabels(), rotation=90, ha="center", va="bottom")
ax.tick_params(axis="y", left=True, right=False, labelleft=True, labelright=False)
plt.setp(ax.get_yticklabels(), rotation=0, ha="right", va="center")

ax.set_title("Cross-Correlation Matrix", pad=14)
plt.tight_layout(pad=0.5)

outdir = Path(file_path_grouping_effect_q2_2020)
outdir.mkdir(parents=True, exist_ok=True)
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_en02_labeled_appendix"
pdf_path = base.with_suffix(".pdf")

plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)

print("Saved:", pdf_path)

#%%
###############################################################################
#------------------------ Elastic Net Perfomance Recovery Q2 2020 (2CV) ------#
###############################################################################

#------------------------ 1. Get the selected plots for Q2 2020 --------------#

file_path_grouping_effect_q2_2020_fix = f"{file_path_MA}/grouping_effect/q2_2020_l2cv"

methods= ["LASSO_l2cv", "ElasticNet_08_l2cv", "ElasticNet_05_l2cv", "ElasticNet_02_l2cv"]
period = "p2"
quarter = pd.Timestamp("2020-06-30")

# Step 1: get the top mse of the quarter
no_selection_dict = results_dictionaries["NoSelection"]
model_results_details_p = no_selection_dict["model"]["periods_details"]["selected"]["bic"][quarter][period]
model_results_details_sorted_mse_p = model_results_details_p.sort_values(by="mse", ascending=True)
model_results_details_sorted_mse_p_row_names = [
    name for name in model_results_details_sorted_mse_p.index.tolist()
    if name not in ['Average', 'Median', 'ci_lower', 'ci_upper']
]

# Step 2: Get a list of selected indicators for each method at that quarter
selected_indicator_p_q = {}
for m in methods:
    d = results_dictionaries[m]
    df = d["varselect"]["selected_vars_quarters"]["selected"]["bic"][period]
    sel_idx = df[quarter]
    sel_idx = sel_idx[sel_idx.eq("X")].index
    selected_indicator_p_q[m] = pd.Index(sel_idx)

# Step 3: Create a matrix that shows the selected indicators ranked with the mse ranking
cols = list(model_results_details_sorted_mse_p_row_names)
selected_indicators_all_methods_mse_rank_p_q = pd.DataFrame("", index=methods, columns=cols)
for m, idx in selected_indicator_p_q.items():
    matched = pd.Index(cols).intersection(idx)
    selected_indicators_all_methods_mse_rank_p_q.loc[m, matched] = "X"

_save_xlsx(selected_indicators_all_methods_mse_rank_p_q, file_path_grouping_effect_q2_2020_fix, f"mse_rank_{quarter.strftime('%Y%m%d')}")

#------------------------ 4. Get heatmap only for entire sample -------------#
# Step 4: Compute cross-correlation matrix for the filtered dataframe up to the selected quarter
filtered_full_sample_df = full_sample_df.loc[:,model_results_details_sorted_mse_p_row_names]
quarter_cc =  pd.Timestamp("2020-03-31")
quarter_idx = filtered_full_sample_df.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df.iloc[0:0, :]

# Step 5: Plot cross-correlation matrix as a heatmap
cross_corr_matrix = filtered_full_sample_df_to_q.corr()
n = cross_corr_matrix.shape[0]
cell_inches = 0.16
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))
fig, ax = plt.subplots(figsize=(fig_size, fig_size))
sns.set_context("talk")
hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=False,
    yticklabels=False,
    rasterized=True,
    square=True
)

outdir = Path(file_path_grouping_effect_q2_2020_fix)
outdir.mkdir(parents=True, exist_ok=True)
ax.set_title("Cross-Correlation Matrix (up to selected quarter)", pad=14)
plt.tight_layout()
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_full"
pdf_path = base.with_suffix(".pdf")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)
print("Saved:", pdf_path)

#------------------------ 3. Get heatmap only for EN02 -----------------------#
# Step 6: Filter the full sample df for the selected indicators of EN02
en02_row = selected_indicators_all_methods_mse_rank_p_q.loc["ElasticNet_02_l2cv"]
en02_selected = en02_row[en02_row == "X"]
en02_selected_list = en02_selected.index.tolist()

# Step 4: Compute cross-correlation matrix only for the filtered dataframe up to the selected quarter
filtered_full_sample_df_en02 = full_sample_df.loc[:, en02_selected_list]
quarter_cc =  pd.Timestamp("2020-03-31")
quarter_idx = filtered_full_sample_df_en02.index.get_loc(quarter_cc)
if quarter_idx > 0:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[:quarter_idx, :]
else:
    filtered_full_sample_df_to_q = filtered_full_sample_df_en02.iloc[0:0, :]

# Step 5: Plot cross-correlation matrix as a heatmap
cross_corr_matrix = filtered_full_sample_df_to_q.corr()
n = cross_corr_matrix.shape[0]
cell_inches = 0.16
max_inches = 40
fig_size = min(max_inches, max(6, n * cell_inches))
fig, ax = plt.subplots(figsize=(fig_size, fig_size))
sns.set_context("talk")
hm = sns.heatmap(
    cross_corr_matrix,
    ax=ax,
    annot=False,
    cmap="coolwarm",
    center=0,
    xticklabels=False,
    yticklabels=False,
    rasterized=True,
    square=True
)

outdir = Path(file_path_grouping_effect_q2_2020_fix)
outdir.mkdir(parents=True, exist_ok=True)
ax.set_title("Cross-Correlation Matrix (up to selected quarter)", pad=14)
plt.tight_layout()
base = outdir / f"crosscorr_{quarter_cc:%Y%m%d}_{period}_en02"
pdf_path = base.with_suffix(".pdf")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.01)
plt.close(fig)
print("Saved:", pdf_path)

#%%

###############################################################################
###############################################################################
######################### Appendix ############################################
###############################################################################
###############################################################################

###############################################################################
#------------------------ Cross Correlation matrix ---------------------------#
###############################################################################

file_path_cross_corr = f"{file_path_MA}/appendix/cross_correlation_matrix"
Path(file_path_cross_corr).mkdir(parents=True, exist_ok=True)

selected_ts = pd.Timestamp("2020-03-31")

outdir = Path(file_path_cross_corr)
outdir.mkdir(parents=True, exist_ok=True)

cell_inches = 0.16
max_inches = 40

date_prefix = f"{selected_ts:%Y%m%d}_"
q_str = selected_ts.to_period("Q")

def mask_upto(idx, cutoff_ts: pd.Timestamp):
    if isinstance(idx, pd.PeriodIndex):
        return idx.to_timestamp(how="end") <= cutoff_ts
    return pd.to_datetime(idx) <= cutoff_ts

for period, cols in release_periods_dict.items():
    cols_set = set(cols)
    cols_in_order = [c for c in full_sample_df.columns if c in cols_set]
    row_mask = mask_upto(full_sample_df.index, selected_ts)
    df_p = full_sample_df.loc[row_mask, cols_in_order].apply(pd.to_numeric, errors="coerce")
    corr = df_p.corr(method="pearson", min_periods=1)
    n = corr.shape[0]
    fig_size = min(max_inches, max(6, n * cell_inches))

    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    sns.set_context("talk")
    sns.heatmap(
        corr,
        ax=ax,
        annot=False,
        cmap="coolwarm",
        center=0,
        xticklabels=False,
        yticklabels=False,
        rasterized=True,
        square=True,
    )
    ax.set_title(f"Cross-Correlation Matrix — {period} (≤ {selected_ts:%Y-%m-%d}, {q_str})", pad=14)
    plt.tight_layout()
    base = outdir / f"crosscorr_{date_prefix}{period}"
    plt.savefig(base.with_suffix(".pdf"), format="pdf", bbox_inches="tight", pad_inches=0.01)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    sns.set_context("talk")
    sns.heatmap(
        corr,
        ax=ax,
        annot=False,
        cmap="coolwarm",
        center=0,
        xticklabels=False,
        yticklabels=False,
        rasterized=True,
        square=True,
    )
    step = 5 if n >= 25 else 1
    positions = np.arange(0, n, step)
    ax.set_xticks(positions)
    ax.set_yticks(positions)
    ax.set_xticklabels(corr.columns[::step], rotation=90, ha="center", fontsize=6)
    ax.set_yticklabels(corr.index[::step], fontsize=6)
    ax.set_title(f"Cross-Correlation Matrix — {period} (≤ {selected_ts:%Y-%m-%d}, {q_str}; every {step}th label)", pad=14)
    plt.tight_layout()
    base_labeled = outdir / f"crosscorr_{date_prefix}{period}_every{step}"
    plt.savefig(base_labeled.with_suffix(".pdf"), format="pdf", bbox_inches="tight", pad_inches=0.01)
    plt.close(fig)

    corr.to_csv(outdir / f"crosscorr_{date_prefix}{period}.csv", float_format="%.6f")

    print(f"Saved heatmaps for {period} up to {selected_ts:%Y-%m-%d} ({q_str})")

#%%
###############################################################################
#------------------------ Outcome Plots (all methods) (lamda en02) -----------#
###############################################################################

weights = ["periods_mseweight", "periods_avg"]
periods = ["p1", "p2", "p3"]

file_path_plots_period_stack = f"{file_path_MA}/appendix/gdp_nowcast_oof_period_plot_len02"
plotter_methods = ResultsPlotter(output_dir=file_path_plots_period_stack, fmt="pdf", dpi=150)

method_label_map = {
    "LASSO_len02": "LASSO (λ=EN02)",
    "ElasticNet_08_len02": "EN08 (λ=EN02)",
    "ElasticNet_05_len02": "EN05 (λ=EN02)",
    "ElasticNet_02_len02": "EN02 (λ=EN02)",
    "NoSelection": "NPS"
}

methods= ["LASSO_len02", "ElasticNet_08_len02", "ElasticNet_05_len02", "ElasticNet_02_len02"]

all_methods_one_period_plot = {}

for weight in weights:
    all_methods_one_period_plot.setdefault(weight, {})
    for period in periods:
        filename = f"all_methods_{period}_{weight}_oos"
        fig = plotter_methods.plot_one_period_all_methods(
            results_dictionaries=results_dictionaries,
            methods=methods,
            weight=weight,
            period=period,
            filename=filename,
            method_label_map=method_label_map,
            oos_start=2019,
            oos_end=2024,
        )
        all_methods_one_period_plot[weight][period] = fig

#%%
###############################################################################
#------------------------ Outcome Plots (all methods) (lamda 2CV) -----------#
###############################################################################

weights = ["periods_mseweight", "periods_avg"]
periods = ["p1", "p2", "p3"]

file_path_plots_period_stack = f"{file_path_MA}/appendix/gdp_nowcast_oof_period_plot_l2cv"
plotter_methods = ResultsPlotter(output_dir=file_path_plots_period_stack, fmt="pdf", dpi=150)

method_label_map = {
    "LASSO_l2cv": "LASSO (λ=2CV)",
    "ElasticNet_08_l2cv": "EN08 (λ=2CV)",
    "ElasticNet_05_l2cv": "EN05 (λ=2CV)",
    "ElasticNet_02_l2cv": "EN02 (λ=2CV)",
}

methods= ["LASSO_l2cv", "ElasticNet_08_l2cv", "ElasticNet_05_l2cv", "ElasticNet_02_l2cv"]

all_methods_one_period_plot = {}

for weight in weights:
    all_methods_one_period_plot.setdefault(weight, {})
    for period in periods:
        filename = f"all_methods_{period}_{weight}_oos"
        fig = plotter_methods.plot_one_period_all_methods(
            results_dictionaries=results_dictionaries,
            methods=methods,
            weight=weight,
            period=period,
            filename=filename,
            method_label_map=method_label_map,
            oos_start=2019,
            oos_end=2024,
        )
        all_methods_one_period_plot[weight][period] = fig

#%%
###############################################################################
#---------------------- Outcome Plots: AR(4) only ----------------------------#
###############################################################################

weight = "periods_mseweight"
period = "p1"

methods= ["LASSO"]
ar4_results_dictionary = results_dictionaries[methods[0]]

file_path_plots_ar4 = f"{file_path_MA}/appendix/gdp_pred_oof_period_plot_ar4"
plotter_ar4_pdf = ResultsPlotter(output_dir=file_path_plots_ar4, fmt="pdf", dpi=150)

filename = f"ar4_oos"
fig = plotter_ar4_pdf.plot_one_period_ar4(
    results_dictionary=ar4_results_dictionary,
    weight=weight,
    period=period,
    filename=filename,
    oos_start=2019,
    oos_end=2024,
)

#%%




































