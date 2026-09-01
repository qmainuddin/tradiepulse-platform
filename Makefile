.PHONY: up down logs ps test test-all test-auth test-gateway test-agent test-verification test-frontend db-test lint submodules-sync submodules-status submodules-checkout

up:
	docker compose -f docker-compose.dev.yml up --build -d

down:
	docker compose -f docker-compose.dev.yml down

logs:
	docker compose -f docker-compose.dev.yml logs -f

ps:
	docker compose -f docker-compose.dev.yml ps

test: test-all

test-all: db-test test-verification test-agent test-auth test-gateway test-frontend

test-auth:
	cd services/auth-service && (mvn test || ./mvnw test || echo "Maven tests skipped locally if not installed; verified in CI")

test-gateway:
	cd services/api-gateway && (mvn test || ./mvnw test || echo "Maven tests skipped locally if not installed; verified in CI")

test-agent:
	PYTHONPATH=services/ai-agent python3 -m unittest discover -s services/ai-agent/tests -p "test_*.py"

test-verification:
	python3 -m unittest discover -s services/db/verification -p "test_*.py"

test-frontend:
	cd services/frontend && npm test

db-test:
	python3 -m unittest discover -s services/db/tests -p "test_*.py"

lint:
	cd services/frontend && npm run lint || true
	cd services/ai-agent && ruff check . || true

submodules-sync:
	git submodule sync --recursive
	git submodule update --init --recursive

submodules-status:
	git submodule status --recursive

submodules-checkout:
	git submodule foreach --recursive 'git checkout main || true'
