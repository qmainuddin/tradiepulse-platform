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

## 🧪 Comprehensive Automated Test Suites & Added Test Cases

TradiePulse adheres strictly to the **TDD Law** (RED $\to$ GREEN $\to$ REFACTOR) with 41+ automated tests across all operational tiers:

```
Test Suites Inventory:
├── services/db/tests/test_spatial_matching.py         (7 tests, 100% Green)
├── services/db/verification/test_verification.py       (6 tests, 100% Green)
├── services/ai-agent/tests/test_bounded_history.py     (2 tests, 100% Green)
├── services/ai-agent/tests/test_budget_governor.py     (3 tests, 100% Green)
├── services/ai-agent/tests/test_schema_gates.py        (6 tests, 100% Green)
├── services/ai-agent/tests/test_pii_redactor.py        (7 tests, 100% Green)
├── services/ai-agent/tests/test_semantic_cache.py      (4 tests, 100% Green)
├── services/ai-agent/tests/test_workflow.py            (5 tests, 100% Green)
└── services/frontend/packages/contracts/               (Contracts Validated)
```

### Detailed Breakdown of Added Test Cases

#### 1. AI Agent Guardrails & Token Discipline (`services/ai-agent/tests/`)
- **Bounded History Management (`test_bounded_history.py`)**:
  - `test_history_under_ceiling_remains_uncompressed`: Verifies conversation history below the limit ($N \le 4$) is kept verbatim without distortion.
  - `test_history_exceeding_ceiling_compresses_older_turns`: Verifies that conversations $> 4$ turns retain the last 4 turns verbatim and compress earlier turns into structured rolling summaries to prevent unbounded context burn.
- **Token Budget Governor (`test_budget_governor.py`)**:
  - `test_within_budget_passes`: Verifies prompts within the 4096 request token ceiling pass validation.
  - `test_exceeding_budget_rejected`: Enforces ceiling violation rejection on prompts $> 4096$ tokens.
  - `test_record_usage_and_metrics`: Verifies multi-turn cumulative token tracking (tokens in, tokens out, total USD cost).
- **Typed Schema Gates & Self-Healing (`test_schema_gates.py`)**:
  - `test_direct_valid_json_parsing`: Direct validation of `IntakeClassification` Pydantic models.
  - `test_markdown_fence_cleaning`: Verifies automatic extraction and sanitization of JSON enclosed in ` ```json ... ``` ` fences.
  - `test_bounded_repair_success`: Simulates corrupted/hallucinated LLM output and verifies 1-step schema-anchored repair recovery.
  - `test_location_extraction_schema_validation`: Validates Canterbury spatial extraction schemas.
  - `test_match_confirmation_schema_validation`: Validates structured booking confirmation models.
- **NZ PII Redaction (`test_pii_redactor.py`)**:
  - `test_redact_nz_phone_numbers`: Redacts local NZ mobiles (`021`, `022`, `027`) and landlines (`03`, `04`, `09`).
  - `test_redact_nz_international_phone`: Redacts E.164 and international format NZ numbers (`+64 21...`, `+64-3-...`).
  - `test_redact_nz_ird_numbers`: Redacts 8-digit and 9-digit IRD numbers (`123-456-789`, `49-091-850`).
  - `test_redact_credit_cards`: Redacts Visa/Mastercard credit card sequences.
  - `test_redact_multiple_pii_in_single_message`: Verifies simultaneous multi-PII sanitization in a single complex input turn.
  - `test_no_pii_passthrough`: Ensures no false positives or text degradation on normal trades problem descriptions.
- **Semantic Response Cache (`test_semantic_cache.py`)**:
  - `test_cache_miss_then_hit_with_normalized_query`: Verifies semantic key hashing and 0-token hit retrieval.
  - `test_distinct_queries_do_not_collide`: Ensures distinct trade requests (plumber vs. electrician) do not produce false positive collisions.
  - `test_get_metrics_reporting`: Verifies accurate hit-rate percentage calculation and telemetry.
  - `test_whitespace_and_punctuation_normalization`: Handles chaotic punctuation and irregular spacing.
- **Multi-Trade Workflow Orchestration (`test_workflow.py`)**:
  - `test_full_plumber_matching_conversation`: Complete multi-turn plumber booking and event publishing flow.
  - `test_electrician_matching_flow`: End-to-end electrical problem intake in Papanui.
  - `test_mechanic_matching_flow`: End-to-end automotive breakdown problem intake in Hornby.
  - `test_ambiguous_request_triggers_clarification`: Deterministic clarification branching when request spans multiple trades.
  - `test_workflow_budget_tracking_and_metrics`: Validates token usage metrics logging across workflow steps.

#### 2. PostGIS Spatial Matching & NZ Compliance (`services/db/`)
- **Spatial Matching Engine (`test_spatial_matching.py`)**:
  - `test_nearest_tradie_ordering`: Proves that distance sorting ranks closer tradies first (Riccarton $\approx 3.2\text{km}$ over Papanui $\approx 4.4\text{km}$).
  - `test_rating_tie_breaker_for_equal_distance`: Verifies that if two tradies are at the same distance, the higher-rated tradie ranks first.
  - `test_radius_cutoff`: Verifies strict exclusion of tradies outside customer radius (excluding Rangiora $\approx 25\text{km}$ and Dunedin $\approx 360\text{km}$).
  - `test_unverified_tradies_excluded`: Guarantees unverified and inactive tradies never appear in match results.
  - `test_availability_filter`: Enforces day-of-week calendar availability filtering.
  - `test_limit_truncation`: Validates returned result truncation against request limits.
  - `test_empty_candidates_returns_empty`: Safe handling of zero-candidate spatial queries.
- **NZ Licensing & Regulatory Compliance (`test_verification.py`)**:
  - `test_ird_modulus11_checksum`: Validates official NZ Inland Revenue Modulus-11 checksums for both 8-digit and 9-digit formats (`49-091-850`, `49-098-847`, `105-001-541`).
  - `test_ewrb_license_verification`: Validates Electrical Workers Registration Board licence format and inspector status.
  - `test_pgdb_license_verification`: Validates Plumbers, Gasfitters and Drainlayers Board registration.
  - `test_christchurch_regional_compliance`: Enforces mandatory NZ \$2M Public Liability Insurance and Canterbury building code standards.
  - `test_full_tradie_onboarding_verification_pipeline`: Full orchestration pipeline verifying tax, licence, and regional insurance sequentially.

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

## 🔮 Phase 2 Extension & Future Roadmap

The Phase 2 expansion focuses on transitioning TradiePulse from an intelligent matchmaking portal into a full-lifecycle, automated operational backbone for New Zealand trades businesses:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               TRADIEPULSE PHASE 2 ROADMAP                              │
├──────────────────────────────┬─────────────────────────────┬───────────────────────────┤
│ 1. Instant Mobile Dispatch   │ 2. Live GPS & ETA Tracking  │ 3. Milestone Escrow & GST │
│    • 2-way Twilio SMS Bridge │    • WebSocket Live Stream  │    • Stripe NZ Integration│
│    • WhatsApp Notifications  │    • PostGIS Arrival Fences │    • Automatic 15% GST    │
├──────────────────────────────┼─────────────────────────────┼───────────────────────────┤
│ 4. Real-time MBIE Live Sync  │ 5. Nationwide Expansion     │ 6. Multimodal Voice AI    │
│    • EWRB/PGDB API Webhooks  │    • Auckland, Wellington   │    • Gemini Live Phone Bot│
│    • Auto-Revocation on Expiry│   • Localized Council Codes│    • Site Photo Damage RAG│
└──────────────────────────────┴─────────────────────────────┴───────────────────────────┘
```

### 1. Instant Mobile Dispatch & SMS/WhatsApp Bridge (Twilio / Resend)
- **Problem**: Busy tradies are on job sites or driving and cannot continuously monitor a web dashboard.
- **Phase 2 Solution**:
  - Immediate two-way SMS & WhatsApp dispatch when a customer problem is classified.
  - Tradies can accept or decline jobs by simply replying `"1"` (Accept) or `"2"` (Decline) to an automated SMS.
  - Virtual masked phone numbers protect both customer and tradie privacy under NZ Privacy Act 2020.

### 2. Live GPS Tracking & Geofenced Arrival Notifications
- **Problem**: Homeowners experience friction not knowing exact tradie arrival times within broad 4-hour booking windows.
- **Phase 2 Solution**:
  - Tradie mobile companion PWA streams GPS coordinates via WebSockets when en-route.
  - PostGIS `ST_DWithin` spatial trigger automatically sends customer notifications: *"Dave is 5 minutes away (approx 2.1km)"*.
  - Real-time live interactive map in the Customer Portal showing tradie transit progress.

### 3. Stripe NZ & Milestone-Based Escrow Payments
- **Problem**: Tradies struggle with late invoice payments, while customers fear paying upfront before inspection.
- **Phase 2 Solution**:
  - Integration with **Stripe Connect NZ** for automated pre-authorized milestone escrow.
  - Customer funds are held safely upon booking confirmation and released upon customer digital sign-off.
  - Automatic generation of New Zealand GST-compliant (15%) tax invoices with IRD numbers formatted for Xero and MYOB.

### 4. Real-Time MBIE Regulatory Sync (EWRB & PGDB Webhooks)
- **Problem**: Manual license uploads can expire or be suspended without the platform knowing.
- **Phase 2 Solution**:
  - Direct integration with the **Ministry of Business, Innovation and Employment (MBIE)** public API register.
  - Nightly automated cron synchronization to verify practicing license status.
  - Instant automated suspension of tradie profile from search catalog if their practicing license expires or is revoked.

### 5. Nationwide Multi-City Spatial Expansion
- **Problem**: Current PostGIS index and regional rules are focused primarily on Greater Christchurch & Canterbury.
- **Phase 2 Solution**:
  - Expand spatial partitions to **Auckland, Wellington, Hamilton, Tauranga, and Queenstown**.
  - Local council building consent rules and geographic terrain routing (e.g. alpine and ferry transport considerations).

### 6. Voice AI Dispatcher & Multimodal Site Assessment (Gemini Live API)
- **Problem**: Elderly homeowners and tradies in transit prefer speaking over typing.
- **Phase 2 Solution**:
  - Integration of **Gemini Live API** bidirectional low-latency audio for phone-in bookings.
  - **Multimodal Site Photo Analysis**: Homeowners upload photos of damaged pipes or electrical boards; computer vision estimates required replacement parts and flags safety hazards prior to tradie arrival.

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
