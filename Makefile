.PHONY: help install test lint format docker-build docker-run dvc-setup dvc-repro clean

# Default target
help:
	@echo "Quantitative Momentum System - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install dependencies"
	@echo "  make dvc-setup      Setup DVC"
	@echo ""
	@echo "Development:"
	@echo "  make test           Run tests"
	@echo "  make lint           Run linting"
	@echo "  make format         Format code with black"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run backtester in Docker"
	@echo "  make docker-scan    Run scanner in Docker"
	@echo "  make docker-compose Start all services"
	@echo ""
	@echo "DVC:"
	@echo "  make dvc-repro      Run DVC pipeline"
	@echo "  make dvc-dag        Show pipeline DAG"
	@echo "  make dvc-push       Push data to remote"
	@echo "  make dvc-pull       Pull data from remote"
	@echo ""
	@echo "Execution:"
	@echo "  make backtest       Run backtester"
	@echo "  make scan           Run scanner"
	@echo "  make mlflow         Start MLflow UI"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove generated files"
	@echo "  make clean-docker   Remove Docker images"

# Setup
install:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy

dvc-setup:
	./setup_dvc.sh

# Development
test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/

# Docker
docker-build:
	docker build -t momentum-system:latest .

docker-run:
	docker run --rm \
		-e FD_API_KEY=${FD_API_KEY} \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/models:/app/models \
		-v $(PWD)/.cache:/app/.cache \
		momentum-system:latest

docker-scan:
	docker run --rm \
		-e FD_API_KEY=${FD_API_KEY} \
		-e FINVIZ_API_TOKEN=${FINVIZ_API_TOKEN} \
		-v $(PWD)/data:/app/data \
		momentum-system:latest \
		python -m src.scanner

docker-compose:
	docker-compose up

docker-compose-down:
	docker-compose down

# DVC
dvc-repro:
	dvc repro

dvc-dag:
	dvc dag

dvc-push:
	dvc push

dvc-pull:
	dvc pull

# Execution
backtest:
	python -m src.backtester

scan:
	python -m src.scanner

mlflow:
	mlflow ui --port 5000

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache .coverage htmlcov/
	rm -f *.png *.csv

clean-docker:
	docker rmi momentum-system:latest || true
	docker-compose down -v

# CI/CD simulation (run locally)
ci-local:
	make lint
	make test
	make docker-build

# Full pipeline
all: install test docker-build dvc-repro
