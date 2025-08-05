import pandas as pd
import sqlite3
import numpy as np
from datetime import datetime, timedelta
import schedule
import time

def fetch_fuel_data():
       # Simulate realistic fuel price data for Nigeria
       regions = ["Lagos", "Abuja", "Port Harcourt"]
       fuel_types = ["Petrol", "Diesel"]
       data = []
       base_date = datetime.now() - timedelta(days=30)
       
       # Base prices (NGN per liter) and regional adjustments
       base_prices = {"Petrol": 600, "Diesel": 700}  # Starting prices
       region_modifiers = {
           "Lagos": 0.95,  # Cheaper due to proximity to ports
           "Abuja": 1.05,  # Slightly higher due to transport costs
           "Port Harcourt": 1.0  # Moderate due to refining proximity
       }
       
       for i in range(30):  # 30 days of data
           date = base_date + timedelta(days=i)
           # Add a slight upward trend over time (e.g., 0.5% daily increase)
           trend_factor = 1 + (i * 0.005)
           
           for region in regions:
               for fuel in fuel_types:
                   # Base price with trend and regional adjustment
                   base_price = base_prices[fuel] * trend_factor * region_modifiers[region]
                   # Add random daily fluctuation (±5%)
                   fluctuation = np.random.uniform(-0.05, 0.05)
                   price = base_price * (1 + fluctuation)
                   
                   data.append({
                       "date": date.strftime("%Y-%m-%d"),
                       "region": region,
                       "fuel_type": fuel,
                       "price": round(price, 2)
                   })
       
       return pd.DataFrame(data)

def store_data(df):
       conn = sqlite3.connect('fuel_data.db')
       # Ensure no duplicate entries by checking existing data
       existing = load_data()
       if not existing.empty:
           existing_set = set(existing[['date', 'region', 'fuel_type']].itertuples(index=False, name=None))
           df_set = set(df[['date', 'region', 'fuel_type']].itertuples(index=False, name=None))
           df = df[~df[['date', 'region', 'fuel_type']].apply(tuple, axis=1).isin(existing_set)]
       df.to_sql('fuel_prices', conn, if_exists='append', index=False)
       conn.close()
       print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Stored {len(df)} new rows in fuel_data.db")

def load_data():
       try:
           conn = sqlite3.connect('fuel_data.db')
           query = "SELECT * FROM fuel_prices ORDER BY date"
           df = pd.read_sql(query, conn)
           conn.close()
           return df
       except Exception as e:
           print(f"Error loading data: {e}")
           return pd.DataFrame()

def job():
       print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled data update...")
       df = fetch_fuel_data()
       store_data(df)

if __name__ == "__main__":
       # Schedule the job to run daily at 2:00 AM
       schedule.every().day.at("02:00").do(job)
       print("Scheduler started. Waiting for scheduled tasks...")
       
       # Keep the script running to check for scheduled tasks
       while True:
           schedule.run_pending()
           time.sleep(60)  # Check every minute