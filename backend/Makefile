.PHONY: help db-up db-down db-logs db-shell db-reset backend-up backend-down up down logs migrate migrate-create migrate-upgrade migrate-downgrade migrate-current migrate-history

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

# Alembic migration commands
migrate: ## Show current migration status
	alembic current

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="description")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "Error: MESSAGE is required. Usage: make migrate-create MESSAGE='your message'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MESSAGE)"

migrate-upgrade: ## Apply all pending migrations
	alembic upgrade head

migrate-downgrade: ## Downgrade one migration (usage: make migrate-downgrade REVISION="-1")
	@if [ -z "$(REVISION)" ]; then \
		echo "Error: REVISION is required. Usage: make migrate-downgrade REVISION='-1' or REVISION='revision_id'"; \
		exit 1; \
	fi
	alembic downgrade $(REVISION)

migrate-current: ## Show current migration version
	alembic current

migrate-history: ## Show migration history
	alembic history

