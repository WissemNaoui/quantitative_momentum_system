"""
Momentum Strategy Backtester

This module validates the ROC² trend quality metric using historical data.
It runs a grid search over different lookback windows and holding periods,
tracking performance with MLflow.

The strategy:
1. Every N days, score all tickers using calculate_trend_quality()
2. Buy the highest-scoring ticker (if score > 0)
3. Hold for H days, then repeat

This proves whether the metric has predictive power.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import mlflow
import matplotlib.pyplot as plt
import os
import pickle
from src.math_utils import calculate_trend_quality


class MomentumBacktester:
    def __init__(self, tickers, start_date="2024-01-01"):
        """
        Initialize backtester with a universe of stocks.
        
        Args:
            tickers: List of ticker symbols to trade
            start_date: Start date for historical data (YYYY-MM-DD)
        """
        self.tickers = tickers
        self.start_date = start_date
        self.data = None

    def fetch_data(self):
        """
        Download historical price data with smart fallback strategy:
        1. Try cache first (fast)
        2. Try FinancialDatasets.ai (reliable, no rate limits)
        3. Fallback to YFinance if FD API key not set
        """
        # Create cache filename based on tickers and date
        cache_dir = ".cache"
        os.makedirs(cache_dir, exist_ok=True)
        tickers_hash = hash(tuple(sorted(self.tickers)))
        cache_file = f"{cache_dir}/data_{tickers_hash}_{self.start_date}.pkl"
        
        # 1. Try cache first
        if os.path.exists(cache_file):
            try:
                print(f"📦 Loading from cache: {cache_file}")
                with open(cache_file, 'rb') as f:
                    self.data = pickle.load(f)
                print(f"✅ Loaded {len(self.data)} days from cache")
                return self
            except Exception as e:
                print(f"⚠️  Cache load failed: {e}")
        
        # 2. Try FinancialDatasets.ai (preferred)
        fd_api_key = os.getenv("FD_API_KEY")
        
        if fd_api_key:
            try:
                print("🚀 Using FinancialDatasets.ai (reliable, no rate limits)")
                from src.fd_loader import fetch_history_fd
                
                self.data = fetch_history_fd(
                    self.tickers, 
                    start_date=self.start_date,
                    api_key=fd_api_key
                )
                
                # Save to cache
                with open(cache_file, 'wb') as f:
                    pickle.dump(self.data, f)
                print(f"💾 Cached to: {cache_file}")
                
                return self
                
            except Exception as e:
                print(f"⚠️  FinancialDatasets.ai failed: {e}")
                print("🔄 Falling back to Yahoo Finance...")
        else:
            print("ℹ️  FD_API_KEY not set, using Yahoo Finance")
            print("   (Set FD_API_KEY for better reliability)")
        
        # 3. Fallback to YFinance
        print(f"📥 Fetching history for {len(self.tickers)} tickers from YFinance...")
        
        try:
            # Download Close prices only
            self.data = yf.download(self.tickers, start=self.start_date, progress=False)['Close']
            
            # Handle single ticker case (yfinance returns Series instead of DataFrame)
            if len(self.tickers) == 1:
                self.data = pd.DataFrame({self.tickers[0]: self.data})
            
            # Forward fill missing data and drop any remaining NaNs
            self.data = self.data.ffill().dropna()
            
            print(f"✅ Downloaded {len(self.data)} days of data")
            
            # Save to cache
            with open(cache_file, 'wb') as f:
                pickle.dump(self.data, f)
            print(f"💾 Cached to: {cache_file}")
            
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch data from both FinancialDatasets.ai and YFinance!\n"
                f"Error: {e}\n"
                f"Solution: Set FD_API_KEY environment variable for reliable data access."
            )
        
        return self

    def run(self, lookback_window=20, holding_period=10):
        """
        Run backtest with specified parameters.
        
        Args:
            lookback_window: Number of days to calculate trend quality over
            holding_period: Number of days to hold each position
            
        Returns:
            tuple: (final_portfolio_value, equity_curve_list)
        """
        dates = self.data.index
        cash = 10000
        equity_curve = [cash]
        trades = []
        
        # Step through time (walk-forward simulation)
        for i in range(lookback_window, len(dates) - holding_period, holding_period):
            current_date = dates[i]
            
            # 1. Get window of past data (no look-ahead bias)
            window = self.data.iloc[i-lookback_window:i]
            
            # 2. Score every ticker using our ROC² metric
            scores = {}
            for ticker in self.tickers:
                try:
                    score, slope, r2 = calculate_trend_quality(window[ticker])
                    scores[ticker] = score
                except Exception as e:
                    # Ticker might have missing data in this window
                    continue
            
            # 3. Pick Winner (Highest Score)
            if not scores:
                equity_curve.append(cash)
                continue
                
            best_ticker = max(scores, key=scores.get)
            best_score = scores[best_ticker]
            
            # 4. Execute Trade (Only if positive trend)
            if best_score > 0:
                buy_price = self.data.loc[current_date, best_ticker]
                sell_date = dates[i + holding_period]
                sell_price = self.data.loc[sell_date, best_ticker]
                
                roi = (sell_price - buy_price) / buy_price
                cash = cash * (1 + roi)
                
                trades.append({
                    'date': current_date,
                    'ticker': best_ticker,
                    'score': best_score,
                    'buy': buy_price,
                    'sell': sell_price,
                    'roi': roi
                })
            
            equity_curve.append(cash)
        
        # Store trades for analysis
        self.trades = pd.DataFrame(trades)
        
        return cash, equity_curve


def run_experiment():
    """
    Run MLflow experiment to find optimal parameters.
    
    This tests different combinations of lookback windows and holding periods
    to find which settings maximize returns.
    """
    # Test on a mix of tech stocks (you can customize this universe)
    universe = ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'AMD', 'META', 'GOOGL']
    
    print("=" * 60)
    print("🔬 MOMENTUM STRATEGY BACKTEST")
    print("=" * 60)
    
    backtester = MomentumBacktester(universe, start_date="2024-01-01").fetch_data()
    
    mlflow.set_experiment("Momentum_Strategy_R2")
    
    # Grid Search Parameters
    lookbacks = [10, 20, 30]
    holdings = [5, 10, 15]
    
    results = []
    
    for lb in lookbacks:
        for hp in holdings:
            print(f"\n📊 Testing: Lookback={lb}, Holding={hp}")
            
            with mlflow.start_run(run_name=f"Win_{lb}_Hold_{hp}"):
                # Log parameters
                mlflow.log_param("lookback", lb)
                mlflow.log_param("holding", hp)
                mlflow.log_param("universe_size", len(universe))
                
                # Run backtest
                final_val, curve = backtester.run(lb, hp)
                
                # Calculate metrics
                roi = (final_val - 10000) / 10000
                max_equity = max(curve)
                drawdown = (max_equity - final_val) / max_equity if max_equity > 0 else 0
                
                # Log metrics
                mlflow.log_metric("total_roi", roi)
                mlflow.log_metric("final_value", final_val)
                mlflow.log_metric("max_drawdown", drawdown)
                mlflow.log_metric("num_trades", len(backtester.trades))
                
                # Save equity curve chart
                plt.figure(figsize=(10, 6))
                plt.plot(curve, linewidth=2)
                plt.axhline(y=10000, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
                plt.title(f"Equity Curve (Lookback={lb}, Hold={hp})\nFinal ROI: {roi:.2%}")
                plt.xlabel("Trade Number")
                plt.ylabel("Portfolio Value ($)")
                plt.legend()
                plt.grid(alpha=0.3)
                plt.tight_layout()
                plt.savefig("curve.png", dpi=150)
                mlflow.log_artifact("curve.png")
                plt.close()
                
                # Save trade log
                if len(backtester.trades) > 0:
                    backtester.trades.to_csv("trades.csv", index=False)
                    mlflow.log_artifact("trades.csv")
                
                results.append({
                    'lookback': lb,
                    'holding': hp,
                    'roi': roi,
                    'final_value': final_val,
                    'trades': len(backtester.trades)
                })
                
                print(f"   → ROI: {roi:+.2%} | Final: ${final_val:,.0f} | Trades: {len(backtester.trades)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📈 RESULTS SUMMARY")
    print("=" * 60)
    results_df = pd.DataFrame(results).sort_values('roi', ascending=False)
    print(results_df.to_string(index=False))
    
    best = results_df.iloc[0]
    print(f"\n🏆 WINNER: Lookback={int(best['lookback'])}, Holding={int(best['holding'])}")
    print(f"   ROI: {best['roi']:+.2%}")
    print(f"\n💡 Update your scanner.py with these parameters!")
    print("\n✅ Backtesting Complete. Run 'mlflow ui' to explore all runs.")


if __name__ == "__main__":
    run_experiment()