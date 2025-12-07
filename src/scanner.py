import requests
import pandas as pd
import io
import os
import time
import yfinance as yf
from src.math_utils import calculate_trend_quality

# --- CONFIGURATION ---
LOOKBACK_WINDOW = 20
BATCH_SIZE = 10       # Small batch to avoid YF bans
DELAY_SECONDS = 2     # Polite wait time
MIN_R2_THRESHOLD = 0.7 # Minimum smoothness (0.0 to 1.0)

# Fallback list if Finviz API Key is missing
FALLBACK_UNIVERSE = [
    'NVDA', 'MSFT', 'AAPL', 'AMZN', 'GOOGL', 'META', 'TSLA', 
    'AMD', 'AVGO', 'CRM', 'NFLX', 'ADBE', 'INTC', 'QCOM', 'TXN',
    'AMAT', 'MU', 'NOW', 'IBM', 'UBER', 'ABNB', 'PLTR', 'COIN'
]

def get_finviz_data():
    """
    Fetches tickers from Finviz Elite.
    Returns a DataFrame with a 'Ticker' column.
    """
    token = os.getenv("FINVIZ_API_TOKEN")
    
    if not token:
        print("⚠️  FINVIZ_API_TOKEN not found. Switching to Fallback Universe.")
        return pd.DataFrame({'Ticker': FALLBACK_UNIVERSE})
    
    url = "https://elite.finviz.com/export.ashx"
    params = {
        "auth": token,
        "f": "fa_div_pos,sec_technology", # Tech stocks with dividends
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
        print("🔄 Using Fallback Universe instead.")
        return pd.DataFrame({'Ticker': FALLBACK_UNIVERSE})

def analyze_market():
    # 1. Get List of Tickers
    df_finviz = get_finviz_data()
    if df_finviz.empty: 
        return pd.DataFrame()

    all_tickers = df_finviz['Ticker'].tolist()
    valid_scores = []
    
    print(f"📥 Scanning {len(all_tickers)} tickers using Yahoo Finance...")
    
    # 2. BATCH PROCESSING
    for i in range(0, len(all_tickers), BATCH_SIZE):
        batch = all_tickers[i : i + BATCH_SIZE]
        print(f"   Processing batch {i+1}-{min(i+BATCH_SIZE, len(all_tickers))}...")
        
        try:
            # Download 3 months of data to ensure we have enough for 20-day lookback
            # auto_adjust=True handles splits/dividends
            data = yf.download(batch, period="3mo", progress=False, group_by='ticker', auto_adjust=True)
            
            # 3. SCORE EACH TICKER
            for ticker in batch:
                try:
                    # Extract history for specific ticker
                    # Handle YF multi-index (Batch) vs Single Index (One ticker)
                    if len(batch) > 1:
                        if ticker not in data.columns: continue
                        history = data[ticker]['Close'].dropna()
                    else:
                        history = data['Close'].dropna()

                    # Check data length
                    if len(history) < LOOKBACK_WINDOW: continue

                    # Get the specific window for analysis
                    recent_window = history.tail(LOOKBACK_WINDOW)
                    
                    # --- CORE LOGIC IMPORTED FROM MATH_UTILS ---
                    score, slope, r2 = calculate_trend_quality(recent_window)
                    
                    # Filter: Must be moving UP (Score > 0) and SMOOTH (R2 > Threshold)
                    if score > 0 and r2 > MIN_R2_THRESHOLD:
                        valid_scores.append({
                            "Ticker": ticker,
                            "Score": round(score, 6),
                            "R2": round(r2, 4),
                            "Slope": round(slope, 6),
                            "Price": round(recent_window.iloc[-1], 2)
                        })
                except Exception as e:
                    # Specific ticker error, skip it
                    continue
                        
        except Exception as e:
            print(f"⚠️  Batch failed: {e}")
            
        # Sleep to prevent rate limiting
        time.sleep(DELAY_SECONDS)

    if not valid_scores:
        print("\n⚠️  No stocks passed the criteria!")
        return pd.DataFrame()

    # 4. RANKING
    results = pd.DataFrame(valid_scores)
    # Sort by the Score (Slope * R2)
    results = results.sort_values('Score', ascending=False)
    
    return results.head(10)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 MOMENTUM SCANNER (Live)")
    print("="*60)
    
    top_picks = analyze_market()
    
    if not top_picks.empty:
        print("\n🏆 TOP PICKS FOR TOMORROW:")
        print(top_picks.to_string(index=False))
        
        # Save to CSV with timestamp
        filename = f"picks_{pd.Timestamp.now().strftime('%Y-%m-%d')}.csv"
        top_picks.to_csv(filename, index=False)
        print(f"\n💾 Saved results to {filename}")
    else:
        print("No stocks passed the strict filter criteria.")
