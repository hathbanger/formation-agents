SHELL := /bin/bash

PYTHON := python
PIP := pip
DOCKER_COMPOSE := docker-compose
DOCKER_REGISTRY := registry.digitalocean.com/your-registry  # Update this with your DO registry

ENV_FILE := .env
DEPLOY_ENV_FILE := deploy.env  # For deployment-specific variables

.PHONY: help install lint format test build up down logs run-cli run-api run-telegram run-all clean agent deploy-agent

help:
	@echo "OSS BOSS Makefile commands:"
	@echo "  make install      Install Python dependencies"
	@echo "  make lint         Run linters (flake8, isort)"
	@echo "  make format       Format code (black, isort)"
	@echo "  make test         Run tests"
	@echo "  make build        Build Docker images"
	@echo "  make up           Start services in background"
	@echo "  make down         Stop services and remove containers"
	@echo "  make logs         Follow Docker Compose logs"
	@echo "  make run-cli      Run CLI interface"
	@echo "  make run-api      Run API server"
	@echo "  make run-telegram Run Telegram bot"
	@echo "  make run-all      Run all interfaces locally"
	@echo "  make clean        Remove Python cache files"
	@echo "  make agent SCRIPT=script-name  Run a specific agent script in Docker"
	@echo "  make deploy-agent SCRIPT=script-name  Deploy agent to Digital Ocean"

install:
	$(PIP) install -r requirements.txt

lint:
	flake8 .
	isort --check-only .

format:
	black .
	isort .

test:
	pytest

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

run-cli:
	$(PYTHON) main.py --cli

run-api:
	$(PYTHON) main.py --api

run-telegram:
	$(PYTHON) main.py --telegram

run-all:
	$(PYTHON) main.py --all

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

agent:
ifndef SCRIPT
	$(error SCRIPT is undefined. Usage: make agent SCRIPT=script-name)
endif
	docker build -t ossboss-agent \
		--build-arg AGENT_SCRIPT_NAME=$(SCRIPT).py \
		.
	docker run --rm -it \
		--env-file $(ENV_FILE) \
		--name ossboss-$(SCRIPT) \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		-v $(PWD)/tmp:/app/tmp \
		-v $(PWD)/reports:/app/reports \
		-p 8000:8000 \
		ossboss-agent

deploy-agent:
ifndef SCRIPT
	$(error SCRIPT is undefined. Usage: make deploy-agent SCRIPT=script-name)
endif
	@if [ ! -f $(DEPLOY_ENV_FILE) ]; then \
		echo "$(DEPLOY_ENV_FILE) not found. Create it with your Digital Ocean credentials."; \
		exit 1; \
	fi
	# Build the image with deployment settings
	docker build -t $(DOCKER_REGISTRY)/$(SCRIPT):latest \
		--build-arg AGENT_SCRIPT_NAME=$(SCRIPT).py \
		--build-arg DO_DEPLOYMENT=true \
		.
	# Push to Digital Ocean registry
	docker push $(DOCKER_REGISTRY)/$(SCRIPT):latest
	# Apply deployment if doctl is installed
	@if command -v doctl >/dev/null 2>&1; then \
		echo "Deploying to Digital Ocean..."; \
		doctl apps create --spec deployment-specs/$(SCRIPT).yaml || \
		doctl apps update --spec deployment-specs/$(SCRIPT).yaml; \
	else \
		echo "doctl not found. Please install Digital Ocean CLI tools."; \
		exit 1; \
	fi
