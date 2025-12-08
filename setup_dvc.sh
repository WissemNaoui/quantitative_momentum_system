#!/bin/bash

# DVC Setup Script for Quantitative Momentum System

set -e

echo "=========================================="
echo "DVC Setup for Momentum System"
echo "=========================================="
echo ""

# Check if DVC is installed
if ! command -v dvc &> /dev/null; then
    echo "📦 Installing DVC..."
    pip install "dvc[all]"
else
    echo "✅ DVC already installed"
fi

# Initialize DVC if not already initialized
if [ ! -d ".dvc" ]; then
    echo "🔧 Initializing DVC..."
    dvc init
    git add .dvc .dvcignore
    git commit -m "Initialize DVC" || echo "DVC already initialized in git"
else
    echo "✅ DVC already initialized"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/raw data/processed models
touch data/.gitkeep models/.gitkeep

# Setup DVC remote (optional)
read -p "Do you want to configure DVC remote storage? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Select storage type:"
    echo "1) Amazon S3"
    echo "2) Google Cloud Storage"
    echo "3) Local/Network path"
    echo "4) Skip for now"
    read -p "Choice (1-4): " storage_choice
    
    case $storage_choice in
        1)
            read -p "S3 bucket name (e.g., s3://my-bucket/momentum): " s3_path
            dvc remote add -d storage "$s3_path"
            echo "✅ S3 remote configured"
            echo "⚠️  Set AWS credentials:"
            echo "   dvc remote modify storage access_key_id YOUR_KEY"
            echo "   dvc remote modify storage secret_access_key YOUR_SECRET"
            ;;
        2)
            read -p "GCS bucket name (e.g., gs://my-bucket/momentum): " gcs_path
            dvc remote add -d storage "$gcs_path"
            echo "✅ GCS remote configured"
            echo "⚠️  Make sure you have gcloud credentials configured"
            ;;
        3)
            read -p "Local/Network path (e.g., /mnt/shared/momentum): " local_path
            dvc remote add -d storage "$local_path"
            echo "✅ Local remote configured"
            ;;
        *)
            echo "⏭️  Skipping remote storage setup"
            ;;
    esac
fi

# Track data and models with DVC
echo ""
echo "📊 Setting up DVC tracking..."

# Add .gitkeep files to track empty directories
if [ ! -f "data/.gitkeep" ]; then
    touch data/.gitkeep
fi
if [ ! -f "models/.gitkeep" ]; then
    touch models/.gitkeep
fi

# Create .dvcignore if it doesn't exist
if [ ! -f ".dvcignore" ]; then
    cat > .dvcignore << 'EOF'
# Add patterns of files that DVC should ignore
*.pyc
__pycache__
.git
.env
EOF
fi

echo ""
echo "=========================================="
echo "✅ DVC Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Run the pipeline:"
echo "   dvc repro"
echo ""
echo "2. Track data/models:"
echo "   dvc add data/ models/"
echo "   git add data.dvc models.dvc"
echo "   git commit -m 'Track data and models with DVC'"
echo ""
echo "3. Push to remote (if configured):"
echo "   dvc push"
echo ""
echo "4. View pipeline:"
echo "   dvc dag"
echo ""
