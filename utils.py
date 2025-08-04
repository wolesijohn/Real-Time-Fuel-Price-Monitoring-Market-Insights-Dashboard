import pandas as pd
from prophet import Prophet

def calculate_metrics(df, region, fuel_type, threshold=5):
    df_region = df[(df['region'] == region) & (df['fuel_type'] == fuel_type)]
    df_region['date'] = pd.to_datetime(df_region['date'])
    df_region = df_region.sort_values('date')
    
    df_region['daily_change'] = df_region['price'].pct_change() * 100
    df_region['moving_avg'] = df_region['price'].rolling(window=7).mean()
    spike_alert = df_region['daily_change'].iloc[-1] > threshold if not df_region['daily_change'].empty else False
    return df_region, spike_alert

def forecast_prices(df, region, fuel_type, days=7):
    df_region = df[(df['region'] == region) & (df['fuel_type'] == fuel_type)][['date', 'price']]
    df_region['date'] = pd.to_datetime(df_region['date'])
    df_prophet = df_region.rename(columns={'date': 'ds', 'price': 'y'})
    
    model = Prophet(daily_seasonality=True)
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]