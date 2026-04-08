import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path

sns.set_style('whitegrid')

url = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/shampoo.csv'
df = pd.read_csv(url, header=0, names=['Month', 'Sales'])
print('shape', df.shape)

# convert to datetime (the format in dataset is e.g., 1-01, 1-02 etc.)
if 'Month' in df.columns:
    parts = df['Month'].str.split('-', expand=True)
    df['Year'] = parts[0].astype(int) + 2000
    df['MonthNum'] = parts[1].astype(int)
    df['Month'] = pd.to_datetime(dict(year=df['Year'], month=df['MonthNum'], day=1))

# sort
df = df.sort_values('Month')

# duplicates
print('dups', df.duplicated('Month').sum())

# set index and ensure regular monthly frequency
both = df.set_index('Month')[['Sales']]
all_months = pd.date_range(start=both.index.min(), end=both.index.max(), freq='MS')
both = both.reindex(all_months)
# interpolate any small gaps (as shampoo data has no real gaps)
both['Sales'] = both['Sales'].interpolate(method='linear').ffill().bfill()

# features
both['Year'] = both.index.year
both['MonthNum'] = both.index.month
both['Day'] = both.index.day
both['Weekday'] = both.index.weekday
both['WeekOfYear'] = both.index.isocalendar().week
for lag in [1,2,3,6,12]:
    both[f'lag_{lag}'] = both['Sales'].shift(lag)
both['roll_3'] = both['Sales'].rolling(window=3,min_periods=1).mean()
both['roll_6'] = both['Sales'].rolling(window=6,min_periods=1).mean()

both = both.dropna()
print('after dropna', both.shape)

n_test=12
train=both.iloc[:-n_test]; test=both.iloc[-n_test:]
features=['lag_1','lag_2','lag_3','roll_3','roll_6','Year','MonthNum','Weekday','WeekOfYear']
X_train=train[features]; y_train=train['Sales']; X_test=test[features]; y_test=test['Sales']

scaler = StandardScaler(); X_train_sc = scaler.fit_transform(X_train); X_test_sc = scaler.transform(X_test)

lr=LinearRegression(); lr.fit(X_train_sc,y_train); y_pred_lr=lr.predict(X_test_sc)
rf=RandomForestRegressor(n_estimators=10,random_state=42); rf.fit(X_train,y_train); y_pred_rf=rf.predict(X_test)

arima_model=SARIMAX(train['Sales'], order=(1,1,1), seasonal_order=(1,1,1,12), enforce_stationarity=False, enforce_invertibility=False)
arima_fit=arima_model.fit(disp=False)

arima_pred = arima_fit.predict(start=test.index[0], end=test.index[-1], dynamic=False)
y_pred_arima = pd.Series(arima_pred.values, index=test.index)

for name,y_pred in [('Linear',y_pred_lr),('RF',y_pred_rf),('SARIMA',y_pred_arima) ]:
    mae=mean_absolute_error(y_test,y_pred)
    rmse=np.sqrt(mean_squared_error(y_test,y_pred))
    print(name, mae, rmse)

future = arima_fit.get_forecast(steps=12)
print('future', future.predicted_mean.head())

Path('outputs').mkdir(exist_ok=True)
with open('outputs/forecast.pkl','wb') as f:
    pickle.dump(arima_fit, f)

future_df = future.predicted_mean.to_frame(name='Forecast')
future_df.index = pd.date_range(start=both.index.max()+pd.DateOffset(months=1), periods=12, freq='MS')
future_df.to_csv('outputs/sales_forecast_future.csv')
print('done')