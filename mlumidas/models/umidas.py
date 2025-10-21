# --- Updated UMidas class ---
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error
from loguru import logger

class UMidas:
    def __init__(self, y_var, train_data, test_data, model_grid):
        self.y_var = y_var
        self.train_data = train_data
        self.test_data = test_data
        self.model_grid = model_grid

        self.criteria = ["bic", "aic", "adj_r2"]
        self.best_models_by_criterion = {
            c: {
                "score": np.inf if c != "adj_r2" else -np.inf,
                "spec": None,
                "variable_names": None,
                "model": None
            } for c in self.criteria
        }

    def to_yX_np(self, df):
        y = df.iloc[:, 0].values
        X = df.iloc[:, 1:].values
        return y, X

    def _extract_score(self, model, criterion):
        if criterion == "bic":
            return model.bic
        elif criterion == "aic":
            return model.aic
        elif criterion == "adj_r2":
            return model.rsquared_adj
        else:
            raise ValueError(f"Unknown criterion: {criterion}")

    def get_best(self):
        y, X_all = self.to_yX_np(self.train_data)
        X_columns = self.train_data.columns[1:]

        for spec in self.model_grid:
            if max(spec) >= X_all.shape[1]:
                logger.warning(f"Skipping spec {spec} — index {max(spec)} exceeds available columns ({X_all.shape[1]})")
                continue

            try:
                X_spec = X_all[:, list(spec)]
                X_spec = sm.add_constant(X_spec)
                model = sm.OLS(y, X_spec).fit()

                for crit in self.criteria:
                    score = self._extract_score(model, crit)

                    is_better = (
                        score < self.best_models_by_criterion[crit]["score"]
                        if crit in {"bic", "aic"}
                        else score > self.best_models_by_criterion[crit]["score"]
                    )

                    if is_better:
                        self.best_models_by_criterion[crit] = {
                            "score": score,
                            "spec": spec,
                            "variable_names": [X_columns[i] for i in spec],
                            "summary": model.summary(),
                            "model": None
                        }

            except Exception as e:
                logger.warning(f"Failed to fit model with spec {spec}: {e}")
                continue

        return self.best_models_by_criterion

    def fit(self, spec): 
        y, X_all = self.to_yX_np(self.train_data)
        X_spec = X_all[:, list(spec)]
        X_spec = sm.add_constant(X_spec)
        model = sm.OLS(y, X_spec).fit()
        return model

    def predict(self, model, spec):
        X_test_full = self.test_data.iloc[:, 1:].values
        X_spec = X_test_full[:, list(spec)]
        X_spec = sm.add_constant(X_spec, has_constant='add')

        if X_spec.shape[1] != len(model.params):
            raise ValueError(f"Mismatch: test has {X_spec.shape[1]} cols, model expects {len(model.params)}.")

        prediction = model.get_prediction(X_spec)
        summary = prediction.summary_frame(alpha=0.05)

        y_actual = self.test_data.iloc[0, 0]
        y_pred = summary['mean'].iloc[0]
        mse = mean_squared_error([y_actual], [y_pred])

        return y_actual, y_pred, mse
    
    def fit_full(self):
        y, X_all_full = self.to_yX_np(self.train_data)
        X_all_full = sm.add_constant(X_all_full)
        model = sm.OLS(y, X_all_full).fit()
        return model

    def predict_full(self, model):
        X_test_full = self.test_data.iloc[:, 1:].values
        X_test_full = sm.add_constant(X_test_full, has_constant='add')

        if X_test_full.shape[1] != len(model.params):
            raise ValueError(f"Mismatch: test has {X_test_full.shape[1]} cols, model expects {len(model.params)}.")

        prediction = model.get_prediction(X_test_full)
        summary = prediction.summary_frame(alpha=0.05)

        y_actual = self.test_data.iloc[0, 0]
        y_pred = summary['mean'].iloc[0]
        mse = mean_squared_error([y_actual], [y_pred])

        return y_actual, y_pred, mse