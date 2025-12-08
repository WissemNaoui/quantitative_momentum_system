# Docker, DVC, and CI/CD Guide

## 🐳 Docker

### Quick Start

**Build the image:**
```bash
docker build -t momentum-system:latest .
```

**Run backtester:**
```bash
docker run --rm \
  -e FD_API_KEY=$FD_API_KEY \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  momentum-system:latest
```

**Run scanner:**
```bash
docker run --rm \
  -e FD_API_KEY=$FD_API_KEY \
  -e FINVIZ_API_TOKEN=$FINVIZ_API_TOKEN \
  momentum-system:latest \
  python -m src.scanner
```

### Docker Compose

**Start all services:**
```bash
docker-compose up
```

**Run specific service:**
```bash
# Run backtester
docker-compose run --rm backtester

# Run scanner
docker-compose run --rm scanner

# Start MLflow UI
docker-compose up mlflow
```

**View logs:**
```bash
docker-compose logs -f backtester
```

**Stop all services:**
```bash
docker-compose down
```

### Multi-Stage Build Benefits

Our Dockerfile uses multi-stage builds for:
- **Smaller images**: ~200MB vs ~1GB
- **Faster builds**: Cached dependencies
- **Security**: No build tools in production image

---

## 📊 DVC (Data Version Control)

### Setup

**Initialize DVC:**
```bash
pip install dvc
dvc init
```

**Configure remote storage (optional):**
```bash
# S3
dvc remote add -d storage s3://your-bucket/momentum-system
dvc remote modify storage access_key_id $AWS_ACCESS_KEY_ID
dvc remote modify storage secret_access_key $AWS_SECRET_ACCESS_KEY

# Or Google Cloud Storage
dvc remote add -d storage gs://your-bucket/momentum-system

# Or local network storage
dvc remote add -d storage /mnt/shared/momentum-system
```

### Usage

**Run the entire pipeline:**
```bash
dvc repro
```

**Run specific stage:**
```bash
dvc repro backtest
```

**View pipeline DAG:**
```bash
dvc dag
```

**Track changes:**
```bash
# After running pipeline
dvc add data/ models/
git add data.dvc models.dvc dvc.lock
git commit -m "Update data and models"
```

**Push data to remote:**
```bash
dvc push
```

**Pull data from remote:**
```bash
dvc pull
```

### Pipeline Stages

1. **fetch_data**: Download historical data
2. **backtest**: Run strategy validation
3. **scan**: Generate daily stock picks

### Parameters

Edit `params.yaml` to change:
- Stock universe
- Lookback windows
- Holding periods
- Scanner thresholds

Then run:
```bash
dvc repro
```

DVC will automatically re-run only the affected stages.

---

## 🔄 CI/CD (GitHub Actions)

### Workflows

#### 1. **CI - Test and Validate** (`ci.yml`)
**Triggers:** Push to main/develop, Pull requests

**What it does:**
- Runs unit tests
- Code formatting (Black)
- Linting (Flake8)
- Type checking (MyPy)
- Builds Docker image
- Validates DVC pipeline

**Status:** [![CI](https://github.com/YOUR_USERNAME/momentum-system/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/momentum-system/actions)

#### 2. **CD - Deploy** (`cd.yml`)
**Triggers:** After successful CI on main branch

**What it does:**
- Builds production Docker image
- Pushes to Docker Hub
- Tags with SHA and 'latest'

**Required Secrets:**
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

#### 3. **Scheduled Backtest** (`backtest.yml`)
**Triggers:** Every Sunday at 00:00 UTC

**What it does:**
- Runs weekly backtest
- Extracts best parameters
- Updates `params.yaml` if ROI > 20%
- Uploads results as artifacts

**Required Secrets:**
- `FD_API_KEY`

#### 4. **Daily Scanner** (`scanner.yml`)
**Triggers:** Every weekday at 9:00 AM UTC

**What it does:**
- Runs daily stock scanner
- Uploads picks as artifacts
- Creates summary report
- (Optional) Sends notifications

**Required Secrets:**
- `FD_API_KEY`
- `FINVIZ_API_TOKEN` (optional)

### Setup GitHub Secrets

1. Go to your repo → Settings → Secrets and variables → Actions
2. Add these secrets:

```
FD_API_KEY=ff4903af-75da-4215-bac5-5fc43987e6d4
FINVIZ_API_TOKEN=your_token_here
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_password
```

### Manual Triggers

All workflows support manual dispatch:

```bash
# Via GitHub UI: Actions → Select workflow → Run workflow

# Or via GitHub CLI:
gh workflow run ci.yml
gh workflow run backtest.yml
gh workflow run scanner.yml
```

### Viewing Results

**Workflow runs:**
- Go to Actions tab in GitHub
- Click on a workflow run
- View logs, artifacts, and summaries

**Artifacts:**
- Backtest results (30-day retention)
- Daily picks (90-day retention)
- Coverage reports

---

## 🚀 Complete Workflow Example

### Local Development

```bash
# 1. Setup
git clone https://github.com/YOUR_USERNAME/momentum-system
cd momentum-system
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Run tests
pytest tests/

# 4. Run DVC pipeline
dvc repro

# 5. View results
mlflow ui
```

### Docker Development

```bash
# 1. Build
docker-compose build

# 2. Run backtester
docker-compose run --rm backtester

# 3. View MLflow
docker-compose up mlflow
# Open http://localhost:5000
```

### Production Deployment

```bash
# 1. Push to GitHub
git add .
git commit -m "Update strategy"
git push origin main

# 2. CI/CD automatically:
#    - Runs tests
#    - Builds Docker image
#    - Deploys to Docker Hub

# 3. Pull and run anywhere:
docker pull YOUR_USERNAME/momentum-system:latest
docker run -e FD_API_KEY=$FD_API_KEY YOUR_USERNAME/momentum-system:latest
```

---

## 📈 Monitoring and Maintenance

### Daily

- Check scanner workflow results
- Review top picks in artifacts

### Weekly

- Review backtest results
- Check if parameters were auto-updated
- Monitor MLflow metrics

### Monthly

- Review Docker image size
- Clean up old artifacts
- Update dependencies

---

## 🐛 Troubleshooting

### Docker Issues

**Build fails:**
```bash
# Clear cache and rebuild
docker build --no-cache -t momentum-system:latest .
```

**Container can't access API:**
```bash
# Check environment variables
docker run --rm momentum-system:latest env | grep API
```

### DVC Issues

**Pipeline fails:**
```bash
# Check status
dvc status

# Force re-run
dvc repro --force
```

**Remote storage errors:**
```bash
# Test connection
dvc remote list
dvc push --remote storage -v
```

### CI/CD Issues

**Workflow fails:**
- Check Actions tab for error logs
- Verify secrets are set correctly
- Test locally with `act` (GitHub Actions local runner)

**Docker push fails:**
```bash
# Verify Docker Hub credentials
docker login
```

---

## 🎯 Best Practices

### Docker

1. **Use .dockerignore** to exclude unnecessary files
2. **Multi-stage builds** for smaller images
3. **Version tags** for reproducibility
4. **Health checks** for production containers

### DVC

1. **Track large files** (data, models) with DVC
2. **Track code and configs** with Git
3. **Use remote storage** for team collaboration
4. **Run `dvc repro`** instead of manual scripts

### CI/CD

1. **Test before deploy** (CI → CD workflow)
2. **Use secrets** for sensitive data
3. **Cache dependencies** for faster builds
4. **Artifact retention** based on importance

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [DVC Documentation](https://dvc.org/doc)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)

---

**Next Steps:**
1. Set up GitHub secrets
2. Push to GitHub to trigger CI/CD
3. Monitor first workflow run
4. Review and iterate
