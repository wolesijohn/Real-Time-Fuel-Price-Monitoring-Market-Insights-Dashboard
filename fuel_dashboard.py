import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from fuel_fetch_data import fetch_fuel_data, store_data, load_data
from utils import calculate_metrics, forecast_prices

# Streamlit Dashboard
st.set_page_config(page_title="Fuel Price Dashboard", layout="wide")

st.title("Real-Time Fuel Price Monitoring Dashboard")

# Initialize database and fetch data
try:
    df = load_data()
except:
    df = fetch_fuel_data()
    store_data(df)

# Sidebar for region and fuel type selection
st.sidebar.header("Filter Options")
region = st.sidebar.selectbox("Select Region", df['region'].unique())
fuel_type = st.sidebar.selectbox("Select Fuel Type", df['fuel_type'].unique())
time_range = st.sidebar.slider("Select Time Range (days)", 7, 30, 30)

# Filter data based on selections
df_filtered = df[(df['region'] == region) & (df['fuel_type'] == fuel_type)]
df_filtered['date'] = pd.to_datetime(df_filtered['date'])
df_filtered = df_filtered[df_filtered['date'] >= datetime.now() - timedelta(days=time_range)]

# Calculate metrics and detect spikes
df_metrics, spike_alert = calculate_metrics(df, region, fuel_type)

# Display metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Latest Price (NGN)", f"{df_metrics['price'].iloc[-1]:.2f}" if not df_metrics.empty else "N/A")
with col2:
    st.metric("Daily Change (%)", f"{df_metrics['daily_change'].iloc[-1]:.2f}" if not df_metrics['daily_change'].empty else "N/A")

# Spike Alert
if spike_alert:
    st.error(f"🚨 Price Spike Alert: {fuel_type} in {region} increased by more than 5% in the last 24 hours!")

# Trend Chart
fig = px.line(df_metrics, x='date', y='price', title=f"{fuel_type} Price Trend in {region}")
fig.add_scatter(x=df_metrics['date'], y=df_metrics['moving_avg'], name='7-Day Moving Average', line=dict(color='orange'))
fig.update_layout(xaxis_title="Date", yaxis_title="Price (NGN)")
st.plotly_chart(fig, use_container_width=True)

# Forecast
if st.checkbox("Show Price Forecast"):
    forecast = forecast_prices(df, region, fuel_type)
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast'))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', name='Lower CI'))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill='tonexty', name='Upper CI'))
    fig_forecast.update_layout(title=f"7-Day Price Forecast for {fuel_type} in {region}", xaxis_title="Date", yaxis_title="Price (NGN)")
    st.plotly_chart(fig_forecast, use_container_width=True)

# Data refresh button
if st.button("Refresh Data"):
    new_data = fetch_fuel_data()
    store_data(new_data)
    st.experimental_rerun()