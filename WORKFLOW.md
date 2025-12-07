# Quantitative Momentum System - Daily Workflow

## 🎯 Your Mission

Find stocks with **high momentum** and **low noise** using the ROC² metric.

---

## 📅 One-Time Setup (Do This Once)

### Step 1: Navigate to Project
```bash
cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system
```

### Step 2: Activate Environment
```bash
source venv/bin/activate
```

### Step 3: Verify Installation
```bash
python tests/test_math_utils.py
```

You should see: `✅ All tests passed!`

---

## 🔬 Research Phase (Do This Once to Find Optimal Settings)

### Step 1: Run Backtester
```bash
python -m src.backtester
```

This will:
- Test 9 different parameter combinations
- Save results to MLflow
- Generate equity curves
- Take ~2-5 minutes depending on your internet speed

### Step 2: Analyze Results
```bash
mlflow ui
```

Then open: http://localhost:5000

**What to look for:**
- Sort runs by `total_roi` (descending)
- Click on the best run
- Note the `lookback` and `holding` parameters
- Check the equity curve (should be smooth upward trend)

### Step 3: Update Scanner
Edit `src/scanner.py` and update line 24:

```python
LOOKBACK_WINDOW = 20  # Use the winning value from MLflow
```

---

## 📊 Production Phase (Do This Daily)

### Step 1: Set API Key (First Time Only)
```bash
export FINVIZ_API_TOKEN="your_finviz_elite_token_here"
```

To make it permanent, add to your `~/.bashrc`:
```bash
echo 'export FINVIZ_API_TOKEN="your_token"' >> ~/.bashrc
```

### Step 2: Run Scanner
```bash
python -m src.scanner
```

**Output:**
```
🏆 TOP PICKS FOR TODAY
Ticker    Score    R2     Momentum_Pct  Price
NVDA      0.0234   0.945  +12.5%        $875.23
AAPL      0.0189   0.912  +8.3%         $195.45
...
```

### Step 3: Review Results

**What each column means:**
- **Ticker**: Stock symbol
- **Score**: Slope × R² (higher = better)
- **R2**: How smooth the trend is (0-1, higher = more predictable)
- **Momentum_Pct**: Price change over lookback window
- **Price**: Current price

**Decision Rules:**
1. Only consider stocks with **Score > 0** (already filtered)
2. Prefer stocks with **R² > 0.85** (smooth trends)
3. Check the top 3-5 picks
4. Do your own due diligence (news, fundamentals, etc.)

### Step 4: Track Your Picks

The scanner saves results to: `picks_YYYYMMDD_HHMM.csv`

Keep a trading journal:
```bash
# Create a journal file
echo "Date,Ticker,Entry_Price,Exit_Price,ROI,Notes" > trading_journal.csv

# After each trade, add a line:
echo "2024-12-07,NVDA,875.23,920.50,+5.2%,Strong R2 signal" >> trading_journal.csv
```

---

## 🔄 Weekly Maintenance

### Review Performance
```bash
# Compare your actual results vs backtest
python -m src.backtester  # Re-run with recent data
```

### Update Stock Universe

If you want to scan different stocks, edit `src/scanner.py`:

```python
# Around line 35, modify the fallback list:
return ['NVDA', 'AAPL', 'MSFT', 'YOUR_STOCKS_HERE']
```

Or adjust Finviz filters (line 31):
```python
"f": "sh_opt_option,sh_price_o5,sh_avgvol_o500",  # Modify these
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "FINVIZ_API_TOKEN not set"
```bash
# Check if it's set
echo $FINVIZ_API_TOKEN

# If empty, set it
export FINVIZ_API_TOKEN="your_token"
```

### "No buy signals today"
This is normal! The strategy only buys when conditions are right.

Possible reasons:
- Market is in downtrend (all scores negative)
- High volatility (low R² values)
- Not enough data for some tickers

### YFinance Download Errors
```bash
# YFinance sometimes has rate limits
# Just wait 1 minute and try again
sleep 60 && python -m src.scanner
```

---

## 📈 Advanced: Customization

### Change Lookback Window
Edit `src/scanner.py`:
```python
LOOKBACK_WINDOW = 30  # Try 10, 20, 30, or 60
```

### Add More Filters
Edit `src/scanner.py`, around line 125:
```python
# Example: Only stocks above $50
buys = scores_df[
    (scores_df['Score'] > 0) & 
    (scores_df['Price'] > 50)
].head(top_n)
```

### Test on Different Time Periods
Edit `src/backtester.py`, line 121:
```python
backtester = MomentumBacktester(universe, start_date="2023-01-01")
```

---

## 🎓 Understanding the Output

### What is a "Good" Score?

**Typical ranges:**
- **Score > 0.02**: Excellent (strong, smooth uptrend)
- **Score 0.01-0.02**: Good (solid momentum)
- **Score 0.005-0.01**: Moderate (worth considering)
- **Score < 0.005**: Weak (probably skip)

### What is a "Good" R²?

- **R² > 0.90**: Very smooth (predictable)
- **R² 0.80-0.90**: Smooth (good)
- **R² 0.70-0.80**: Moderate noise
- **R² < 0.70**: Choppy (risky)

### Example Interpretation

```
Ticker: NVDA
Score: 0.0234
R2: 0.945
Momentum_Pct: +12.5%
```

**Translation:**
"NVDA has gone up 12.5% over the last 20 days in a very smooth, predictable manner (R²=0.945). The combined score of 0.0234 is excellent."

---

## 🚀 Quick Reference

```bash
# Daily routine (30 seconds)
cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system
source venv/bin/activate
python -m src.scanner

# View backtest results
mlflow ui

# Run tests
python tests/test_math_utils.py
```

---

**Remember:** This is a tool to find opportunities. Always do your own research before trading!
