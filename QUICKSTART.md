# Quick Reference Card

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd quantitative_momentum_system
make install

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Run
make backtest
```

## 📋 Common Commands

### Local Development
```bash
make test          # Run tests
make backtest      # Run backtester
make scan          # Run scanner
make mlflow        # Start MLflow UI
```

### Docker
```bash
make docker-build       # Build image
make docker-run         # Run backtester
make docker-scan        # Run scanner
make docker-compose     # Start all services
```

### DVC
```bash
make dvc-repro     # Run pipeline
make dvc-dag       # View pipeline
make dvc-push      # Push to remote
make dvc-pull      # Pull from remote
```

## 🔑 Environment Variables

```bash
export FD_API_KEY="your_key"
export FINVIZ_API_TOKEN="your_token"
```

## 📊 Workflows

### Daily Routine
```bash
make scan          # Get today's picks
```

### Weekly Routine
```bash
make backtest      # Validate strategy
make mlflow        # Review results
```

### Before Deployment
```bash
make test          # Run tests
make lint          # Check code quality
make docker-build  # Build image
```

## 🐛 Troubleshooting

### Tests failing
```bash
pytest tests/ -v  # Verbose output
```

### Docker issues
```bash
make clean-docker  # Clean and rebuild
make docker-build
```

### DVC issues
```bash
dvc status         # Check status
dvc repro --force  # Force re-run
```

## 📚 Documentation

- `README.md` - Project overview
- `WORKFLOW.md` - Daily usage guide
- `DEVOPS_GUIDE.md` - Docker, DVC, CI/CD
- `FD_API_GUIDE.md` - API integration

## 🔗 Quick Links

- MLflow UI: http://localhost:5000
- GitHub Actions: `.github/workflows/`
- Docker Hub: `YOUR_USERNAME/momentum-system`
