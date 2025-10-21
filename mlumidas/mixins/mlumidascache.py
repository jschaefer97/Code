import time
from collections import defaultdict
from tqdm import tqdm
from loguru import logger
from joblib import dump, load
import pandas as pd
from collections import defaultdict as _dd
import numpy as np

from utils.utils import get_formatted_date
from mlumidas.models.umidas import UMidas
from mlumidas.utils.modelgrid import get_model_grid_dict


class MLUMidasCacheMixin:

    def _make_cache_key_cache(self, top_level_key, quarter, freq, series, period_type, crit, transformation, *extras):
        return (top_level_key, quarter, freq, series, period_type, crit, transformation) + tuple(extras)

    def _make_history_key(self, top_level_key, freq, series, period_type, crit, transformation):
        return (top_level_key, freq, series, period_type, crit, transformation)

    def _save_cache(self, cache, path, filename):
        dump(cache, f"{path}/{filename}", compress=("lz4", 3))  # Fast + small

    def _load_cache(self, path, filename):
        return load(f"{path}/{filename}")

    def _save_history(self, hist, path, filename):
        dump(hist, f"{path}/{filename}", compress=("lz4", 3))

    def _load_history(self, path, filename):
        return load(f"{path}/{filename}")

    def load_or_compute_model_cache(
        self,
        umidas_model_lags,
        file_path_modelcache,
        start_date,
        end_date,
        y_var,
        fwr_idx_dict,
        series_model_dataframes,
        meta,
    ):
        model_grid_dict = get_model_grid_dict()

        formatted_start_date = get_formatted_date(start_date)
        formatted_end_date = get_formatted_date(end_date)
        top_level_key = f"{formatted_start_date}_to_{formatted_end_date}_{y_var}_lags_{umidas_model_lags}"

        logger.info(f"Top-level key for this run: {top_level_key}")

        self.y_var = y_var
        self.file_path_modelcache = file_path_modelcache
        self.fwr_idx_dict = fwr_idx_dict
        self.series_model_dataframes = series_model_dataframes
        self.meta = meta

        try:
            model_cache = self._load_cache(file_path_modelcache, f"model_cache_{top_level_key}.pkl")
            logger.info(f"Loaded existing model cache from: {file_path_modelcache}")
        except FileNotFoundError:
            logger.warning(f"No existing model cache found at {file_path_modelcache}. Initializing empty cache.")
            model_cache = {}

        missing_combinations = []

        all_series = list(series_model_dataframes.keys())

        for series in all_series:
            for qtr in fwr_idx_dict:
                for period_type in series_model_dataframes[series].keys():
                    if period_type == "full_model_df":
                        continue
                    meta_obj = meta.get(series)
                    if meta_obj is None:
                        logger.warning(f"Skipping series '{series}' — no metadata found.")
                        continue
                    freq = meta_obj.freq
                    if freq == "D":
                        freq = "ME"

                    # Determine transformation safely (default to None if not available or freq unexpected)
                    transformation = None
                    if freq == "ME":
                        transformation = getattr(meta_obj, "transformation_m1", None)
                    elif freq == "QE":
                        transformation = getattr(meta_obj, "transformation_applied_q", None)

                    for crit in ["bic", "aic", "adj_r2"]:
                        key = self._make_cache_key_cache(top_level_key, qtr, freq, series, period_type, crit, transformation)
                        if key not in model_cache:
                            missing_combinations.append((top_level_key, qtr, freq, series, period_type, transformation))
                            
        missing_combinations = list(set(missing_combinations))

        if missing_combinations:
            logger.warning(f"Total missing combinations (best-spec search groups): {len(missing_combinations)}")

            est_minutes = self._estimate_compute_time(missing_combinations, model_grid_dict)
            logger.warning(f"Estimated time to compute missing combinations: {est_minutes:.2f} minutes")

            model_cache = self._compute_and_cache_models(
                est_minutes, missing_combinations, model_grid_dict, model_cache
            )
        else:
            logger.info("No missing best-spec combinations found. Nothing to compute.")

        try:
            self._save_cache(model_cache, file_path_modelcache, f"model_cache_{top_level_key}.pkl")
            logger.success(f"Model cache (specs + predictions) saved to: {file_path_modelcache}")
        except Exception as e:
            logger.warning(f"Failed to save updated model cache: {e}")

        return model_cache, top_level_key

    def _compute_and_cache_models(self, est_minutes, missing_combinations, model_grid_dict, model_cache):
        for top_level_key, quarter, frequency, series, period_type, transformation in missing_combinations:
            try:
                model_grid = model_grid_dict["quarterly_grid"] if frequency == "QE" else model_grid_dict["monthly_grid"]
                period_df = self.series_model_dataframes[series][period_type]
                train_idx = self.fwr_idx_dict[quarter]["train_idx"]
                test_idx = self.fwr_idx_dict[quarter]["test_idx"]
                train_data = period_df.loc[train_idx]
                test_data = period_df.loc[test_idx]

                best_model = UMidas(
                    y_var=self.y_var,
                    train_data=train_data,
                    test_data=test_data,
                    model_grid=model_grid
                )
                best_model.get_best()

                for crit in best_model.best_models_by_criterion:
                    key = self._make_cache_key_cache(top_level_key, quarter, frequency, series, period_type, crit, transformation)
                    
                    spec = best_model.best_models_by_criterion[crit]["spec"]
                    best_spec_model = best_model.fit(spec)
                    y_actual, y_pred, mse = best_model.predict(best_spec_model, spec)

                    model_cache[key] = {
                        "spec": spec,
                        "variable_names": best_model.best_models_by_criterion[crit]["variable_names"],
                        "score": best_model.best_models_by_criterion[crit]["score"],
                        "summary": None,
                        "y_actual": y_actual,
                        "y_pred": y_pred,
                        "mse": mse,
                    }
            except Exception as e:
                logger.warning(f"Spec computation failed for {series} | {period_type} | {quarter}: {e}")

        unique_top_keys = {tpl[0] for tpl in missing_combinations}
        save_top_key = next(iter(unique_top_keys)) if unique_top_keys else "unknown"
        self.model_cache = model_cache
        self._save_cache(self.model_cache, self.file_path_modelcache, f"model_cache_{save_top_key}.pkl")
        logger.success(f"Updated model cache saved to: {self.file_path_modelcache}")

        return model_cache

    def _estimate_compute_time(self, missing_combinations, model_grid_dict):
        time_per_model = 0.000004845
        unique_monthly = set(
            (q, s, p)
            for (_, q, freq, s, p, _) in missing_combinations
            if freq == "ME"
        )
        n_missing_models = len(unique_monthly)
        n_specs = len(model_grid_dict["monthly_grid"])
        total_models = n_missing_models * n_specs

        est_seconds = total_models * time_per_model
        est_minutes = est_seconds / 60

        logger.info(
            f"Estimated compute time for missing monthly indicator specs: "
            f"{est_minutes:.2f} minutes "
            f"({total_models} models at {time_per_model} sec/model)"
        )
        return est_minutes

    # ==============================================================
    #            NEW: MSE HISTORY (load-or-compute)
    # ==============================================================

    def load_or_compute_mse_history(
        self,
        file_path_modelcache: str,
        top_level_key: str,
        model_cache: dict | None = None,
    ) -> dict:
       
        hist_fname = f"mse_history_{top_level_key}.pkl"

        try:
            mse_history = self._load_history(file_path_modelcache, hist_fname)
            logger.info(f"Loaded existing MSE history from: {file_path_modelcache}/{hist_fname}")
            return mse_history
        except FileNotFoundError:
            logger.info("No existing MSE history found on disk. Will compute from model cache...")

        # if model_cache not provided, try to load the model cache by top-level key
        if model_cache is None:
            try:
                model_cache = self._load_cache(file_path_modelcache, f"model_cache_{top_level_key}.pkl")
                logger.info(f"Loaded model cache for building MSE history: {file_path_modelcache}")
            except FileNotFoundError:
                logger.error(
                    f"Cannot build MSE history: model cache file 'model_cache_{top_level_key}.pkl' not found "
                    f"in {file_path_modelcache}. Provide `model_cache` or compute it first."
                )
                return {}

        # Build history from cache
        mse_history = self._compute_mse_history_from_model_cache(model_cache, top_level_key)

        # Save to disk
        try:
            self._save_history(mse_history, file_path_modelcache, hist_fname)
            logger.success(f"MSE history saved to: {file_path_modelcache}/{hist_fname}")
        except Exception as e:
            logger.warning(f"Failed to save MSE history: {e}")

        return mse_history

    def _compute_mse_history_from_model_cache(self, model_cache: dict, top_level_key: str) -> dict:

        buckets: dict = {}

        for key, payload in model_cache.items():
            # key expected: (top, quarter, freq, series, period_type, crit, transformation, ...)
            if not isinstance(key, tuple) or len(key) < 7:
                continue

            top_k, quarter, freq, series, period_type, crit, transformation = key[:7]
            # keep only current run's top key
            if str(top_k) != str(top_level_key):
                continue

            # extract/compute squared error
            y_act = payload.get("y_actual")
            y_pred = payload.get("y_pred")
            mse = payload.get("mse")

            if mse is not None and np.isfinite(mse):
                se_val = float(mse)
            else:
                if y_act is None or y_pred is None:
                    continue
                try:
                    se_val = (float(y_act) - float(y_pred)) ** 2
                except Exception:
                    continue

            try:
                q = pd.Timestamp(quarter)
            except Exception:
                # if quarter unparsable, skip
                continue

            hist_key = self._make_history_key(top_level_key, freq, series, period_type, crit, transformation)
            if hist_key not in buckets:
                buckets[hist_key] = {}
            # last write wins if duplicates; we assume unique per (key, quarter)
            buckets[hist_key][q] = se_val

        # Convert to sorted Series
        for hk in list(buckets.keys()):
            s = pd.Series(buckets[hk], dtype=float)
            s = s.sort_index()
            # Optionally drop NaN/infs
            s = s.replace([np.inf, -np.inf], np.nan).dropna()
            buckets[hk] = s

        logger.info(f"Built MSE history: {len(buckets)} series across specs/criteria.")
        return buckets

