# 🚀 How to Run - Simple Guide

## ✅ **Easiest Way: Local Python (RECOMMENDED)**

This is the fastest and simplest way to run everything.

### **Step 1: Setup (One-time)**

```bash
cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system

# Activate virtual environment (already created)
source venv/bin/activate

# Set API key
export FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4"
```

### **Step 2: Run Backtester**

```bash
python -m src.backtester
```

**What it does:**
- Tests 9 parameter combinations
- Logs results to MLflow
- Takes ~2-5 minutes
- Creates: `mlflow.db`, `mlruns/`, `trades.csv`, `curve.png`

### **Step 3: View Results**

```bash
mlflow ui --port 5000
```

Then open: http://localhost:5000

### **Step 4: Run Scanner (Get Stock Picks)**

```bash
python -m src.scanner
```

**What it does:**
- Analyzes stocks
- Generates top picks
- Takes ~30 seconds
- Creates: `picks_YYYYMMDD_HHMM.csv`

---

## 🐳 **Docker (After Fixing)**

The Docker build failed because of a configuration issue. Here's how to fix and run:

### **Fix 1: Build Docker Image**

```bash
cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system

# Build the image
docker build -t momentum-system:latest .
```

### **Fix 2: Run with Docker**

```bash
# Run backtester
docker run --rm \
  -e FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/.cache:/app/.cache \
  -v $(pwd)/mlruns:/app/mlruns \
  momentum-system:latest

# Run scanner
docker run --rm \
  -e FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4" \
  -v $(pwd)/data:/app/data \
  momentum-system:latest \
  python -m src.scanner
```

### **Fix 3: Docker Compose**

```bash
# Create .env file first
echo 'FD_API_KEY=ff4903af-75da-4215-bac5-5fc43987e6d4' > .env

# Start all services
docker-compose up
```

---

## 📋 **Quick Commands (Using Makefile)**

The Makefile makes everything easier:

```bash
# Setup
make install              # Install dependencies (already done)

# Run
make backtest             # Run backtester
make scan                 # Run scanner
make mlflow               # Start MLflow UI

# Docker
make docker-build         # Build Docker image
make docker-run           # Run backtester in Docker
make docker-scan          # Run scanner in Docker
make docker-compose       # Start all services

# Testing
make test                 # Run tests

# Cleanup
make clean                # Remove temp files
make help                 # See all commands
```

---

## ⚡ **Right Now - Quick Test**

Want to see it work immediately? Run this:

```bash
cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system
source venv/bin/activate
export FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4"

# Quick test (30 seconds)
python tests/test_math_utils.py

# Run scanner (1 minute)
python -m src.scanner

# Run backtester (5 minutes)
python -m src.backtester

# View results
mlflow ui --port 5000
```

---

## 🐛 **Troubleshooting**

### **Issue: Docker build fails**

**Solution:** Use local Python instead (faster anyway):
```bash
source venv/bin/activate
python -m src.backtester
```

### **Issue: "No module named 'src'"**

**Solution:** Make sure you're in the project directory:
```bash
cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system
```

### **Issue: API key not set**

**Solution:** Export it:
```bash
export FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4"
```

### **Issue: Virtual environment not activated**

**Solution:**
```bash
source venv/bin/activate
```

---

## 📊 **What You'll Get**

### **After Backtester:**
```
quantitative_momentum_system/
├── mlflow.db              # Experiment database
├── mlruns/                # Experiment artifacts
├── trades.csv             # All trades
├── curve.png              # Equity curve chart
└── .cache/                # Cached data
```

### **After Scanner:**
```
picks_20241208_1830.csv    # Today's top picks
```

### **MLflow UI Shows:**
- All experiment runs
- Parameters tested
- ROI for each combination
- Equity curves
- Trade details

---

## 🎯 **Recommended Workflow**

### **Daily:**
```bash
source venv/bin/activate
export FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4"
python -m src.scanner
```

### **Weekly:**
```bash
source venv/bin/activate
export FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4"
python -m src.backtester
mlflow ui --port 5000
```

---

## 💡 **Pro Tips**

1. **Add API key to .bashrc** (permanent):
   ```bash
   echo 'export FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4"' >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Create alias** for quick access:
   ```bash
   echo 'alias momentum="cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system && source venv/bin/activate"' >> ~/.bashrc
   ```

3. **Use tmux** for long-running backtests:
   ```bash
   tmux new -s backtest
   python -m src.backtester
   # Detach: Ctrl+B, then D
   # Reattach: tmux attach -t backtest
   ```

---

## ✅ **Summary**

**Easiest way to run:**
```bash
cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system
source venv/bin/activate
export FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4"
python -m src.scanner  # or src.backtester
```

**That's it!** 🚀

Docker is optional and mainly for production deployment.
