#!/bin/bash

# Quantitative Momentum System - Quick Start Script

set -e  # Exit on error

echo "=========================================="
echo "Quantitative Momentum System Setup"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Activate the environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Test the core math:"
echo "   python tests/test_math_utils.py"
echo ""
echo "3. Run the backtester:"
echo "   python -m src.backtester"
echo ""
echo "4. View results:"
echo "   mlflow ui"
echo ""
echo "5. Set your Finviz API key:"
echo "   export FINVIZ_API_TOKEN='your_token'"
echo ""
echo "6. Run the scanner:"
echo "   python -m src.scanner"
echo ""
