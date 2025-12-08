# 🚀 Complete Deployment Guide - DVC, GitHub Actions, Docker

## Overview

This guide will help you deploy your momentum system with:
- **DVC** - Version control for data and models
- **GitHub Actions** - Automated daily scans and weekly backtests
- **Docker** - Containerized deployment

---

## 📊 Part 1: DVC Setup (10 minutes)

### **What is DVC?**
DVC tracks your data and models like Git tracks code. Benefits:
- Version control for large files
- Reproducible pipelines
- Share data with team
- Remote storage (S3, GCS, etc.)

### **Step 1: Initialize DVC**

```bash
cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system

# Install DVC (already in requirements.txt)
source venv/bin/activate
pip install "dvc[all]"

# Initialize DVC
dvc init

# Commit DVC config
git add .dvc .dvcignore
git commit -m "Initialize DVC"
```

### **Step 2: Track Data with DVC**

```bash
# Track data directory
dvc add .cache/
dvc add models/

# This creates .cache.dvc and models.dvc files
git add .cache.dvc models.dvc .gitignore
git commit -m "Track data and models with DVC"
```

### **Step 3: Run DVC Pipeline**

```bash
# Run the entire pipeline
dvc repro

# View pipeline DAG
dvc dag
```

**What it does:**
- Runs fetch_data → backtest → scan
- Tracks all inputs/outputs
- Caches results
- Ensures reproducibility

### **Step 4: Setup Remote Storage (Optional)**

#### **Option A: AWS S3**

```bash
# Configure S3 remote
dvc remote add -d storage s3://your-bucket/momentum-system

# Set credentials
dvc remote modify storage access_key_id YOUR_KEY
dvc remote modify storage secret_access_key YOUR_SECRET

# Push data to S3
dvc push
```

#### **Option B: Google Cloud Storage**

```bash
# Configure GCS remote
dvc remote add -d storage gs://your-bucket/momentum-system

# Push data
dvc push
```

#### **Option C: Local/Network Storage**

```bash
# Use local or network path
dvc remote add -d storage /mnt/shared/momentum-system

# Push data
dvc push
```

---

## 🐳 Part 2: Docker Setup (15 minutes)

### **What is Docker?**
Docker packages your app with all dependencies. Benefits:
- Works anywhere
- Consistent environments
- Easy deployment
- Scalable

### **Step 1: Build Docker Image**

```bash
# Build the image
docker build -t momentum-system:latest .

# This takes ~5 minutes first time
```

### **Step 2: Test Docker Locally**

```bash
# Run backtester
docker run --rm \
  -e FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4" \
  -e FINVIZ_API_TOKEN="de26d606-709e-4801-a3a7-2771a43ff6f4" \
  -v $(pwd)/.cache:/app/.cache \
  -v $(pwd)/mlruns:/app/mlruns \
  momentum-system:latest

# Run scanner
docker run --rm \
  -e FD_API_KEY="ff4903af-75da-4215-bac5-5fc43987e6d4" \
  -e FINVIZ_API_TOKEN="de26d606-709e-4801-a3a7-2771a43ff6f4" \
  -v $(pwd)/data:/app/data \
  momentum-system:latest \
  python -m src.scanner
```

### **Step 3: Use Docker Compose**

```bash
# Start all services
docker-compose up

# This starts:
# - Backtester
# - Scanner
# - MLflow UI (http://localhost:5000)

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all
docker-compose down
```

### **Step 4: Push to Docker Hub (Optional)**

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag momentum-system:latest YOUR_USERNAME/momentum-system:latest

# Push to Docker Hub
docker push YOUR_USERNAME/momentum-system:latest

# Now anyone can run:
# docker pull YOUR_USERNAME/momentum-system:latest
```

---

## 🔄 Part 3: GitHub Actions Setup (20 minutes)

### **What is GitHub Actions?**
Automates your workflows. Benefits:
- Daily stock scans (automatic!)
- Weekly backtests (automatic!)
- Automated testing
- Automated deployment

### **Step 1: Create GitHub Repository**

```bash
cd /home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Momentum trading system with MLOps"

# Create repo on GitHub (via web or CLI)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/momentum-system.git
git branch -M main
git push -u origin main
```

### **Step 2: Add GitHub Secrets**

Go to your repo → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

```
FD_API_KEY = ff4903af-75da-4215-bac5-5fc43987e6d4
FINVIZ_API_TOKEN = de26d606-709e-4801-a3a7-2771a43ff6f4
DOCKER_USERNAME = your_dockerhub_username
DOCKER_PASSWORD = your_dockerhub_password
```

### **Step 3: Workflows Are Already Created!**

You have 4 workflows in `.github/workflows/`:

#### **1. CI (Continuous Integration)** - `ci.yml`
**Triggers:** Every push, every PR

**What it does:**
- Runs tests
- Checks code quality (Black, Flake8, MyPy)
- Builds Docker image
- Validates DVC pipeline

#### **2. CD (Continuous Deployment)** - `cd.yml`
**Triggers:** After CI succeeds on main branch

**What it does:**
- Builds production Docker image
- Pushes to Docker Hub
- Tags with SHA and 'latest'

#### **3. Weekly Backtest** - `backtest.yml`
**Triggers:** Every Sunday at 00:00 UTC

**What it does:**
- Fetches latest data
- Runs backtest with all parameters
- Logs results to MLflow
- If ROI > 20%, updates params.yaml
- Uploads results as artifacts

#### **4. Daily Scanner** - `scanner.yml`
**Triggers:** Every weekday at 09:00 UTC

**What it does:**
- Fetches stock universe from Finviz
- Runs momentum scanner
- Generates stock picks
- Uploads picks as artifacts
- Creates summary report

### **Step 4: Test Workflows**

```bash
# Push to GitHub
git push origin main

# This triggers:
# 1. CI workflow (tests, linting, Docker build)
# 2. CD workflow (if CI passes)

# View in GitHub:
# Go to Actions tab
# See workflows running
```

### **Step 5: Manual Workflow Triggers**

You can manually trigger workflows:

**Via GitHub UI:**
1. Go to **Actions** tab
2. Select workflow (e.g., "Daily Scanner")
3. Click **Run workflow**
4. Choose branch
5. Click **Run workflow**

**Via GitHub CLI:**
```bash
# Install GitHub CLI
sudo apt install gh

# Login
gh auth login

# Run scanner manually
gh workflow run scanner.yml

# Run backtest manually
gh workflow run backtest.yml
```

---

## 📅 Part 4: Automated Schedule

Once set up, your system runs automatically:

### **Daily (Weekdays at 9 AM UTC)**
```
GitHub Actions → Daily Scanner
  ↓
Fetches 100+ stocks from Finviz
  ↓
Analyzes momentum
  ↓
Generates picks
  ↓
Uploads to GitHub Artifacts
  ↓
(Optional) Sends notification
```

**Access results:**
- Go to Actions → Daily Scanner → Latest run
- Download `daily-picks-XXX` artifact
- Extract and view CSV

### **Weekly (Sundays at Midnight UTC)**
```
GitHub Actions → Weekly Backtest
  ↓
Fetches latest data
  ↓
Tests 9 parameter combinations
  ↓
Logs to MLflow
  ↓
If ROI > 20%: Updates params.yaml
  ↓
Uploads results as artifacts
```

**Access results:**
- Go to Actions → Weekly Backtest → Latest run
- Download `backtest-results-XXX` artifact
- View mlflow.db, trades.csv, curve.png

---

## 🎯 Part 5: Complete Deployment Checklist

### **Local Setup** ✅
- [x] System working locally
- [x] Backtester validated (293% ROI)
- [x] Scanner producing picks
- [x] MLflow tracking experiments

### **DVC Setup**
- [ ] `dvc init` completed
- [ ] Data tracked with `dvc add`
- [ ] Remote storage configured (optional)
- [ ] Pipeline tested with `dvc repro`

### **Docker Setup**
- [ ] Docker image built
- [ ] Tested locally
- [ ] Docker Compose working
- [ ] Pushed to Docker Hub (optional)

### **GitHub Setup**
- [ ] Repository created
- [ ] Code pushed to GitHub
- [ ] Secrets added
- [ ] CI workflow passing
- [ ] CD workflow deploying

### **Automation**
- [ ] Daily scanner running
- [ ] Weekly backtest running
- [ ] Notifications configured (optional)

---

## 🚀 Quick Start Commands

### **DVC**
```bash
# Setup
dvc init
dvc add .cache/ models/
git add .dvc .dvcignore .cache.dvc models.dvc
git commit -m "Setup DVC"

# Run pipeline
dvc repro

# View pipeline
dvc dag
```

### **Docker**
```bash
# Build and run
docker build -t momentum-system:latest .
docker run --rm -e FD_API_KEY=$FD_API_KEY momentum-system:latest

# Or use compose
docker-compose up
```

### **GitHub Actions**
```bash
# Push to trigger
git add .
git commit -m "Update system"
git push origin main

# Manual trigger
gh workflow run scanner.yml
```

---

## 📊 Monitoring Your Automated System

### **Check GitHub Actions**
```
1. Go to your repo
2. Click "Actions" tab
3. See all workflow runs
4. Click on a run to see details
5. Download artifacts
```

### **View Artifacts**
```bash
# Download from GitHub Actions
# Extract picks_YYYYMMDD.csv
# Or view in GitHub UI
```

### **Check Logs**
```bash
# In GitHub Actions
# Click on workflow run
# Click on job
# View detailed logs
```

---

## 🎓 Advanced: Cloud Deployment

### **AWS EC2**
```bash
# SSH into EC2 instance
ssh -i key.pem ubuntu@your-instance

# Clone repo
git clone https://github.com/YOUR_USERNAME/momentum-system
cd momentum-system

# Run with Docker
docker-compose up -d

# View logs
docker-compose logs -f
```

### **Google Cloud Run**
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/momentum-system

# Deploy
gcloud run deploy momentum-system \
  --image gcr.io/PROJECT_ID/momentum-system \
  --platform managed \
  --set-env-vars FD_API_KEY=$FD_API_KEY
```

---

## 🐛 Troubleshooting

### **DVC Issues**
```bash
# Check status
dvc status

# Force re-run
dvc repro --force

# Check remote
dvc remote list
```

### **Docker Issues**
```bash
# Clean rebuild
docker build --no-cache -t momentum-system:latest .

# Check logs
docker logs CONTAINER_ID

# Remove all
docker system prune -a
```

### **GitHub Actions Issues**
```bash
# Check workflow file syntax
cat .github/workflows/scanner.yml

# View logs in GitHub UI
# Actions → Workflow → Run → Job → Step

# Test locally with act
act -j scan
```

---

## 📈 What You Get

### **With DVC:**
- ✅ Version control for data
- ✅ Reproducible pipelines
- ✅ Shareable experiments
- ✅ Remote storage

### **With Docker:**
- ✅ Deploy anywhere
- ✅ Consistent environments
- ✅ Easy scaling
- ✅ Production-ready

### **With GitHub Actions:**
- ✅ Daily stock picks (automatic!)
- ✅ Weekly backtests (automatic!)
- ✅ Automated testing
- ✅ Automated deployment
- ✅ Artifact storage

---

## 🎯 Next Steps

1. **Today:** Setup DVC and Docker locally
2. **This Week:** Push to GitHub, configure secrets
3. **Next Week:** Monitor automated workflows
4. **Month 2:** Deploy to cloud (AWS/GCP)

---

**Your system can now run completely automatically!** 🚀

**Start with:** `dvc init` and `docker build -t momentum-system:latest .`
