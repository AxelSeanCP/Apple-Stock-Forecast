# -*- coding: utf-8 -*-
"""Apple_Forecast.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uZX6jfzzgCbELdkwvvWXHMRUgtm20Zxo

# Setup
"""

!pip install -q statsmodels

"""## Import Libraries"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.deterministic import DeterministicProcess
from statsmodels.graphics.tsaplots import plot_pacf
from sklearn.linear_model import LinearRegression

# Set Matplotlib defaults
plt.style.use("seaborn-whitegrid")
plt.rc("figure", autolayout=True, figsize=(11, 4))
plt.rc(
    "axes",
    labelweight="bold",
    labelsize="large",
    titleweight="bold",
    titlesize=16,
    titlepad=10,
)
plot_params = dict(
    color="0.75",
    style=".-",
    markeredgecolor="0.25",
    markerfacecolor="0.25",
)
# %config InlineBackend.figure_format = 'retina'

"""# Data Loading"""

apple = pd.read_csv("/content/AAPL.csv")

apple.head()

target_columns = ['Date', 'Close']
apple = apple[target_columns]
apple.head()

apple.set_index(
    pd.PeriodIndex(apple.Date, freq="D"),
    inplace=True
)
apple.drop("Date", axis=1, inplace=True)
apple.head()

ax = apple.Close.plot(title="Stock Close Price", **plot_params)
_ = ax.set(ylabel="Price")

"""# Data Preparation"""

moving_average = apple.rolling(
    window=36,
    center=True,
    min_periods=18
).mean()

ax = apple.plot(style=".", color="0.5")
moving_average.plot(
    ax=ax, linewidth=3, title="Apple Stock 365-Day Moving Average", legend=False
)

"""# Predict Trend"""

dp = DeterministicProcess(
    index=apple.index,
    order=1,
    constant=True,
    drop=True
)

X = dp.in_sample()
X.head()

y = apple.Close

model = LinearRegression(fit_intercept=False)
model.fit(X, y)

y_pred = pd.Series(model.predict(X), index=X.index)

ax = apple.plot(style=".", color="0.5", title="Apple Stock - Linear Trend")
_ = y_pred.plot(ax=ax, linewidth=3, label="Trend")

num_years = 15
X = dp.out_of_sample(steps=365 * num_years)

y_fore = pd.Series(model.predict(X), index=X.index)

y_fore.head()

ax = apple.plot(title="Apple Stock - Linear Trend Forecast", **plot_params)
ax = y_pred.plot(ax=ax, linewidth=3, label="Trend")
ax = y_fore.plot(ax=ax, linewidth=3, label="Trend Forecast", color="C3")
_ = ax.legend()

"""# Serial Dependencies"""

_ = plot_pacf(apple.Close, lags=12)

def make_lags(ts, lags):
  return pd.concat(
      {
          f'y_lag_{i}': ts.shift(i) for i in range(1, lags+1)
      },
      axis=1
  )

X = make_lags(apple.Close, lags=2)
X = X.fillna(0.0)
X.head()

y = apple.Close.copy()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = pd.Series(model.predict(X_train), index=X_train.index)
y_fore = pd.Series(model.predict(X_test), index=X_test.index)

ax = y_train.plot(**plot_params, label="Actual Train")
ax = y_test.plot(**plot_params, label="Actual Test")
ax = y_pred.plot(ax=ax, label="Predict Train")
ax = y_fore.plot(ax=ax, color="C3", label="Predict Test")
ax.legend()

ax = y_test.plot(**plot_params, label="Actual", legend=True)
_ = y_fore.plot(ax=ax, color="C3", label="Prediction", legend=True)