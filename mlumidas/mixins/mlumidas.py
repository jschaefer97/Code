import re
from loguru import logger
import pandas as pd
from sympy import series  # unused import preserved to match your environment
from tqdm import tqdm
import numpy as np

from utils.checks import Checks

from mlumidas.select.pyentscv import PYENTSCV
from mlumidas.select.pyhardt import PYHARDT
from mlumidas.select.pyen import PYEN
from mlumidas.select.pyadal import PYADAL

from mlumidas.utils.modelgrid import get_model_grid_dict
from utils.utils import get_formatted_date
from mlumidas.models.umidas import UMidas
from mlumidas.models.benchmarkar4 import BenchmarkAR4
from mlumidas.models.benchmarkar2 import BenchmarkAR2
from data.datautils.statistics import Statistics
from data.datautils.statistics import Statistics


class MLUMidasMixin:

    def get_results_dict(
        self,
        varselection_method,
        fwr_idx_dict,
        release_periods_dict,
        y_var,

        # --- Varselect -------------------------------------#
        full_sample_df,
        alpha,
        tcv_splits,
        test_size,
        gap,
        max_train_size,
        cv,
        alphas,
        max_iter,
        random_state,
        with_mean,
        with_std,
        fit_intercept,
        selection_rule,
        se_factor,
        threshold_divisor,
        coef_tol,
        k_indicators,
        lambda_fix,

        # --- Model ----------------------------------------#
        series_model_dataframes,
        release_latest_block_dict,  # kept in signature for compatibility, no longer used
        meta,
        umidas_model_lags,
        start_date,
        end_date,
        remove_non_stat_fwr,
        confidence,

        # --- Cache ----------------------------------------#
        model_cache,

        mse_history,                
        window_quarters=4,          # rolling window length for MSFE
    ):
        # ---- EARLY HARD CHECK ON mse_history ---- #
        if not isinstance(mse_history, dict) or len(mse_history) == 0:
            raise ValueError(
                "mse_history is missing or empty. Provide a dict keyed by "
                "(top_level_cache_key, freq, series, period_key, crit, transformation) "
                "with a pandas Series of squared errors indexed by quarter."
            )

        formatted_start_date = get_formatted_date(start_date)
        formatted_end_date = get_formatted_date(end_date)
        top_level_cache_key = f"{formatted_start_date}_to_{formatted_end_date}_{y_var}_lags_{umidas_model_lags}"

        # normalize the cache so we can reliably look things up
        cache_dict = self._normalize_model_cache(model_cache)

        results_dict = {"varselect": {}, "model": {}}

        period_raw_names_dict = {}
        period_meta_names_dict = {}
        all_full_lst = set()
        all_basenames_lst = set()

        # store per-criterion results
        criteria = ["bic"]  # ["bic", "aic", "adj_r2"]

        # legacy flat store (kept to minimize changes)
        period_model_results_dfs = {c: {} for c in criteria}

        # detailed per-(quarter,period) frames for 'selected' only
        period_model_results_dfs_dict = {
            "selected": {c: {} for c in criteria},
        }

        # aggregated (avg/median) – filled later
        period_model_results_avg_dfs_dict = {
            "selected": {c: {} for c in criteria},
        }
        period_model_results_median_dfs_dict = {
            "selected": {c: {} for c in criteria},
        }

        # Pooled (MSFE-weighted) time series (selected only)
        mseweight_store = {"selected": {c: {} for c in criteria}}
        for c in criteria:
            for p in Checks.sorted_periods(list(release_periods_dict.keys())):
                mseweight_store["selected"][c][p] = {}

        # Rich per-series diagnostics DataFrames
        mseweight_details_dfs_dict = {"selected": {c: {} for c in criteria}}

        quarters = sorted(fwr_idx_dict.keys())
        periods_sorted = Checks.sorted_periods(list(release_periods_dict.keys()))

        logger.info("--------------------------------------------------------------------------------")
        logger.info("--------------------------------------------------------------------------------")
        logger.info(f"START Selection '{varselection_method}'")
        logger.info("--------------------------------------------------------------------------------")
        logger.info("--------------------------------------------------------------------------------")

        # --- hold AR(4) results across quarters --- #
        quarter_y_var_ar4_results_dict = {}
        lambda_cv_dict = {}

        for quarter in tqdm(quarters, desc="Running ML-U-MIDAS"):

            train_idx = fwr_idx_dict[quarter]["train_idx"]
            test_idx = fwr_idx_dict[quarter]["test_idx"]

            # RESET per-quarter containers so nothing leaks between quarters
            period_raw_names_dict[quarter] = {}
            period_meta_names_dict[quarter] = {}
            lambda_cv_dict[quarter] = {}

            period_series_model_selected_results_dict = {c: {} for c in criteria}

            # ensure per-quarter slots exist
            for c in criteria:
                period_model_results_dfs[c][quarter] = {}
            for c in criteria:
                period_model_results_dfs_dict["selected"][c][quarter] = {}

            for period in tqdm(periods_sorted, desc="Running periods"):
                # Also ensure a clean slate for each period within the current quarter
                logger.info(f"--- Running \"{varselection_method}\" selection for Quarter {quarter} | Period {period} ---")

                for c in criteria:
                    period_series_model_selected_results_dict[c][period] = {}

                X, y = self._to_ragged_edge_df(
                    train_idx,
                    period,
                    release_periods_dict,
                    y_var,
                    full_sample_df,
                    remove_non_stat_fwr=remove_non_stat_fwr,
                    confidence=confidence,
                )

                # ---------------------------------------------------#
                # --- Varselect -------------------------------------#
                # ---------------------------------------------------#

                varselect_model = None
                varselect_model_out = None

                if varselection_method == "pyentscv":
                    varselect_model = PYENTSCV(
                        l1_ratio=alpha,
                        tcv_splits=tcv_splits,
                        test_size=test_size,
                        gap=gap,
                        max_train_size=max_train_size,
                        alphas=alphas,
                        max_iter=max_iter,
                        random_state=random_state,
                        with_mean=with_mean,
                        with_std=with_std,
                        fit_intercept=fit_intercept,
                        selection_rule=selection_rule,
                        # se_factor=se_factor,
                        threshold_divisor=threshold_divisor,
                        coef_tol=coef_tol,
                        k_indicators=k_indicators,
                    )
                elif varselection_method == "pyen":
                    varselect_model = PYEN(
                        l1_ratio=alpha,
                        max_iter=max_iter,
                        random_state=random_state,
                        with_mean=with_mean,
                        with_std=with_std,
                        fit_intercept=fit_intercept,
                        selection_rule=selection_rule,
                        se_factor=se_factor,
                        threshold_divisor=threshold_divisor,
                        coef_tol=coef_tol,
                        lambda_fix=lambda_fix,
                    )

                elif varselection_method == "pyadal":
                    varselect_model = PYADAL(
                        tcv_splits=tcv_splits,
                        test_size=test_size,
                        gap=gap,
                        max_train_size=max_train_size,
                        alphas=alphas,
                        max_iter=max_iter,
                        with_mean=with_mean,
                        with_std=with_std,
                        fit_intercept=fit_intercept
                    )

                elif varselection_method == "pyhardt":
                    varselect_model = PYHARDT(
                        y_var=y_var,
                        significance_level=alpha,
                        k_indicators=k_indicators,
                    )
                elif varselection_method == "no_selection":
                    varselect_model_out = {"selected_features": X.columns.tolist()}
                else:
                    raise ValueError(f"Unknown method: {varselection_method}")

                if varselect_model is not None:
                    varselect_model.fit(X, y)
                    varselect_model_out = varselect_model.get_result()

                # ------- Get Varselect Output ----------------------#

                selected_vars = varselect_model_out.get("selected_features", [])
                coef_series_sel = varselect_model_out.get("coef_series_selected", pd.Series(dtype=float))
                lambda_cv = varselect_model_out.get("best_alpha", pd.Series(dtype=float))

                lambda_cv_dict[quarter][period] = lambda_cv

                # Guarantee same order/length as selected_vars
                coef_values = coef_series_sel.reindex(selected_vars).to_numpy(dtype=float)

                coef_map = {}
                for raw_name, coef_val in zip(selected_vars, coef_values):
                    coef_map[raw_name] = float(coef_val) if np.isfinite(coef_val) else np.nan

                bases = self._get_meta_names(selected_vars, y_var)

                period_raw_names_dict[quarter][period] = selected_vars
                release_selected_block_dict = self._get_release_selected_block_dict(period_raw_names_dict, meta)
                period_meta_names_dict[quarter][period] = sorted(bases)

                self._update_all_selected_lst(selected_vars, y_var, all_full_lst, all_basenames_lst, bases)

                # ---------------------------------------------------#
                # --- Benchmark Model (per quarter) -----------------#
                # ---------------------------------------------------#
                y_var_quarter_df = series_model_dataframes[y_var]["full_model_df"]
                train_data_ar4 = y_var_quarter_df.loc[train_idx]
                test_data_ar4  = y_var_quarter_df.loc[test_idx]

                ar4_model_inst = BenchmarkAR4(                 
                    y_var=y_var,
                    train_data=train_data_ar4,
                    test_data=test_data_ar4,
                )

                ar4_model = ar4_model_inst.fit()
                y_actual_ar4, y_pred_ar4, mse_ar4 = ar4_model_inst.predict(ar4_model)

                quarter_y_var_ar4_results_dict[quarter] = {
                    "y_actual_ar4": y_actual_ar4,
                    "y_pred_ar4": y_pred_ar4,
                    "mse_ar4": mse_ar4
                }

                # ---------------------------------------------------#
                # --- Model (using cache) ---------------------------#
                # ---------------------------------------------------#

                # ---------- SELECTED block (per selected name) -----#
                for series_selected_name in period_raw_names_dict[quarter][period]:

                    if Checks.get_series_meta_name(series_selected_name) == y_var:
                        continue

                    selected_period = release_selected_block_dict[quarter][period][series_selected_name]
                    series_meta_name_selected = Checks.get_series_meta_name(series_selected_name)

                    freq_key_sel = self._freq_for(series_meta_name_selected, meta)
                    transformation_key_sel = self._transformation_for(series_meta_name_selected, freq_key_sel, meta)
                    component_key_sel = self._category_for(series_meta_name_selected, meta, "component")
                    subcategory_key_sel = self._category_for(series_meta_name_selected, meta, "subcategory")
                    category_key_sel = self._category_for(series_meta_name_selected, meta, "category")

                    for crit in criteria:
                        y_actual_s, y_pred_s, mse_s, spec_s = self._get_cached_predictions(
                            cache_dict=cache_dict,
                            top_level_cache_key=top_level_cache_key,
                            quarter=quarter,
                            freq_key=freq_key_sel,
                            series=series_meta_name_selected,
                            period_key=selected_period,
                            crit=crit,
                            transformation_key=transformation_key_sel,
                        )
                        if y_pred_s is None:
                            logger.warning(f"[cache-miss/preds] (selected) {(top_level_cache_key, quarter, freq_key_sel, series_meta_name_selected, selected_period, crit, transformation_key_sel)}")
                            continue

                        period_series_model_selected_results_dict[crit][period][series_selected_name] = {
                            "y_actual": y_actual_s,
                            "y_pred": y_pred_s,
                            "mse": mse_s,
                            "ar4": quarter_y_var_ar4_results_dict[quarter]["y_pred_ar4"] if quarter_y_var_ar4_results_dict.get(quarter) else None,
                            "coef": coef_map.get(series_selected_name, np.nan),
                            "component": component_key_sel if component_key_sel else "no_component",
                            "subcategory": subcategory_key_sel if subcategory_key_sel else "no_subcategory",
                            "category": category_key_sel if category_key_sel else "no_category",
                            "spec": spec_s
                        }

                # ---------------------------------------------------#
                # --- Building results dict + pooled MSFE -----------#
                # ---------------------------------------------------#
                dict_name = "selected"
                for crit in criteria:
                    if period in period_series_model_selected_results_dict[crit]:
                        period_model_results_df = self._to_period_model_results_df(
                            period_series_model_selected_results_dict[crit], period
                        )
                    else:
                        period_model_results_df = pd.DataFrame()

                    # Guard: warn if y_actual differs within (quarter, period) – ignore CI rows
                    if "y_actual" in period_model_results_df.columns:
                        mask = ~period_model_results_df.index.isin(["Average", "Median", "ci_lower", "ci_upper"])
                        y_actual_series = pd.Series(period_model_results_df.loc[mask, "y_actual"])
                        nunique = y_actual_series.nunique(dropna=False)
                        if nunique > 1:
                            logger.warning(
                                f"[quarter={quarter} | period={period}] y_actual not unique across series. "
                                f"Counts: {y_actual_series.value_counts(dropna=False).to_dict()}"
                            )

                    period_model_results_df = self._append_avg_median_rows(period_model_results_df)
                    period_model_results_dfs[crit][quarter][period] = period_model_results_df
                    period_model_results_dfs_dict[dict_name][crit][quarter][period] = period_model_results_df

                    # --- Compute pooled MSFE-weighted value (pure inverse-MSFE) --- #
                    if not period_model_results_df.empty and "y_pred" in period_model_results_df.columns:
                        # Rows we can weight over (exclude CI/summary rows)
                        rows = [r for r in period_model_results_df.index if r not in ("Average", "Median", "ci_lower", "ci_upper")]
                        if rows:
                            # unified y_actual for this quarter/period
                            try:
                                y_actual_vals = pd.to_numeric(period_model_results_df.loc[rows, "y_actual"], errors="coerce").dropna()
                                y_actual_val = float(y_actual_vals.iloc[0]) if not y_actual_vals.empty else np.nan
                            except Exception:
                                y_actual_val = np.nan

                            # Collect per-row info needed to pull MSFE history (only 'selected')
                            row_info = []
                            for r in rows:
                                smn = Checks.get_series_meta_name(r)
                                fq = self._freq_for(smn, meta)
                                per_key = release_selected_block_dict[quarter][period].get(r)
                                trans = self._transformation_for(smn, fq, meta)
                                ypred = pd.to_numeric(pd.Series([period_model_results_df.at[r, "y_pred"]]).iloc[0], errors="coerce")
                                row_info.append({
                                    "row": r, "series": smn, "freq": fq,
                                    "period_key": per_key, "trans": trans,
                                    "y_pred": float(ypred) if np.isfinite(ypred) else np.nan
                                })

                            # Compute MSFE window per row across ALL rows (single group)
                            cq = pd.Timestamp(quarter)
                            eps = 1e-12
                            msfe_mean_map = {}
                            past_mse_window_map = {}

                            for ri in row_info:
                                hkey = (top_level_cache_key, ri["freq"], ri["series"], ri["period_key"], crit, ri["trans"])
                                s = mse_history.get(hkey)
                                if s is None or s.empty:
                                    continue
                                # only quarters strictly before current quarter
                                s_past = s[s.index < cq]
                                if s_past.empty:
                                    continue
                                s_win = s_past.tail(int(window_quarters))
                                if s_win.empty:
                                    continue
                                msfe_mean_map[ri["row"]] = float(pd.to_numeric(s_win, errors="coerce").mean())
                                past_mse_window_map[ri["row"]] = [
                                    float(x) if np.isfinite(x) else np.nan
                                    for x in pd.to_numeric(s_win, errors="coerce").tolist()
                                ]

                            # Pure inverse-MSFE weights across all rows with MSFE estimates
                            msfe_series = pd.Series(msfe_mean_map, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
                            inv_msfe = 1.0 / (msfe_series + eps)
                            inv_sum = float(inv_msfe.sum()) if len(inv_msfe) else np.nan
                            base_w = inv_msfe / inv_msfe.sum() if len(inv_msfe) else pd.Series(dtype=float)
                            w_final = base_w.copy()
                            survivors = set(w_final.index)

                            # pooled value over rows that have y_pred
                            y_now_all = pd.to_numeric(
                                period_model_results_df.loc[w_final.index.intersection(period_model_results_df.index), "y_pred"],
                                errors="coerce"
                            ).dropna()
                            if not y_now_all.empty:
                                w_use = w_final.reindex(y_now_all.index).fillna(0.0)
                                if w_use.sum() > 0:
                                    w_use = w_use / w_use.sum()
                                pooled_value = float((w_use * y_now_all).sum())
                            else:
                                # If there are weights but no numeric y_pred, treat as an error as well
                                raise ValueError(
                                    f"No numeric y_pred available for weighted pooling at quarter={quarter}, period={period}, crit={crit}."
                                )

                            # Build per-series diagnostics table
                            weights_detail_rows = []
                            for ri in row_info:
                                r = ri["row"]
                                msfe_mean = msfe_mean_map.get(r, np.nan)
                                inv_i = (1.0 / (msfe_mean + eps)) if np.isfinite(msfe_mean) else np.nan
                                in_survivors = r in survivors
                                w_fin = w_final.get(r, 0.0) if w_final is not None else np.nan
                                y_pred_orig = ri["y_pred"]
                                y_pred_contrib = (w_fin * y_pred_orig) if (np.isfinite(w_fin) and np.isfinite(y_pred_orig)) else np.nan

                                weights_detail_rows.append({
                                    "series_meta_name": ri["series"],
                                    "row_name": r,  # index used in period df
                                    "freq": ri["freq"],
                                    "period_key_used": ri["period_key"],   # lookup transparency
                                    "transformation": ri["trans"],
                                    "window_quarters": int(window_quarters),
                                    "past_mse_window": past_mse_window_map.get(r, np.nan),  # list or NaN
                                    "msfe_mean": msfe_mean,
                                    "inv_msfe": inv_i if in_survivors else (np.nan if r not in msfe_mean_map else (1.0 / (msfe_mean + eps))),
                                    "inv_msfe_sum_survivors": inv_sum,
                                    "weight_final": w_fin,
                                    "y_pred_original": y_pred_orig,
                                    "y_pred_weighted_contribution": y_pred_contrib,
                                    "y_actual": y_actual_val,
                                })

                            weights_df = pd.DataFrame(weights_detail_rows).set_index("row_name")

                            # Append a pooled summary row
                            pooled_row = pd.Series({
                                "series_meta_name": "__pool__",
                                "freq": "",
                                "period_key_used": "",
                                "transformation": "",
                                "window_quarters": int(window_quarters),
                                "past_mse_window": np.nan,
                                "msfe_mean": np.nan,
                                "inv_msfe": np.nan,
                                "inv_msfe_sum_survivors": inv_sum,
                                "weight_final": float(pd.to_numeric(weights_df["weight_final"], errors="coerce").sum()) if not weights_df.empty else np.nan,
                                "y_pred_original": np.nan,
                                "y_pred_weighted_contribution": pooled_value,
                                "y_actual": y_actual_val,
                            }, name="__POOLED__")

                            weights_df = pd.concat([weights_df, pooled_row.to_frame().T], axis=0)

                            # Save details table for inspection
                            mseweight_details_dfs_dict["selected"][crit].setdefault(quarter, {})
                            mseweight_details_dfs_dict["selected"][crit][quarter][period] = weights_df

                            # Save pooled time-series point
                            if np.isfinite(pooled_value):
                                q_ts = pd.Timestamp(quarter)
                                y_pred_ar4_val = quarter_y_var_ar4_results_dict.get(quarter, {}).get("y_pred_ar4", np.nan)
                                y_act_ar4_val  = quarter_y_var_ar4_results_dict.get(quarter, {}).get("y_actual_ar4", np.nan)
                                mse_ar4_val    = quarter_y_var_ar4_results_dict.get(quarter, {}).get("mse_ar4", np.nan)

                                mseweight_store["selected"][crit][period][q_ts] = {
                                    "y_actual": y_actual_val,
                                    "y_pred": pooled_value,
                                    "y_actual_ar4": y_act_ar4_val,
                                    "y_pred_ar4": y_pred_ar4_val,
                                    "mse_ar4": mse_ar4_val,
                                }

        # attach detailed period dfs
        results_dict["model"]["periods_details"] = period_model_results_dfs_dict

        # --- Attach the mseweight details (selected only) --- #
        results_dict["model"]["periods_details"]["mseweight"] = mseweight_details_dfs_dict

        # --- Build pooled (mse-weighted) DataFrames per period --- #
        period_model_results_mseweight_dfs_dict = {
            "selected": {c: {} for c in criteria},
        }
        for crit in criteria:
            for period in periods_sorted:
                data = mseweight_store["selected"][crit][period]
                if not data:
                    period_model_results_mseweight_dfs_dict["selected"][crit][period] = pd.DataFrame()
                    continue

                q_idx = sorted(data.keys())
                y_pred_series = pd.Series({q: data[q]["y_pred"] for q in q_idx}, dtype=float)
                y_act_series  = pd.Series({q: data[q]["y_actual"] for q in q_idx}, dtype=float)
                out_df = pd.DataFrame({"y_actual": y_act_series, "y_pred": y_pred_series}).sort_index()

                with np.errstate(invalid="ignore"):
                    out_df["mse"] = (out_df["y_actual"] - out_df["y_pred"]) ** 2

                # attach AR4 diagnostics if present
                y_act_ar4  = pd.Series({q: data[q]["y_actual_ar4"] for q in q_idx}, dtype=float)
                y_pred_ar4 = pd.Series({q: data[q]["y_pred_ar4"]   for q in q_idx}, dtype=float)
                mse_ar4    = pd.Series({q: data[q]["mse_ar4"]      for q in q_idx}, dtype=float)

                out_df["y_actual_ar4"] = y_act_ar4.reindex(out_df.index)
                out_df["y_pred_ar4"]   = y_pred_ar4.reindex(out_df.index)
                out_df["mse_ar4"]      = mse_ar4.reindex(out_df.index)
                with np.errstate(divide="ignore", invalid="ignore"):
                    out_df["rmse"] = (out_df["mse"] / out_df["mse_ar4"]).replace([np.inf, -np.inf], np.nan)

                out_df["avg_rmse_y"] = out_df["rmse"].groupby(out_df.index.year).transform("mean")
                out_df["avg_mse_y"]  = out_df["mse"].groupby(out_df.index.year).transform("mean")

                period_model_results_mseweight_dfs_dict["selected"][crit][period] = out_df

        # --- build per-period summaries (avg/median) per criterion, for selected --- #
        for crit in criteria:
            for period in periods_sorted:
                avg_df, median_df = self._to_avg_median_dfs(
                    results_dict["model"]["periods_details"]["selected"][crit],
                    period,
                    metrics=("y_actual", "y_pred", "mse"),
                )

                avg_df = avg_df.copy()
                avg_df["y_actual_ar4"] = avg_df.index.map(
                    lambda q: quarter_y_var_ar4_results_dict.get(q, {}).get("y_actual_ar4", np.nan)
                )
                avg_df["y_pred_ar4"] = avg_df.index.map(
                    lambda q: quarter_y_var_ar4_results_dict.get(q, {}).get("y_pred_ar4", np.nan)
                )
                avg_df["mse_ar4"] = avg_df.index.map(
                    lambda q: quarter_y_var_ar4_results_dict.get(q, {}).get("mse_ar4", np.nan)
                )
                with np.errstate(divide="ignore", invalid="ignore"):
                    avg_df["rmse"] = (avg_df["mse"] / avg_df["mse_ar4"]).replace([np.inf, -np.inf], np.nan)
                avg_df["avg_rmse_y"] = avg_df["rmse"].groupby(avg_df.index.year).transform("mean")
                avg_df["avg_mse_y"] = avg_df["mse"].groupby(avg_df.index.year).transform("mean")

                median_df = median_df.copy()
                median_df["y_actual_ar4"] = median_df.index.map(
                    lambda q: quarter_y_var_ar4_results_dict.get(q, {}).get("y_actual_ar4", np.nan)
                )
                median_df["y_pred_ar4"] = median_df.index.map(
                    lambda q: quarter_y_var_ar4_results_dict.get(q, {}).get("y_pred_ar4", np.nan)
                )
                median_df["mse_ar4"] = median_df.index.map(
                    lambda q: quarter_y_var_ar4_results_dict.get(q, {}).get("mse_ar4", np.nan)
                )
                with np.errstate(divide="ignore", invalid="ignore"):
                    median_df["rmse"] = (median_df["mse"] / median_df["mse_ar4"]).replace([np.inf, -np.inf], np.nan)
                median_df["avg_rmse_y"] = median_df["rmse"].groupby(median_df.index.year).transform("mean")
                median_df["avg_mse_y"] = median_df["mse"].groupby(median_df.index.year).transform("mean")

                period_model_results_avg_dfs_dict["selected"][crit][period] = avg_df
                period_model_results_median_dfs_dict["selected"][crit][period] = median_df

        results_dict["model"]["periods_avg"] = period_model_results_avg_dfs_dict
        results_dict["model"]["periods_median"] = period_model_results_median_dfs_dict
        results_dict["model"]["periods_mseweight"] = period_model_results_mseweight_dfs_dict  # pooled series

        # --- selected variables matrices (per period, and period-quarter) --- #
        selected_vars_quarters_df_dict, selected_vars_quarters_periods_df_dict = self._build_selected_vars_matrices(results_dict)
        results_dict["varselect"]["selected_vars_quarters"] = selected_vars_quarters_df_dict
        results_dict["varselect"]["selected_vars_quarters_periods"] = selected_vars_quarters_periods_df_dict
        results_dict["varselect"]["lambda_cv"] = lambda_cv_dict 
        results_dict["varselect"]["all_selected"] = {
            "raw": sorted(all_full_lst),
            "meta_names": sorted(all_basenames_lst),
        }

        self.results_dict = results_dict

        logger.info("--------------------------------------------------------------------------------")
        logger.info("--------------------------------------------------------------------------------")
        logger.info(f"END Selection '{varselection_method}'")
        logger.info("--------------------------------------------------------------------------------")
        logger.info("--------------------------------------------------------------------------------")

        return results_dict

    # ------------------------ misc helpers ------------------------------- #
    def _get_meta_names(self, selected_vars, y_var):
        return {
            Checks.get_series_meta_name(s)
            for s in selected_vars
            if Checks.get_series_meta_name(s) != y_var
        }

    def _freq_for(self, series_meta_name, meta):
        """Map meta freq to cache freq key (D -> ME; default QE if missing)."""
        info = meta.get(series_meta_name) if meta is not None else None
        if info is None or not hasattr(info, "freq") or info.freq is None:
            return "QE"
        f = info.freq
        return "ME" if f == "D" else f

    def _transformation_for(self, series_meta_name, freq_key, meta):
        """Return the transformation string used in the cache key for this series/freq."""
        info = meta.get(series_meta_name) if meta is not None else None
        if info is None:
            return None
        if freq_key == "ME":
            return getattr(info, "transformation_m1", None)
        if freq_key == "QE":
            return getattr(info, "transformation_applied_q", None)
        return None

    def _category_for(self, series_meta_name, meta, category_type):
        info = meta.get(series_meta_name) if meta is not None else None
        if info is None:
            return "no_category"

        value = getattr(info, category_type, None)
        if value is None:
            return "no_category"

        return value

    def _to_ragged_edge_df(
        self,
        train_idx,
        period,
        release_periods_dict,
        y_var,
        full_sample_df,
        remove_non_stat_fwr=False,
        confidence=0.05
    ):
        released = set(release_periods_dict.get(period, []))
        non_stat_removed_series = 0
        logger.debug(f"Period '{period}' has {len(released)} released series.")
        non_stat_removed_series = 0
        logger.debug(f"Period '{period}' has {len(released)} released series.")

        def is_lag(col: str) -> bool:
            return bool(re.search(r"_lag\d+$", str(col)))

        def get_base(col: str) -> str:
            return Checks.get_series_meta_name(col)

        included = []
        for c in full_sample_df.columns:
            if c == y_var:
                continue

            # Keep ALL lag columns, regardless of period/release list
            if is_lag(c):
                included.append(c)
                continue

            # keep exact released (unlagged) series as before
            if c in released:
                included.append(c)
                continue

        ragged_edge_df = full_sample_df.loc[train_idx, included]
        y_series = full_sample_df.loc[train_idx, y_var]
        ragged_edge_df_joined = ragged_edge_df.join(y_series, how="inner")
        ragged_edge_df_clean = ragged_edge_df_joined.dropna(axis=0)

        if remove_non_stat_fwr:
            for series in ragged_edge_df_clean.columns:
                if series == y_var:
                    continue
                if not Statistics.check_stationarity_s(ragged_edge_df_clean[series], confidence):
                    logger.warning(f"Series {series} is non-stationary in period {period}. Dropping.")
                    ragged_edge_df_clean = ragged_edge_df_clean.drop(columns=[series])
                    non_stat_removed_series += 1
            logger.debug(f"Period '{period}': Removed {non_stat_removed_series} non-stationary series out of {len(included)} included.")

        if remove_non_stat_fwr:
            for series in ragged_edge_df_clean.columns:
                if series == y_var:
                    continue
                if not Statistics.check_stationarity_s(ragged_edge_df_clean[series], confidence):
                    logger.warning(f"Series {series} is non-stationary in period {period}. Dropping.")
                    ragged_edge_df_clean = ragged_edge_df_clean.drop(columns=[series])
                    non_stat_removed_series += 1
            logger.debug(f"Period '{period}': Removed {non_stat_removed_series} non-stationary series out of {len(included)} included.")

        X = ragged_edge_df_clean.drop(columns=[y_var])
        y = ragged_edge_df_clean[y_var]

        return X, y

    def _update_all_selected_lst(self, selected_vars, y_var, all_full_lst, all_basenames_lst, bases):
        for v in selected_vars:
            if Checks.get_series_meta_name(v) != y_var:
                all_full_lst.add(v)
        all_basenames_lst.update(bases)

    def _to_period_model_results_df(self, period_model_results_dict, period):
        df = pd.DataFrame.from_dict(
            period_model_results_dict[period], orient="index"
        )
        cols = [c for c in ['y_actual', 'y_pred', 'mse', 'ar4', 'component', 'subcategory', 'category'] if c in df.columns]
        df = df[cols]
        df.index.name = 'series_meta_name'
        try:
            if 'y_pred' in df.columns:
                mask = ~df.index.isin(['Average', 'Median', 'ci_lower', 'ci_upper'])
                yvals = pd.to_numeric(df.loc[mask, 'y_pred'], errors='coerce').dropna().to_numpy()
                n = yvals.size
                if n > 0:
                    mean = float(np.mean(yvals))
                    std = float(np.std(yvals, ddof=1)) if n > 1 else 0.0
                    se = std / np.sqrt(n) if n > 1 else 0.0
                    half = 1.96 * se 

                    row_lower = pd.Series({c: np.nan for c in df.columns}, name="ci_lower")
                    row_upper = pd.Series({c: np.nan for c in df.columns}, name="ci_upper")
                    row_lower['y_pred'] = mean - half
                    row_upper['y_pred'] = mean + half

                    df = pd.concat([df, pd.DataFrame([row_lower, row_upper])], axis=0)
        except Exception as _e:
            logger.debug(f"CI rows not added for period '{period}': {_e}")

        return df

    def _append_avg_median_rows(self, period_model_results_df, avg_label="Average", median_label="Median"):
        if period_model_results_df.empty:
            return period_model_results_df
        avg = period_model_results_df.mean(numeric_only=True)
        med = period_model_results_df.median(numeric_only=True)
        summary = pd.DataFrame([avg, med], index=[avg_label, median_label]).reindex(period_model_results_df.columns, axis=1)
        return pd.concat([period_model_results_df, summary], axis=0)

    def _to_avg_median_dfs(
        self,
        period_model_results_dfs,
        period,
        metrics=("y_actual", "y_pred", "mse"),
        avg_label="Average",
        median_label="Median",
    ):
        avg_rows = {}
        med_rows = {}

        for q in period_model_results_dfs.keys():
            df = period_model_results_dfs.get(q, {}).get(period)
            if df is None or df.empty:
                avg_rows[q] = pd.Series({m: np.nan for m in metrics})
                med_rows[q] = pd.Series({m: np.nan for m in metrics})
                continue

            # --- Average row values
            y_act_avg = df.loc[avg_label, "y_actual"] if (avg_label in df.index and "y_actual" in df.columns) else np.nan
            y_pred_avg = df.loc[avg_label, "y_pred"]   if (avg_label in df.index and "y_pred"   in df.columns) else np.nan
            mse_avg = (y_act_avg - y_pred_avg) ** 2 if np.isfinite(y_act_avg) and np.isfinite(y_pred_avg) else np.nan

            avg_vals_map = {"y_actual": y_act_avg, "y_pred": y_pred_avg, "mse": mse_avg}
            avg_rows[q] = pd.Series({m: avg_vals_map.get(m, np.nan) for m in metrics})

            # --- Median row values
            y_act_med = df.loc[median_label, "y_actual"] if (median_label in df.index and "y_actual" in df.columns) else np.nan
            y_pred_med = df.loc[median_label, "y_pred"]   if (median_label in df.index and "y_pred"   in df.columns) else np.nan
            mse_med = (y_act_med - y_pred_med) ** 2 if np.isfinite(y_act_med) and np.isfinite(y_pred_med) else np.nan

            med_vals_map = {"y_actual": y_act_med, "y_pred": y_pred_med, "mse": mse_med}
            med_rows[q] = pd.Series({m: med_vals_map.get(m, np.nan) for m in metrics})

        avg_df = pd.DataFrame.from_dict(avg_rows, orient="index")
        median_df = pd.DataFrame.from_dict(med_rows, orient="index")
        avg_df.index.name = "quarter"
        median_df.index.name = "quarter"
        return avg_df, median_df

    def _get_release_selected_block_dict(self, period_raw_names_dict, meta):
        release_selected_block_dict = {}

        for quarter, periods in period_raw_names_dict.items():
            release_selected_block_dict[quarter] = {}
            for period, selected_vars in periods.items():
                release_selected_block_dict[quarter][period] = {}
                for var in selected_vars:
                    release_selected_block_dict[quarter][period][var] = self._map_var_to_period(var, meta)
        return release_selected_block_dict

    def _map_var_to_period(self, selected_var, meta):
        meta_name = Checks.get_series_meta_name(selected_var)
        info = meta.get(meta_name)
        freq = info.freq

        if freq == "QE":
            m_q = re.search(r"_lag(\d+)$", selected_var)
            out = f"q_period_lag{m_q.group(1)}" if m_q else "q_period"
            return out

        elif freq in {"ME", "D"}:
            m_block = re.search(r"(m[123])(?:_lag(\d+))?$", selected_var)
            block, lag = m_block.groups()
            out = f"{block}_period" + (f"_lag{lag}" if lag else "")
            return out

        else:
            raise ValueError(f"Unknown freq '{freq}' for series '{meta_name}'")

    # ------------------------ KEY HELPERS ------------------------------- #
    def _make_cache_key(self, top_level_cache_key, quarter, freq, series, period_type, crit, transformation):
        return (top_level_cache_key, quarter, freq, series, period_type, crit, transformation)
    
    # ---- Cache helpers -------------------------------------------------- #
    def _normalize_model_cache(self, model_cache):
        if isinstance(model_cache, dict):
            items = model_cache.items()
        else:
            items = []
            try:
                for item in model_cache:
                    if isinstance(item, tuple):
                        if len(item) == 2 and isinstance(item[0], tuple):
                            items.append(item)
                        elif len(item) >= 7:
                            key = tuple(item[:-1])
                            payload = item[-1]
                            items.append((key, payload))
            except Exception as e:
                logger.warning(f"Failed to iterate external model_cache: {e}")
                items = []

        normalized = {}
        for k, payload in items:
            # prefer 7-tuple (includes transformation); else fall back to 6
            base_key = tuple(k[:7]) if len(k) >= 7 else tuple(k[:6])
            existing = normalized.get(base_key)
            if existing is None:
                normalized[base_key] = payload
            else:
                has_pred_new = isinstance(payload, dict) and payload.get("y_pred") is not None
                has_pred_old = isinstance(existing, dict) and existing.get("y_pred") is not None
                if has_pred_new and not has_pred_old:
                    normalized[base_key] = payload
        return normalized

    def _lookup_cache_entry(self, cache_dict, desired_key):
        if desired_key in cache_dict:
            return cache_dict[desired_key]

        # tolerant: match on date for quarter element (rare path)
        if len(desired_key) == 7:
            tlk, q_desired, freq, series, block, crit, transformation = desired_key
            q_desired_date = None
            try:
                q_desired_date = pd.Timestamp(q_desired).date()
            except Exception:
                pass
            if q_desired_date is None:
                return None

            for (tlk_k, q_k, f_k, s_k, b_k, c_k, t_k), payload in cache_dict.items():
                # skip 6-tuples when looking for 7-tuple key
                if not isinstance((tlk_k, q_k, f_k, s_k, b_k, c_k, t_k), tuple):
                    continue
                if tlk_k != tlk or f_k != freq or s_k != series or b_k != block or c_k != crit or t_k != transformation:
                    continue
                try:
                    if pd.Timestamp(q_k).date() == q_desired_date:
                        return payload
                except Exception:
                    continue
            return None

        # 6-tuple tolerant match
        tlk, q_desired, freq, series, block, crit = desired_key
        q_desired_date = None
        try:
            q_desired_date = pd.Timestamp(q_desired).date()
        except Exception:
            pass
        if q_desired_date is None:
            return None

        for key_k, payload in cache_dict.items():
            if len(key_k) != 6:
                continue
            tlk_k, q_k, f_k, s_k, b_k, c_k = key_k
            if tlk_k != tlk or f_k != freq or s_k != series or b_k != block or c_k != crit:
                continue
            try:
                if pd.Timestamp(q_k).date() == q_desired_date:
                    return payload
            except Exception:
                continue
        return None

    def _get_cached_predictions(self, cache_dict, top_level_cache_key, quarter, freq_key, series, period_key, crit, transformation_key):
        key7 = self._make_cache_key(top_level_cache_key, quarter, freq_key, series, period_key, crit, transformation_key)
        # logger.debug(f"THIS IS IT: Cache lookup for key={key7}")
        entry = self._lookup_cache_entry(cache_dict, key7)
        # logger.debug(f"Cache lookup for key={key7} found entry={entry is not None}")
        if entry is None:
            return None, None, None, None
        return entry.get("y_actual"), entry.get("y_pred"), entry.get("mse"), entry.get("spec")

    # ---------- matrices of selected vars (unchanged except 'latest' removed) -------------------- #
    def _build_selected_vars_matrices(self, results_dict):
        details = results_dict.get("model", {}).get("periods_details", {})
        summary_rows_to_exclude = {"Average", "Median", "ci_lower", "ci_upper"}

        def _extract_all_quarters(dn, cr):
            return list(details.get(dn, {}).get(cr, {}).keys())

        def _extract_all_periods(dn, cr):
            periods = set()
            for q, per_map in details.get(dn, {}).get(cr, {}).items():
                periods.update(per_map.keys())
            return sorted(periods, key=lambda p: str(p))

        def _gather_vars_for_period(dn, cr, period):
            vars_set = set()
            for q, per_map in details.get(dn, {}).get(cr, {}).items():
                df = per_map.get(period)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    vars_set.update([idx for idx in df.index if idx not in summary_rows_to_exclude])
            return sorted(vars_set)

        # Output containers
        selected_vars_quarters_df_dict = {dn: {cr: {} for cr in details.get(dn, {})} for dn in details if dn != "mseweight"}
        selected_vars_quarters_periods_df_dict = {dn: {cr: None for cr in details.get(dn, {})} for dn in details if dn != "mseweight"}

        for dict_name in details.keys():  # "selected" (and "mseweight" which we skip)
            if dict_name == "mseweight":
                continue
            for crit in details[dict_name].keys():
                quarters = _extract_all_quarters(dict_name, crit)
                periods = _extract_all_periods(dict_name, crit)

                # --- (1) per-period matrices over quarters
                for period in periods:
                    row_vars = _gather_vars_for_period(dict_name, crit, period)
                    if not row_vars:
                        selected_vars_quarters_df_dict[dict_name][crit][period] = pd.DataFrame()
                        continue

                    mat = pd.DataFrame(index=row_vars, columns=quarters, dtype=object)

                    for q in quarters:
                        df = details[dict_name][crit].get(q, {}).get(period)
                        if not isinstance(df, pd.DataFrame) or df.empty:
                            continue

                        present_rows = [r for r in df.index if r in row_vars]
                        # Mark selection uniformly with "X"
                        for r in present_rows:
                            mat.at[r, q] = "X"

                    # Count "X" per column
                    counts = mat.applymap(lambda v: 1 if isinstance(v, str) and v == "X" else 0).sum(axis=0)
                    mat.loc["Selected_Count"] = counts.to_list()
                    selected_vars_quarters_df_dict[dict_name][crit][period] = mat

                # --- (2) one matrix per dict_name/crit over all (period, quarter)
                all_vars = set()
                for period in periods:
                    all_vars.update(_gather_vars_for_period(dict_name, crit, period))
                all_vars = sorted(all_vars)

                if not all_vars or not quarters or not periods:
                    selected_vars_quarters_periods_df_dict[dict_name][crit] = pd.DataFrame()
                    continue

                cols = pd.MultiIndex.from_tuples(
                    [(period, q) for period in periods for q in quarters],
                    names=["period", "quarter"]
                )
                mat_pq = pd.DataFrame(index=all_vars, columns=cols, dtype=object)

                for period in periods:
                    for q in quarters:
                        df = details[dict_name][crit].get(q, {}).get(period)
                        if not isinstance(df, pd.DataFrame) or df.empty:
                            continue
                        valid_rows = [r for r in df.index if r in all_vars]
                        for r in valid_rows:
                            mat_pq.at[r, (period, q)] = "X"

                counts = mat_pq.applymap(lambda v: 1 if isinstance(v, str) and v == "X" else 0).sum(axis=0)
                mat_pq.loc["Selected_Count"] = counts.to_list()

                selected_vars_quarters_periods_df_dict[dict_name][crit] = mat_pq

        return selected_vars_quarters_df_dict, selected_vars_quarters_periods_df_dict
