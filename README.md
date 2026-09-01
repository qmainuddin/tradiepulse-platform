# TradiePulse Platform

> **Target:** [tradiepulse.mainuddintalukdar.cloud](https://tradiepulse.mainuddintalukdar.cloud/)  
> **Region:** Christchurch & New Zealand  
> **Architecture:** Event-Driven Microservices + Micro-Frontend + Deterministic LangGraph Agent Core

TradiePulse is an enterprise-grade AI marketplace connecting New Zealanders with qualified, nearby tradespeople (plumbers, electricians, and mechanics). The platform demonstrates frugal, resilient AI architecture governed by strict prompt caching, typed schema gates, deterministic state machines, and a clean microservice topology.

---

## 🏛️ Platform Architecture

```
tradiepulse-platform/
├── AGENTS.md / CLAUDE.md / .aiignore   # Part 0: Agent Operating Rules & Non-negotiable Laws
├── .gitmodules                         # Git submodules manifest
├── docker-compose.yml                  # Production stack (GHCR image tags)
├── docker-compose.dev.yml              # Local development stack
├── Taskfile.yml / Makefile             # Cross-repo developer task runner
├── infra/
│   ├── caddy/Caddyfile                 # Auto-TLS reverse proxy for tradiepulse.mainuddintalukdar.cloud
│   └── env/.env.example                # Full environment variable and secret matrix
├── docs/                               # Architecture blueprints, ADRs, compliance guides
└── services/
    ├── db/                             # PostgreSQL 16 + PostGIS spatial migrations & functions
    ├── frontend/                       # Next.js 14 Shell + React/TS Module Federation remotes
    ├── api-gateway/                    # Spring Cloud Gateway (Java 21 reactive, JWT edge, Redis rate limit)
    ├── auth-service/                   # Spring Boot 3 Auth & Identity (Argon2id, OAuth2, 48h verify, step-up)
    ├── config-service/                 # Spring Cloud Config Server (native/git profiles, encrypted secrets)
    └── ai-agent/                       # Python 3.12 + FastAPI + LangGraph + Redis Cache + Qdrant RAG
```

---

## 🚀 Quick Start (Local Development)

### 1. Configure Environment
```bash
cp infra/env/.env.example .env
```

### 2. Launch Development Stack
```bash
# Start all containers in background
task up
# Or
make up
```

### 3. Run Automated Test Suites
```bash
task test:all
# Or
make test-all
```

---

## 🔒 Security & Compliance
- **Authentication & RBAC:** Short-lived JWTs (15 min), rotating refresh tokens with family reuse revocation, 4 roles (`super_admin`, `admin`, `customer`, `tradesperson`).
- **Step-Up Impersonation:** Admin impersonation requires answering security questions, issues short-lived `act_as` tokens, and generates immutable audit trails.
- **NZ Verification Seams:** Pluggable `VerificationProvider` for EWRB (electricians), PGDB (plumbers), IRD mod-11 checksums, and Christchurch regional building standards.
- **Privacy & Redaction:** Automated PII masking before dispatching prompts to LLM providers.

---

## 📜 Agent Constitution & TDD
All development across every repository is bound by the laws in [AGENTS.md](AGENTS.md).
- **Strict TDD:** RED → GREEN → REFACTOR.
- **Coverage Gates:** $\ge 85\%$ line and $\ge 80\%$ branch coverage; $100\%$ on critical auth & matching paths.
- **Token Discipline:** Aggressive prompt caching, Redis semantic cache, bounded conversation history, and hard request token ceilings.
