import requests
import pandas as pd
import io
import os
import matplotlib.pyplot as plt
import yfinance as yf
import time
from src.math_utils import calculate_trend_quality

# --- CONFIGURATION ---
# UPDATED based on your Backtest Results
LOOKBACK_WINDOW = 20  
BATCH_SIZE = 10       # Small batch to avoid YF bans
DELAY_SECONDS = 3     # Polite wait time

def get_finviz_data():
    token = os.getenv("FINVIZ_API_TOKEN")
    if not token: raise ValueError("Set FINVIZ_API_TOKEN env var!")
    
    url = "https://elite.finviz.com/export.ashx"
    params = {
        "auth": token,
        # Using the "Dividend Tech" filter from your link
        "f": "fa_div_pos,sec_technology", 
        "o": "-perf52w",
        "c": "1,65" # Ticker, Price
    }
    
    print("📡 Fetching stock universe from Finviz Elite...")
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        print(f"✅ Found {len(df)} tickers matching criteria")
        return df
    except Exception as e:
        print(f"❌ Finviz Error: {e}")
        return pd.DataFrame()

def analyze_market():
    # 1. Get List of Tickers
    df_finviz = get_finviz_data()
    if df_finviz.empty: return pd.DataFrame()

    all_tickers = df_finviz['Ticker'].tolist()
    valid_scores = []
    
    print(f"📥 Scanning {len(all_tickers)} tickers using Yahoo Finance (Batched)...")
    
    # 2. BATCH PROCESSING (The "Anti-Ban" Logic)
    for i in range(0, len(all_tickers), BATCH_SIZE):
        batch = all_tickers[i : i + BATCH_SIZE]
        print(f"   Processing batch {i} to {i+len(batch)}...")
        
        try:
            # Download batch (approx 2 months to be safe for 20 day lookback)
            data = yf.download(batch, period="3mo", progress=False, group_by='ticker', auto_adjust=True)
            
            # 3. SCORE EACH TICKER
            for ticker in batch:
                try:
                    # Handle Multi-Index Dataframe from YF
                    if len(batch) > 1:
                        if ticker not in data.columns: continue
                        history = data[ticker]['Close'].dropna()
                    else:
                        # Single ticker case
                        history = data['Close'].dropna()

                    # We need at least 20 days
                    if len(history) < LOOKBACK_WINDOW: continue

                    # Get the most recent window
                    recent_window = history.tail(LOOKBACK_WINDOW)
                    
                    # RUN THE MATH
                    score, slope, r2 = calculate_trend_quality(recent_window)
                    
                    # LOGIC: Only keep Positive Trends with High R2 (Smoothness)
                    if score > 0 and r2 > 0.8:
                        valid_scores.append({
                            "Ticker": ticker,
                            "Score": score,
                            "R2": r2,
                            "Momentum_Slope": slope,
                            "Current_Price": round(recent_window.iloc[-1], 2)
                        })
                except Exception as e:
                    continue
                        
        except Exception as e:
            print(f"⚠️ Batch failed: {e}")
            
        # Sleep to be polite to Yahoo
        time.sleep(DELAY_SECONDS)

    if not valid_scores:
        print("\n⚠️  No valid scores calculated!")
        return pd.DataFrame()

    # 4. RANKING
    results = pd.DataFrame(valid_scores)
    # Sort by the "Quality Score" (Slope * R2)
    results = results.sort_values('Score', ascending=False)
    
    return results.head(10)

if __name__ == "__main__":
    print("\n============================================================")
    print("🎯 MOMENTUM SCANNER - YFINANCE MODE")
    print("============================================================")
    
    top_picks = analyze_market()
    
    if not top_picks.empty:
        print("\n🏆 TOP 10 MOMENTUM PICKS:")
        print(top_picks[['Ticker', 'Current_Price', 'Score', 'R2']])
        top_picks.to_csv("todays_picks.csv", index=False)
        print("\n✅ Saved to todays_picks.csv")
    else:
        print("No stocks passed the criteria.")