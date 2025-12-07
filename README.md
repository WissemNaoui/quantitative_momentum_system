# Quantitative Momentum System

A professional, modular trading system that identifies high-quality momentum stocks using the **ROC² (Rate of Change Squared)** metric.

## 🎯 The Strategy

This system combines **momentum** (slope) with **consistency** (R²) to find stocks that are:
- Moving up strongly (positive slope)
- Moving smoothly (high R² = low noise)

**Key Principle:** We only buy stocks with high `Score = Slope × R²`

## 🏗️ Architecture

```
quantitative_momentum_system/
├── src/
│   ├── math_utils.py      # Core ROC² calculation (shared by all modules)
│   ├── backtester.py      # Historical validation with MLflow
│   └── scanner.py         # Production scanner (Finviz + YFinance)
├── tests/
│   └── test_math_utils.py # Unit tests
├── requirements.txt
└── README.md
```

### Why This Design?

**Separation of Concerns:**
- `math_utils.py` contains the single source of truth for the metric
- Both backtester and scanner import the SAME function
- This ensures backtest results are predictive of live performance

**Testability:**
- The backtester validates the strategy on historical data
- The scanner applies the validated logic to live data
- No guesswork—only deploy strategies that pass backtesting

## 🚀 Setup

### 1. Create Virtual Environment

```bash
cd quantitative_momentum_system
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set API Key (for production scanner)

```bash
export FINVIZ_API_TOKEN="your_finviz_elite_token"
```

## 📊 Workflow

### Phase 1: Research (Find What Works)

Run the backtester to find optimal parameters:

```bash
python -m src.backtester
```

This will:
- Test different lookback windows (10, 20, 30 days)
- Test different holding periods (5, 10, 15 days)
- Track all results in MLflow
- Generate equity curves and trade logs

**View Results:**
```bash
mlflow ui
```

Open http://localhost:5000 and find the run with the highest ROI.

**Example Output:**
```
🏆 WINNER: Lookback=20, Holding=10
   ROI: +45.2%
```

### Phase 2: Production (Apply What Works)

Update `src/scanner.py` with the winning parameters:

```python
LOOKBACK_WINDOW = 20  # From your backtest results
```

Then run the scanner:

```bash
python -m src.scanner
```

**Example Output:**
```
🏆 TOP PICKS FOR TODAY
Ticker    Score    R2     Momentum_Pct  Price
NVDA      0.0234   0.945  +12.5%        $875.23
AAPL      0.0189   0.912  +8.3%         $195.45
...
```

### Phase 3: Verify (Test the Math)

Run unit tests to ensure the core logic is correct:

```bash
python tests/test_math_utils.py
```

## 🧮 The Math

### ROC² Metric

```python
def calculate_trend_quality(series):
    # 1. Convert to log prices (exponential → linear)
    y = np.log(series.values)
    x = np.arange(len(y))
    
    # 2. Fit linear regression
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    
    # 3. Calculate score
    r_squared = r_value ** 2
    score = slope * r_squared
    
    return score, slope, r_squared
```

**Why Log Prices?**
- A stock going from $100 → $110 is the same % gain as $200 → $220
- Log prices convert exponential growth to linear growth
- Makes regression more meaningful

**Why Multiply by R²?**
- A stock with slope=0.1 and R²=0.9 is better than slope=0.1 and R²=0.3
- High R² means the trend is smooth and predictable
- Low R² means the trend is noisy and unreliable

## 🔍 Key Features

### 1. **Consistency Between Backtest and Production**
Both modules use `calculate_trend_quality()` from `math_utils.py`. This ensures:
- What you backtest is what you deploy
- No "strategy drift" between research and production

### 2. **MLflow Experiment Tracking**
- Every backtest run is logged
- Compare parameters side-by-side
- Visualize equity curves
- Track trade-level details

### 3. **Robust Error Handling**
- Handles missing data gracefully
- Falls back to default universe if Finviz API fails
- Skips tickers with insufficient history

### 4. **Production-Ready Code**
- Proper logging and status messages
- Saves results to timestamped CSV files
- Clear separation of configuration and logic

## 📈 Next Steps

1. **Run the backtester** to validate the strategy
2. **Analyze results** in MLflow UI
3. **Update scanner parameters** with winning settings
4. **Run scanner daily** to get fresh picks
5. **Track performance** by saving daily results

## 🛠️ Customization

### Change the Stock Universe

Edit `backtester.py`:
```python
universe = ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'AMD', 'META', 'GOOGL']
```

### Adjust Filters

Edit `scanner.py`:
```python
MIN_PRICE = 5.0
MIN_VOLUME = 500000
```

### Add New Metrics

Add functions to `math_utils.py` and import them in both modules.

## 📝 Notes

- **Finviz Elite** is required for the production scanner (or modify to use free screener)
- **YFinance** is free and used for all historical data
- **MLflow** runs locally and stores data in `mlruns/` directory

## 🎓 Learning Resources

- [Linear Regression](https://en.wikipedia.org/wiki/Linear_regression)
- [R-squared](https://en.wikipedia.org/wiki/Coefficient_of_determination)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [YFinance Documentation](https://pypi.org/project/yfinance/)

---

**Built with:** Python, Pandas, NumPy, SciPy, YFinance, MLflow
