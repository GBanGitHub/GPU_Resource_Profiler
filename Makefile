.PHONY: help setup install clean run-info run-profile run-dashboard run-api test lint format

# Default Python and venv paths
PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

# Colors for terminal output
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "GPU Resource Profiler - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start:"
	@echo "  make setup    # Create venv and install dependencies"
	@echo "  make run-info # Check GPU status"

# ============================================================================
# Setup and Installation
# ============================================================================

setup: $(VENV)/bin/activate ## Create virtual environment and install package
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo ""
	@echo "To activate the virtual environment, run:"
	@echo "  source $(VENV)/bin/activate"
	@echo ""
	@echo "Then you can use:"
	@echo "  gpu-profiler info"
	@echo "  gpu-profiler profile --duration 60"
	@echo "  gpu-profiler dashboard"
	@echo "  gpu-profiler api"

$(VENV)/bin/activate: requirements.txt setup.py
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e .
	@touch $(VENV)/bin/activate

install: setup ## Alias for setup

clean: ## Remove virtual environment and cached files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	rm -rf $(VENV)
	rm -rf *.egg-info
	rm -rf build dist
	rm -rf __pycache__ src/__pycache__ src/utils/__pycache__ src/api/__pycache__
	rm -rf .pytest_cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "$(GREEN)Clean complete!$(NC)"

# ============================================================================
# Running the Application
# ============================================================================

run-info: setup ## Display current GPU information
	$(BIN)/gpu-profiler info

run-profile: setup ## Start profiling (use DURATION=60 to set duration in seconds)
	$(BIN)/gpu-profiler profile $(if $(DURATION),--duration $(DURATION),)

run-dashboard: setup ## Launch the web dashboard (default: http://localhost:8050)
	@echo "$(GREEN)Starting dashboard at http://localhost:8050$(NC)"
	$(BIN)/gpu-profiler dashboard

run-api: setup ## Start the REST API server (default: http://localhost:8000)
	@echo "$(GREEN)Starting API at http://localhost:8000$(NC)"
	@echo "$(GREEN)API docs at http://localhost:8000/docs$(NC)"
	$(BIN)/gpu-profiler api

run-all: setup ## Start both API and Dashboard (in background)
	@echo "$(GREEN)Starting API server in background...$(NC)"
	$(BIN)/gpu-profiler api &
	@sleep 2
	@echo "$(GREEN)Starting Dashboard...$(NC)"
	$(BIN)/gpu-profiler dashboard

# ============================================================================
# Profile Management
# ============================================================================

list-profiles: setup ## List all saved profile files
	$(BIN)/gpu-profiler list-profiles

analyze: setup ## Analyze a profile (use FILE=path/to/profile.json)
ifndef FILE
	@echo "$(YELLOW)Usage: make analyze FILE=profiles/profile_xxx.json$(NC)"
	@echo ""
	@echo "Available profiles:"
	@ls -la profiles/*.json 2>/dev/null || echo "  No profiles found"
else
	$(BIN)/gpu-profiler analyze $(FILE)
endif

# ============================================================================
# Development
# ============================================================================

test: setup ## Run tests
	$(BIN)/python -m pytest tests/ -v

lint: setup ## Run linting (requires flake8)
	$(BIN)/pip install flake8 --quiet
	$(BIN)/flake8 src/ --max-line-length=100 --ignore=E501,W503

format: setup ## Format code (requires black)
	$(BIN)/pip install black --quiet
	$(BIN)/black src/ --line-length=100

# ============================================================================
# Docker
# ============================================================================

docker-build: ## Build Docker image
	docker build -t gpu-profiler .

docker-run: ## Run Docker container with GPU support
	docker run --gpus all -p 8000:8000 gpu-profiler

docker-compose-up: ## Start with Docker Compose
	docker-compose up

docker-compose-down: ## Stop Docker Compose
	docker-compose down
