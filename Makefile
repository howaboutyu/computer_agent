# GUI-Actor FastAPI - Simple Makefile
# Usage: make <target>

PYTHON := python3
PIP := pip3
PORT := 8080

.PHONY: help install run dev test clean docker-up docker-down

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies
	$(PIP) install -r requirements.txt

run: ## Run production server
	$(PYTHON) main.py

dev: ## Run development server (with auto-reload)
	$(PYTHON) start_server.py --reload

test: ## Test the API
	$(PYTHON) test_client.py

health: ## Check API health
	@curl -f http://localhost:$(PORT)/health || echo "API not responding"

clean: ## Clean Python cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache

# Docker commands
docker-up: ## Start with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker Compose
	docker-compose down

docker-build: ## Build Docker image
	docker build -t gui-actor-api .

# Quick aliases
up: docker-up
down: docker-down 