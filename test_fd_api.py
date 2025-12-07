import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# 1. SETUP - Read from environment variable (secure)
API_KEY = os.getenv("FD_API_KEY")
if not API_KEY:
    print("❌ Error: FD_API_KEY environment variable not set!")
    print("   Run: export FD_API_KEY='your_key_here'")
    exit(1)

TICKER = "TSLA"
URL = "https://api.financialdatasets.ai/prices/"

# Calculate date range (last 100 days)
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")

# 2. REQUEST
params = {
    "ticker": TICKER,
    "interval": "day",
    "interval_multiplier": 1,
    "start_date": start_date,
    "end_date": end_date,
    "limit": 100
}
headers = {"X-API-KEY": API_KEY}

print(f"📡 Connecting to FinancialDatasets.ai for {TICKER}...")
response = requests.get(URL, params=params, headers=headers)

if response.status_code == 200:
    data = response.json()
    
    # 3. PARSE
    # The API returns a list of dictionaries under the key 'prices' usually
    if 'prices' in data:
        df = pd.DataFrame(data['prices'])
        print(f"✅ Success! Received {len(df)} days of data.")
        print("\n📊 Sample Data:")
        print(df.head())
        print(f"\n📋 Columns: {list(df.columns)}")
        
        # Plot to prove it's real
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        df.set_index('time', inplace=True)
        
        plt.figure(figsize=(12, 6))
        df['close'].plot(title=f"{TICKER} Price from FinancialDatasets.ai", linewidth=2)
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig("fd_test_chart.png", dpi=150)
        print("\n📈 Chart saved to fd_test_chart.png")
        
        # Show data quality metrics
        print(f"\n📊 Data Quality:")
        print(f"   Date Range: {df.index.min()} to {df.index.max()}")
        print(f"   Total Days: {len(df)}")
        print(f"   Missing Values: {df['close'].isna().sum()}")
        print(f"   Price Range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        
    else:
        print("⚠️ Data format unexpected. Keys found:", list(data.keys()))
        print("Raw response:", data)
else:
    print(f"❌ Error {response.status_code}: {response.text}")
