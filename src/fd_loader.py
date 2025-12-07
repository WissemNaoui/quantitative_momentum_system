"""
FinancialDatasets.ai Data Loader

This module provides a robust data loader for the FinancialDatasets.ai API,
which offers:
- Clean, reliable historical data
- No rate limits (unlike Yahoo Finance)
- Consistent data format
- Better uptime

This is used as a fallback when YFinance fails or for production systems
that need reliability.
"""

import requests
import pandas as pd
import os
import time
from datetime import datetime, timedelta


def fetch_history_fd(tickers, start_date=None, lookback_days=365, api_key=None):
    """
    Fetches historical price data from FinancialDatasets.ai
    
    Args:
        tickers: List of ticker symbols
        start_date: Optional start date (YYYY-MM-DD). If None, uses lookback_days
        lookback_days: Number of days to fetch (default 365)
        api_key: API key. If None, reads from FD_API_KEY environment variable
        
    Returns:
        DataFrame with DatetimeIndex and columns for each ticker (Close prices)
    """
    # Get API key
    if api_key is None:
        api_key = os.getenv("FD_API_KEY")
        if not api_key:
            raise ValueError(
                "FinancialDatasets.ai API key not found!\n"
                "Set environment variable: export FD_API_KEY='your_key'"
            )
    
    # Calculate date range
    if start_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    all_data = []
    failed_tickers = []
    
    print(f"🚀 Fetching data from FinancialDatasets.ai...")
    print(f"   Tickers: {len(tickers)}")
    print(f"   Date Range: {start_date} to {end_date}")
    
    for i, ticker in enumerate(tickers, 1):
        url = "https://api.financialdatasets.ai/prices/"
        params = {
            "ticker": ticker,
            "interval": "day",
            "interval_multiplier": 1,
            "start_date": start_date,
            "end_date": end_date,
            "limit": 1000  # Max allowed
        }
        headers = {"X-API-KEY": api_key}
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                prices = data.get('prices', [])
                
                if prices:
                    df = pd.DataFrame(prices)
                    
                    # Standardize columns to match YFinance format
                    df = df.rename(columns={'time': 'Date', 'close': 'Close'})
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.sort_values('Date')
                    df.set_index('Date', inplace=True)
                    df['Ticker'] = ticker
                    all_data.append(df[['Close', 'Ticker']])
                    
                    print(f"   [{i}/{len(tickers)}] ✅ {ticker}: {len(df)} days")
                else:
                    print(f"   [{i}/{len(tickers)}] ⚠️  {ticker}: No data returned")
                    failed_tickers.append(ticker)
                    
            elif resp.status_code == 429:
                print(f"   [{i}/{len(tickers)}] ⏸️  {ticker}: Rate limit hit, waiting...")
                time.sleep(2)
                # Retry once
                resp = requests.get(url, params=params, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    prices = data.get('prices', [])
                    if prices:
                        df = pd.DataFrame(prices)
                        df = df.rename(columns={'time': 'Date', 'close': 'Close'})
                        df['Date'] = pd.to_datetime(df['Date'])
                        df = df.sort_values('Date')
                        df.set_index('Date', inplace=True)
                        df['Ticker'] = ticker
                        all_data.append(df[['Close', 'Ticker']])
                        print(f"   [{i}/{len(tickers)}] ✅ {ticker}: {len(df)} days (retry)")
                else:
                    failed_tickers.append(ticker)
            else:
                print(f"   [{i}/{len(tickers)}] ❌ {ticker}: HTTP {resp.status_code}")
                failed_tickers.append(ticker)
                
        except Exception as e:
            print(f"   [{i}/{len(tickers)}] ⚠️  {ticker}: {str(e)[:50]}")
            failed_tickers.append(ticker)
            
        # Be polite to the API (small delay between requests)
        if i < len(tickers):
            time.sleep(0.1)
    
    if not all_data:
        raise ValueError("No data fetched for any ticker!")
    
    # Combine all into one big dataframe
    full_df = pd.concat(all_data)
    
    # Pivot to match the shape expected by Backtester (Index=Date, Columns=Tickers)
    pivot_df = full_df.pivot_table(index='Date', columns='Ticker', values='Close')
    
    # Forward fill missing values
    pivot_df = pivot_df.ffill()
    
    print(f"\n✅ Data fetch complete!")
    print(f"   Successful: {len(tickers) - len(failed_tickers)}/{len(tickers)}")
    print(f"   Date range: {pivot_df.index.min()} to {pivot_df.index.max()}")
    print(f"   Total days: {len(pivot_df)}")
    
    if failed_tickers:
        print(f"   ⚠️  Failed tickers: {', '.join(failed_tickers)}")
    
    return pivot_df


def fetch_single_ticker_fd(ticker, lookback_days=30, api_key=None):
    """
    Convenience function to fetch data for a single ticker.
    
    Args:
        ticker: Ticker symbol
        lookback_days: Number of days to fetch
        api_key: API key (optional, reads from env if not provided)
        
    Returns:
        Series of close prices with DatetimeIndex
    """
    df = fetch_history_fd([ticker], lookback_days=lookback_days, api_key=api_key)
    return df[ticker]
