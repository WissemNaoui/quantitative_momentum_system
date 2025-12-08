#!/bin/bash
# Simple runner script - handles venv activation automatically

cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system
source venv/bin/activate
export FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4"
export FINVIZ_API_TOKEN="de26d606-709e-4801-a3a7-2771a43ff6f4"

case "$1" in
    backtest)
        echo "🔬 Running backtester..."
        python -m src.backtester
        ;;
    scan)
        echo "🎯 Running scanner..."
        python -m src.scanner
        ;;
    mlflow)
        echo "📊 Starting MLflow UI at http://localhost:5000"
        mlflow ui --port 5000
        ;;
    test)
        echo "🧪 Running tests..."
        python tests/test_math_utils.py
        ;;
    *)
        echo "Usage: ./run.sh [backtest|scan|mlflow|test]"
        echo ""
        echo "Commands:"
        echo "  backtest  - Run strategy backtester"
        echo "  scan      - Get today's stock picks"
        echo "  mlflow    - Start MLflow UI"
        echo "  test      - Run unit tests"
        ;;
esac
