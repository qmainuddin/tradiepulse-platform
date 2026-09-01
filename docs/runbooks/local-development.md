# Local Development Runbook

## Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- Java 21 & Maven (or run via container)
- Task (optional, or standard `make`)

## 1. Environment Setup
Copy the example environment file and adjust if necessary:
```bash
cp infra/env/.env.example .env
```

## 2. Start Full Stack Locally
To build and start all containers in local development mode:
```bash
# Using Taskfile
task up

# Or using Makefile
make up

# Or directly with Docker Compose
docker compose -f docker-compose.dev.yml up --build -d
```

## 3. Service Access Points
- **Web App / Host Shell:** [http://localhost:3000](http://localhost:3000)
- **API Gateway:** [http://localhost:8080](http://localhost:8080)
- **Auth Service:** [http://localhost:8081](http://localhost:8081)
- **Config Service:** [http://localhost:8888](http://localhost:8888)
- **AI Agent API:** [http://localhost:8000](http://localhost:8000)
- **RabbitMQ Management UI:** [http://localhost:15672](http://localhost:15672) (User: `guest`, Password: `guest`)
- **Qdrant Vector Dashboard:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
- **PostgreSQL / PostGIS:** `localhost:5432` (DB: `tradiepulse`, User: `postgres`, Password: `postgres_secure_password`)

## 4. Running Tests
```bash
# Run all test suites
task test:all
# Or
make test-all

# Run individual service tests
task test:agent
task test:auth
task test:gateway
task test:frontend
task db:test
```

## 5. Submodule Management
```bash
# Sync submodules
task submodules:sync

# Ensure not in detached HEAD state
task submodules:checkout
```
