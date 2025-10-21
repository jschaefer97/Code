import statsmodels.api as sm
from sklearn.metrics import mean_squared_error

class BenchmarkAR4:
    def __init__(self, y_var, train_data, test_data):
        self.y_var = y_var
        self.train_data = train_data
        self.test_data = test_data

    def to_yX_np(self, df):
        y = df.iloc[:, 0].to_numpy()
        X = df.iloc[:, 1:].to_numpy()
        return y, X

    def fit(self):
        y, X_all = self.to_yX_np(self.train_data)
        X_train = sm.add_constant(X_all, has_constant='add')
        model = sm.OLS(y, X_train).fit()
        return model

    def predict(self, model):
        X_test = self.test_data.iloc[:, 1:].to_numpy()
        X_test = sm.add_constant(X_test, has_constant='add')

        prediction = model.get_prediction(X_test)
        summary = prediction.summary_frame(alpha=0.05)

        y_actual = self.test_data.iloc[0, 0]
        y_pred = summary['mean'].iloc[0]
        mse = mean_squared_error([y_actual], [y_pred])

        return y_actual, y_pred, mse
     