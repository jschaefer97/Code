#%%
from utils.getdata import _load_object, _save_xlsx
from utils.resultsrender import save_period_rel_rmse_panels
from utils.resultsplotter import ResultsPlotter
import re

import pandas as pd
import numpy as np

from main import FILE_PATH

#%%

###############################################################################
###############################################################################
######################### Result Outputs ######################################
###############################################################################
###############################################################################

file_path_inload = f"{FILE_PATH}/output/results/"
file_path_MA = f"{FILE_PATH}/output/results/MA/appendix/"

#%%

results_spec_nl_c = {
    # Baseline spec
    "LASSO_nl_c": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a1_qw4_nl_c",
    "ElasticNet_08_nl_c": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a0.8_qw4_nl_c",
    "ElasticNet_05_nl_c": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a0.5_qw4_nl_c",
    "ElasticNet_02_nl_c": "NDv5_3p_v2_2002Q2_2024Q4_GDP_pyentscv_tcv5on10_a0.2_qw4_nl_c",
    "NoSelection_nl_c": "NDv5_3p_v2_2002Q2_2024Q4_GDP_nsel_qw4_nl_c",
}

# Load in the dictionaries
results_dictionaries = dict()
for method in results_spec_nl_c.keys():
    spec = results_spec_nl_c[method]
    results_dictionaries[method] = _load_object(f"{file_path_inload}/{spec}", f"results_dict_{spec}.pkl")

#%%
###############################################################################
#------------------------ Relative RMSE Table Full Years ---------------------#
###############################################################################
file_path_era_rmse_tables = f"{file_path_MA}/relative_rmse_table_with_lags"

weights = ["periods_mseweight", "periods_avg"]
pretty_cols = {"LASSO_nl_c": "LASSO", 
                "ElasticNet_08_nl_c": "EN08", 
                "ElasticNet_05_nl_c": "EN05", 
                "ElasticNet_02_nl_c": "EN02", 
                "NoSelection_nl_c": "NPS"}
methods_order = ["LASSO_nl_c", "ElasticNet_08_nl_c", "ElasticNet_05_nl_c", "ElasticNet_02_nl_c", "NoSelection_nl_c"]  # rows
eras = ["covid", "post_covid", "all"]                   # columns

covid_start = pd.Timestamp("2020-03-31")   # 2020Q1
covid_end   = pd.Timestamp("2021-03-31")   # 2021Q1
post_start  = pd.Timestamp("2021-06-30")   # 2021Q2
post_end    = pd.Timestamp("2024-12-31")   # 2024Q4

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
        # tables_by_h[h_label] = df_out.round(2)
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

    # Save XLSX per horizon, include weight in filename
    for h in ("h0", "h1", "h2"):
        if h not in tables_by_h:
            print(f"[warn] Horizon '{h}' missing for weight='{weight}', skipping this sheet.")
            continue
        df_h = tables_by_h[h]
        _save_xlsx(df_h, file_path_era_rmse_tables, f"era_rmse_{h}_{weight}")

    # One LaTeX table per weight
    # Make label unique & TeX-safe-ish (your save function sanitizes, but this keeps it readable)
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


# %%
