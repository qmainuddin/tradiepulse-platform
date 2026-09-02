# TradiePulse Platform

> **Live Production Target:** [https://tradiepulse.mainuddintalukdar.cloud/](https://tradiepulse.mainuddintalukdar.cloud/)  
> **Region:** Christchurch & Greater Canterbury, New Zealand  
> **Architecture:** Event-Driven Microservices · Micro-Frontend · Deterministic LangGraph Agent Core · Zero-Touch GitOps

TradiePulse is an enterprise-grade, agentic AI trades matching marketplace built for Christchurch and New Zealand. It connects homeowners and businesses with licensed, local tradespeople (plumbers, electricians, and mechanics) in seconds through natural language conversation.

The platform demonstrates **frugal, resilient, agent-ready AI architecture** governed by strict prompt caching, typed schema gates, deterministic state machines, and a clean microservice topology.

---

## 🏛️ System Architecture

```
                                  [ https://tradiepulse.mainuddintalukdar.cloud ]
                                                        │
                                          ┌─────────────▼─────────────┐
                                          │     Hostinger VPS Caddy   │
                                          │   (Docker network: stack) │
                                          └─────────────┬─────────────┘
                                                        │
                         ┌──────────────────────────────┴──────────────────────────────┐
                         │ /                                                           │ /api/*, /auth/*, /chat/*
            ┌────────────▼────────────┐                                   ┌────────────▼────────────┐
            │      Frontend Shell     │                                   │    API Gateway (Edge)   │
            │   Next.js 14 (Node 22)  │                                   │ Spring Cloud Gateway 4  │
            │       [Port 3000]       │                                   │       [Port 8080]       │
            └─────────────────────────┘                                   └────────────┬────────────┘
                                                                                       │
                         ┌─────────────────────────────────────────────────────────────┼────────────────────────────┐
                         │                                                             │                            │
            ┌────────────▼────────────┐                                   ┌────────────▼────────────┐  ┌────────────▼────────────┐
            │   Auth & Identity Svc   │                                   │     AI Agent Service    │  │      Config Server      │
            │  Spring Boot 3 (Java 21)│                                   │   FastAPI (Python 3.12) │  │  Spring Cloud Config    │
            │       [Port 8081]       │                                   │       [Port 8000]       │  │       [Port 8888]       │
            └────────────┬────────────┘                                   └────────────┬────────────┘  └─────────────────────────┘
                         │                                                             │
                         └──────────────────────────────┬──────────────────────────────┘
                                                        │
                                          ┌─────────────▼─────────────┐
                                          │   PostgreSQL 16 + PostGIS │
                                          │       [Port 5432]         │
                                          └───────────────────────────┘
                                                        │
                         ┌──────────────────────────────┼──────────────────────────────┐
                         │                              │                              │
            ┌────────────▼────────────┐   ┌─────────────▼─────────────┐  ┌─────────────▼─────────────┐
            │        Redis 7.4        │   │       RabbitMQ 3.13       │  │        Qdrant 1.11        │
            │   (Semantic/L2 Cache)   │   │     (Async Event Broker)  │  │      (Interaction RAG)    │
            │       [Port 6379]       │   │     [Ports 5672/15672]    │  │     [Ports 6333/6334]     │
            └─────────────────────────┘   └───────────────────────────┘  └───────────────────────────┘
```

---

## 📦 Service Topology & Tech Stack

| Service | Technology | Port | Purpose |
|---|---|---|---|
| **`frontend-shell`** | Next.js 14 App Router, React 18, Node.js 22 LTS, TailwindCSS, Zustand | `3000` | Host shell with Customer Portal, Tradie Portal, Admin Console, and Chat Widget |
| **`api-gateway`** | Spring Cloud Gateway, Java 21, Netty Reactive, Redis Rate Limiter | `8080` | Edge security, JWT verification, header sanitization, trace propagation, CORS |
| **`auth-service`** | Spring Boot 3.3, Java 21, Spring Security, Argon2id, Nimbus/JJWT | `8081` | Authentication, rotating refresh token families, 48h activation, Step-Up Impersonation |
| **`config-service`**| Spring Cloud Config Server, Java 21 | `8888` | Centralized external configuration profiles with symmetric `{cipher}` secret decryption |
| **`ai-agent`** | Python 3.12, FastAPI, LangGraph, Pydantic v2, OpenRouter, Groq | `8000` | Deterministic state machine, typed schema gates, semantic caching, PII redaction |
| **`postgres`** | PostgreSQL 16 + PostGIS 3.4 Alpine | `5432` | Spatial matching engine (`catalog.nearest_available_qualified`), schemas & migrations |
| **`redis`** | Redis 7.4 Alpine | `6379` | Token blacklist, session cache, L2 cache, LLM semantic response cache |
| **`rabbitmq`** | RabbitMQ 3.13 Alpine + Management Plugin | `5672` / `15672` | Asynchronous session completion publishing and background RAG event worker |
| **`qdrant`** | Qdrant Vector Search Engine v1.11.2 | `6333` / `6334` | Interaction logging and embeddings RAG store |

---

## 🗄️ Database Schemas & Migrations

All versioned migrations live in [`services/db/migrations/V1__init_schemas.sql` through `V8__spatial_matching_function.sql`](services/db/migrations/):

- **`identity`**: `users`, `security_questions`, `activation_tokens`, `refresh_token_families`.
- **`catalog`**: `tradie_profiles` (with `GEOGRAPHY(Point,4326)` locations), `availability_slots`, and `catalog.nearest_available_qualified()` stored function.
- **`jobs`**: `jobs`, `job_events`, `ratings`.
- **`verification`**: `verification_cases`, `verification_documents`.
- **`audit`**: `audit_log` (tamper-evident audit trail), `chat_sessions`, `chat_messages`.

---

## 🔒 Security, Compliance & Governance

1. **Deterministic Agent Guardrails & Token Discipline (Part 0 Rules)**
   - **Typed Schema Gates (`Pydantic v2`)**: Every LLM output is parsed against strict Pydantic models with a bounded 1-step schema repair before fallback.
   - **Semantic Cache (`Redis`)**: Normalized query embeddings bypass remote LLM calls on repeated intents (0 token burn).
   - **Prompt Caching**: System instructions and schema definitions are strictly separated into stable prefixes for provider-level caching.
   - **PII Redaction**: Automatically sanitizes New Zealand phone numbers (landlines and mobiles), IRD numbers, emails, and credit cards before dispatching to LLMs.
2. **New Zealand Regulatory & Licensing Verification**
   - **`MockIRDProvider`**: Official NZ Inland Revenue **Modulus-11 Checksum** algorithm supporting 8-digit and 9-digit IRD numbers.
   - **`EWRBLicenseProvider`**: Electricians register lookup seam against the Electrical Workers Registration Board.
   - **`PGDBLicenseProvider`**: Plumbers, gasfitters, and drainlayers verification seam against the PGDB board.
   - **`ChristchurchRegionalComplianceProvider`**: Verifies Canterbury regional building standards and minimum \$2M NZ Public Liability Insurance.
3. **Step-Up Impersonation & Audit Trail**
   - Admin support impersonation requires answering the target user's registered security questions.
   - Generates a scoped `act_as` JWT token, activates an un-dismissible amber warning banner in the UI, and writes an append-only entry to `audit.audit_log`.
4. **Modern Supabase Integration**
   - Supports modern Supabase configuration: Publishable Key (`SUPABASE_PUBLISHABLE_KEY`), Secret Key (`SUPABASE_SECRET_KEY`), and OIDC JWKS verification (`SUPABASE_JWKS_URL`).

---

## 🚀 Getting Started (Local Development)

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 22+
- Java 21 & Maven 3.9+ (optional if using Docker)

### 1. Clone & Setup Environment
```bash
git clone git@github.com:qmainuddin/tradiepulse-platform.git
cd tradiepulse-platform
cp .env.example .env
```

### 2. Start the Local Stack
```bash
# Build and start all services locally
make up
# Or using Taskfile:
task up
```
- **Web App:** [http://localhost:3000](http://localhost:3000)
- **API Gateway:** [http://localhost:8080](http://localhost:8080)
- **AI Agent API:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **RabbitMQ Management:** [http://localhost:15672](http://localhost:15672) (User: `guest` / Pass: `guest`)

### 3. Run Automated Test Suites
```bash
# Run all test suites (Database, NZ Verification, AI Agent, Frontend)
make test
# Or:
task test:all
```

---

## 🚢 CI/CD & Production Deployment (Hostinger VPS)

TradiePulse uses a **Zero-Touch GitOps workflow** powered by **GitHub Actions**:

1. **Automated Testing**: Validates PostGIS spatial matching, NZ IRD modulus-11 checksums, LangGraph state machine, and frontend contracts.
2. **Matrix Image Builds**: Builds Docker images for all 5 services with multi-stage caching and publishes them to **GitHub Container Registry** (`ghcr.io/qmainuddin/tradiepulse-...`).
3. **Zero-Touch SSH Deploy**: Connects to the Hostinger VPS (`72.62.70.145`), dynamically generates `/opt/tradiepulse/.env` from GitHub Secrets, transfers configuration files, joins the existing **`stack`** Docker network, and launches the updated containers.

### Required GitHub Secrets

Configure these in **GitHub Settings → Secrets and variables → Actions**:

| Secret Name | Description |
|---|---|
| `HOSTINGER_SSH_HOST` | Hostinger VPS IP address (`72.62.70.145`) |
| `HOSTINGER_SSH_USER` | SSH Username (`root`) |
| `HOSTINGER_SSH_KEY` / `HOSTINGER_SSH_PASSWORD` | Private SSH key or root password for VPS access |
| `SUPABASE_URL` | Supabase project API URL |
| `SUPABASE_PUBLISHABLE_KEY` | Supabase Publishable / Anon key |
| `SUPABASE_SECRET_KEY` | Supabase Secret / Service Role key |
| `SUPABASE_JWKS_URL` | `https://<project-id>.supabase.co/auth/v1/.well-known/jwks.json` |
| `RESEND_API_KEY` | Resend API key for transactional emails |
| `EMAIL_FROM_ADDRESS` | `noreply@mainuddintalukdar.cloud` |
| `OPENROUTER_API_KEY` | OpenRouter API Key |
| `GROQ_API_KEY` | Groq API Key |
| `JWT_SIGNING_KEY` | 32+ character random secret string |
| `SUPERADMIN_PASSWORD` | Initial password for `admin@mainuddintalukdar.cloud` |

---

## 🌐 Hostinger Reverse Proxy Integration (Caddy)

On the Hostinger VPS, TradiePulse runs under the shared Docker network **`stack`** alongside `portfolio-web`. Add this block to your VPS Caddyfile to route traffic to TradiePulse with automatic HTTPS:

```caddy
tradiepulse.mainuddintalukdar.cloud {
    encode gzip zstd

    # API Gateway routes
    handle /api/* {
        reverse_proxy tradiepulse-gateway:8080
    }
    handle /auth/* {
        reverse_proxy tradiepulse-gateway:8080
    }
    handle /chat/* {
        reverse_proxy tradiepulse-gateway:8080 {
            flush_interval -1
        }
    }
    handle /actuator/* {
        reverse_proxy tradiepulse-gateway:8080
    }

    # Next.js Frontend Shell & Portals
    handle {
        reverse_proxy tradiepulse-frontend:3000
    }
}
```

---

## 📜 Agent Operating Rules & TDD Law

All engineers and autonomous AI agents contributing to this codebase are bound by the operating rules in [**`AGENTS.md`**](AGENTS.md):
- **Prime Directives:** Ship small, ship green. Minimalist dependencies by default. Deterministic state machines over clever prompts.
- **Strict TDD Mandate:** RED (failing test) → GREEN (minimum code) → REFACTOR.
- **Enforced Coverage Gates:** Line $\ge 85\%$, Branch $\ge 80\%$, Critical Paths (Auth, Matching, Verification) $100\%$.
- **Zero Secrets / Zero PII in Logs:** Parameterized queries, defense-in-depth authorization re-checks, and automated PII redaction.

---

## 📄 License
© 2026 TradiePulse New Zealand. All rights reserved.
