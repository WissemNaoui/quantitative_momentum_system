#!/bin/bash

# Quick Start Script for Quantitative Momentum System
# This gets you up and running in 3 minutes

set -e

echo "=========================================="
echo "🚀 Quantitative Momentum System"
echo "   Quick Start"
echo "=========================================="
echo ""

# Step 1: Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this from the project root directory"
    exit 1
fi

# Step 2: Setup environment variables
echo "📝 Step 1: Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo "   nano .env"
    echo ""
    read -p "Press Enter after you've added your API keys..."
else
    echo "✅ .env file already exists"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Step 3: Choose installation method
echo ""
echo "=========================================="
echo "Choose how you want to run:"
echo "=========================================="
echo ""
echo "1) 🐍 Local Python (fastest for development)"
echo "2) 🐳 Docker (recommended for production)"
echo "3) 📊 DVC Pipeline (full MLOps workflow)"
echo ""
read -p "Your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "=========================================="
        echo "🐍 Local Python Setup"
        echo "=========================================="
        echo ""
        
        # Check if venv exists
        if [ ! -d "venv" ]; then
            echo "📦 Creating virtual environment..."
            python3 -m venv venv
        fi
        
        echo "🔧 Activating virtual environment..."
        source venv/bin/activate
        
        echo "📥 Installing dependencies..."
        pip install -q -r requirements.txt
        
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "What would you like to run?"
        echo ""
        echo "1) Run backtester (find best parameters)"
        echo "2) Run scanner (get today's stock picks)"
        echo "3) Start MLflow UI (view results)"
        echo "4) Run tests"
        echo ""
        read -p "Your choice (1-4): " run_choice
        
        case $run_choice in
            1)
                echo ""
                echo "🔬 Running backtester..."
                python -m src.backtester
                echo ""
                echo "✅ Backtest complete! Run 'make mlflow' to view results"
                ;;
            2)
                echo ""
                echo "🎯 Running scanner..."
                python -m src.scanner
                echo ""
                echo "✅ Scan complete! Check picks_*.csv for results"
                ;;
            3)
                echo ""
                echo "📊 Starting MLflow UI..."
                echo "Open http://localhost:5000 in your browser"
                mlflow ui --port 5000
                ;;
            4)
                echo ""
                echo "🧪 Running tests..."
                python tests/test_math_utils.py
                ;;
            *)
                echo "Invalid choice"
                ;;
        esac
        ;;
        
    2)
        echo ""
        echo "=========================================="
        echo "🐳 Docker Setup"
        echo "=========================================="
        echo ""
        
        echo "📦 Building Docker image..."
        docker build -t momentum-system:latest .
        
        echo ""
        echo "✅ Docker image built!"
        echo ""
        echo "What would you like to run?"
        echo ""
        echo "1) Run backtester"
        echo "2) Run scanner"
        echo "3) Start all services (docker-compose)"
        echo ""
        read -p "Your choice (1-3): " docker_choice
        
        case $docker_choice in
            1)
                echo ""
                echo "🔬 Running backtester in Docker..."
                docker run --rm \
                    -e FD_API_KEY=$FD_API_KEY \
                    -v $(pwd)/data:/app/data \
                    -v $(pwd)/models:/app/models \
                    -v $(pwd)/.cache:/app/.cache \
                    -v $(pwd)/mlruns:/app/mlruns \
                    momentum-system:latest
                ;;
            2)
                echo ""
                echo "🎯 Running scanner in Docker..."
                docker run --rm \
                    -e FD_API_KEY=$FD_API_KEY \
                    -e FINVIZ_API_TOKEN=$FINVIZ_API_TOKEN \
                    -v $(pwd)/data:/app/data \
                    momentum-system:latest \
                    python -m src.scanner
                ;;
            3)
                echo ""
                echo "🚀 Starting all services..."
                echo "MLflow UI will be at http://localhost:5000"
                docker-compose up
                ;;
            *)
                echo "Invalid choice"
                ;;
        esac
        ;;
        
    3)
        echo ""
        echo "=========================================="
        echo "📊 DVC Pipeline Setup"
        echo "=========================================="
        echo ""
        
        # Check if DVC is installed
        if ! command -v dvc &> /dev/null; then
            echo "📦 Installing DVC..."
            pip install "dvc[all]"
        fi
        
        # Initialize DVC if needed
        if [ ! -d ".dvc" ]; then
            echo "🔧 Initializing DVC..."
            dvc init
        fi
        
        echo ""
        echo "📊 Running DVC pipeline..."
        dvc repro
        
        echo ""
        echo "✅ Pipeline complete!"
        echo ""
        echo "View results:"
        echo "  - MLflow UI: make mlflow"
        echo "  - Pipeline DAG: dvc dag"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ All done!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  - View results: make mlflow"
echo "  - Run tests: make test"
echo "  - See all commands: make help"
echo ""
