# GUI-Actor FastAPI Makefile
# Usage: make <target>

# Variables
PYTHON := python3
PIP := pip3
APP_NAME := gui-actor-api
DOCKER_IMAGE := $(APP_NAME)
DOCKER_TAG := latest
PORT := 8080
HOST := 0.0.0.0

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help install install-dev run run-dev test clean docker-build docker-run docker-stop docker-logs docker-clean docker-push docker-compose-up docker-compose-down docker-compose-logs health-check lint format check-deps setup-env

# Default target
help: ## Show this help message
	@echo "$(BLUE)GUI-Actor FastAPI - Available Commands:$(NC)"
	@echo ""
	@echo "$(GREEN)Development Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# Development Commands
install: ## Install production dependencies
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio httpx black flake8 mypy

setup-env: ## Set up development environment
	@echo "$(GREEN)Setting up development environment...$(NC)"
	$(PYTHON) -m venv venv
	@echo "$(YELLOW)Virtual environment created. Activate it with:$(NC)"
	@echo "$(BLUE)  source venv/bin/activate  # On Unix/macOS$(NC)"
	@echo "$(BLUE)  venv\\Scripts\\activate     # On Windows$(NC)"

check-deps: ## Check if all dependencies are installed
	@echo "$(GREEN)Checking dependencies...$(NC)"
	@$(PYTHON) -c "import torch, transformers, fastapi, uvicorn, PIL, numpy, matplotlib; print('$(GREEN)✓ All dependencies installed$(NC)')" || echo "$(RED)✗ Missing dependencies. Run 'make install'$(NC)"

run: ## Run the FastAPI server (production mode)
	@echo "$(GREEN)Starting GUI-Actor FastAPI server...$(NC)"
	$(PYTHON) main.py

run-dev: ## Run the FastAPI server (development mode with auto-reload)
	@echo "$(GREEN)Starting GUI-Actor FastAPI server in development mode...$(NC)"
	$(PYTHON) start_server.py --reload --log-level debug

run-custom: ## Run with custom host and port
	@echo "$(GREEN)Starting server with custom settings...$(NC)"
	@read -p "Enter host (default: $(HOST)): " host; \
	read -p "Enter port (default: $(PORT)): " port; \
	$(PYTHON) start_server.py --host $${host:-$(HOST)} --port $${port:-$(PORT)}

# Testing Commands
test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	pytest tests/ -v

test-client: ## Test the API client
	@echo "$(GREEN)Testing API client...$(NC)"
	$(PYTHON) test_client.py

health-check: ## Check API health
	@echo "$(GREEN)Checking API health...$(NC)"
	@curl -f http://localhost:$(PORT)/health || echo "$(RED)API is not responding$(NC)"

# Code Quality Commands
lint: ## Run linting checks
	@echo "$(GREEN)Running linting checks...$(NC)"
	flake8 main.py test_client.py start_server.py --max-line-length=88 --ignore=E203,W503

format: ## Format code with black
	@echo "$(GREEN)Formatting code...$(NC)"
	black main.py test_client.py start_server.py --line-length=88

format-check: ## Check code formatting
	@echo "$(GREEN)Checking code formatting...$(NC)"
	black --check main.py test_client.py start_server.py --line-length=88

type-check: ## Run type checking
	@echo "$(GREEN)Running type checks...$(NC)"
	mypy main.py test_client.py start_server.py --ignore-missing-imports

# Docker Commands
docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Run Docker container
	@echo "$(GREEN)Running Docker container...$(NC)"
	docker run -d --name $(APP_NAME) -p $(PORT):$(PORT) $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-stop: ## Stop Docker container
	@echo "$(GREEN)Stopping Docker container...$(NC)"
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true

docker-logs: ## Show Docker container logs
	@echo "$(GREEN)Showing Docker logs...$(NC)"
	docker logs -f $(APP_NAME)

docker-clean: ## Clean up Docker resources
	@echo "$(GREEN)Cleaning up Docker resources...$(NC)"
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) || true

docker-push: ## Push Docker image to registry
	@echo "$(GREEN)Pushing Docker image...$(NC)"
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)

# Docker Compose Commands
docker-compose-up: ## Start services with Docker Compose
	@echo "$(GREEN)Starting services with Docker Compose...$(NC)"
	docker-compose up -d

docker-compose-down: ## Stop services with Docker Compose
	@echo "$(GREEN)Stopping services with Docker Compose...$(NC)"
	docker-compose down

docker-compose-logs: ## Show Docker Compose logs
	@echo "$(GREEN)Showing Docker Compose logs...$(NC)"
	docker-compose logs -f

docker-compose-build: ## Build and start with Docker Compose
	@echo "$(GREEN)Building and starting with Docker Compose...$(NC)"
	docker-compose up --build -d

docker-compose-production: ## Start production stack with nginx
	@echo "$(GREEN)Starting production stack...$(NC)"
	docker-compose --profile production up -d

# Utility Commands
clean: ## Clean up Python cache and temporary files
	@echo "$(GREEN)Cleaning up...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache

logs: ## Show application logs (if using systemd)
	@echo "$(GREEN)Showing application logs...$(NC)"
	journalctl -u $(APP_NAME) -f || echo "$(YELLOW)No systemd service found. Use 'make docker-logs' for Docker logs$(NC)"

status: ## Show status of all services
	@echo "$(GREEN)Service Status:$(NC)"
	@echo "$(BLUE)Local Python process:$(NC)"
	@pgrep -f "python.*main.py" && echo "$(GREEN)✓ Running$(NC)" || echo "$(RED)✗ Not running$(NC)"
	@echo "$(BLUE)Docker container:$(NC)"
	@docker ps | grep $(APP_NAME) && echo "$(GREEN)✓ Running$(NC)" || echo "$(RED)✗ Not running$(NC)"
	@echo "$(BLUE)Docker Compose services:$(NC)"
	@docker-compose ps | grep -v "Name" && echo "$(GREEN)✓ Running$(NC)" || echo "$(RED)✗ Not running$(NC)"

restart: ## Restart the application
	@echo "$(GREEN)Restarting application...$(NC)"
	@make stop || true
	@make run

stop: ## Stop the application
	@echo "$(GREEN)Stopping application...$(NC)"
	@pkill -f "python.*main.py" || true
	@pkill -f "uvicorn.*main:app" || true

# Development Workflow
dev-setup: setup-env install-dev ## Complete development setup
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "$(BLUE)1. Activate virtual environment$(NC)"
	@echo "$(BLUE)2. Run 'make run-dev' to start development server$(NC)"

dev: run-dev ## Start development server (alias for run-dev)

prod: check-deps run ## Start production server

# Quick Commands
up: docker-compose-up ## Quick start with Docker Compose
down: docker-compose-down ## Quick stop with Docker Compose
build: docker-build ## Quick Docker build
logs: docker-compose-logs ## Quick Docker Compose logs

# Documentation
docs: ## Generate API documentation
	@echo "$(GREEN)API documentation available at:$(NC)"
	@echo "$(BLUE)http://localhost:$(PORT)/docs$(NC)"
	@echo "$(BLUE)http://localhost:$(PORT)/redoc$(NC)"

# Monitoring
monitor: ## Monitor application resources
	@echo "$(GREEN)Monitoring application...$(NC)"
	@echo "$(BLUE)CPU and Memory:$(NC)"
	@ps aux | grep -E "(python.*main|uvicorn)" | grep -v grep || echo "$(YELLOW)No Python processes found$(NC)"
	@echo "$(BLUE)Docker containers:$(NC)"
	@docker stats --no-stream $(APP_NAME) 2>/dev/null || echo "$(YELLOW)No Docker containers found$(NC)"

# Backup and Restore
backup: ## Create backup of configuration
	@echo "$(GREEN)Creating backup...$(NC)"
	@mkdir -p backups
	@tar -czf backups/backup-$$(date +%Y%m%d-%H%M%S).tar.gz *.py *.yml *.conf requirements.txt README.md

# Installation helpers
install-gui-actor: ## Install GUI-Actor dependencies
	@echo "$(GREEN)Installing GUI-Actor...$(NC)"
	@if [ ! -d "GUI-Actor" ]; then \
		git clone https://github.com/microsoft/GUI-Actor.git; \
	fi
	@cd GUI-Actor && $(PIP) install -e .

# Show current configuration
config: ## Show current configuration
	@echo "$(GREEN)Current Configuration:$(NC)"
	@echo "$(BLUE)Python:$(NC) $(shell which $(PYTHON))"
	@echo "$(BLUE)Pip:$(NC) $(shell which $(PIP))"
	@echo "$(BLUE)Port:$(NC) $(PORT)"
	@echo "$(BLUE)Host:$(NC) $(HOST)"
	@echo "$(BLUE)Docker Image:$(NC) $(DOCKER_IMAGE):$(DOCKER_TAG)"
	@echo "$(BLUE)App Name:$(NC) $(APP_NAME)" 