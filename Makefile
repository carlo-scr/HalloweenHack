.PHONY: help install setup start start-backend start-frontend stop clean test health

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project directories
BACKEND_DIR := browser-use copy
FRONTEND_DIR := webpage
VENV := $(BACKEND_DIR)/.venv

help: ## Show this help message
	@echo "$(BLUE)HalloweenHack Project - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Install all dependencies (backend + frontend)
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@echo "$(YELLOW)→ Setting up Python backend...$(NC)"
	cd "$(BACKEND_DIR)" && \
		(test -d .venv || python3 -m venv .venv) && \
		. .venv/bin/activate && \
		pip install -q fastapi "uvicorn[standard]" && \
		pip install -q -e .
	@echo "$(YELLOW)→ Installing Node.js frontend...$(NC)"
	cd "$(FRONTEND_DIR)" && npm install
	@echo "$(GREEN)✓ All dependencies installed!$(NC)"

setup: install ## Complete first-time setup
	@echo "$(BLUE)Running setup...$(NC)"
	@./setup-backend.sh
	@echo "$(GREEN)✓ Setup complete!$(NC)"

start: ## Start both backend and frontend
	@echo "$(BLUE)Starting HalloweenHack Project...$(NC)"
	@echo ""
	@$(MAKE) start-backend &
	@sleep 3
	@$(MAKE) start-frontend &
	@echo ""
	@echo "$(GREEN)✓ Project started!$(NC)"
	@echo ""
	@echo "  $(BLUE)🌐 React App:    http://localhost:8080$(NC)"
	@echo "  $(BLUE)🔌 API Server:   http://localhost:8000$(NC)"
	@echo "  $(BLUE)📚 API Docs:     http://localhost:8000/docs$(NC)"
	@echo ""
	@echo "Press Ctrl+C to stop"
	@wait

start-backend: ## Start only the backend server
	@echo "$(YELLOW)→ Starting Browser-Use Backend...$(NC)"
	@cd "$(BACKEND_DIR)" && \
		. .venv/bin/activate && \
		python browser_api_server.py

start-frontend: ## Start only the frontend dev server
	@echo "$(YELLOW)→ Starting React Frontend...$(NC)"
	@cd "$(FRONTEND_DIR)" && npm run dev

stop: ## Stop all running servers
	@echo "$(YELLOW)Stopping servers...$(NC)"
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:8080 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:5173 | xargs kill -9 2>/dev/null || true
	@echo "$(GREEN)✓ Servers stopped$(NC)"

clean: stop ## Clean temporary files and caches
	@echo "$(YELLOW)Cleaning project...$(NC)"
	@rm -rf "$(FRONTEND_DIR)/node_modules/.vite"
	@rm -rf "$(FRONTEND_DIR)/.vite"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(NC)"

health: ## Check if backend is healthy
	@echo "$(YELLOW)Checking backend health...$(NC)"
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "$(RED)✗ Backend not responding$(NC)"

test: ## Run a test browser automation task
	@echo "$(YELLOW)Testing browser automation...$(NC)"
	@curl -s -X POST http://localhost:8000/api/run-task \
		-H "Content-Type: application/json" \
		-d '{"task": "Go to example.com", "max_steps": 3, "headless": true}' | \
		python3 -m json.tool

dev: start ## Alias for 'make start'

# Default target
.DEFAULT_GOAL := help
