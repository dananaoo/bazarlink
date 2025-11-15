.PHONY: help db-up db-down db-logs db-shell db-reset backend-up backend-down up down logs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

db-up: ## Start PostgreSQL database only
	docker-compose up db -d

db-down: ## Stop PostgreSQL database
	docker-compose stop db

db-logs: ## View database logs
	docker-compose logs -f db

db-shell: ## Access PostgreSQL shell
	docker exec -it scp_postgres psql -U postgres -d scp_db

db-reset: ## Reset database (WARNING: deletes all data)
	docker-compose down -v
	docker-compose up db -d

backend-up: ## Start backend (requires database running)
	uvicorn app.main:app --reload

up: ## Start everything (database + backend in Docker)
	docker-compose up -d

down: ## Stop everything
	docker-compose down

logs: ## View all logs
	docker-compose logs -f

