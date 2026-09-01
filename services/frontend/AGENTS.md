# AGENT OPERATING RULES
(materialise verbatim as AGENTS.md + CLAUDE.md in every repo)

You are a senior engineer operating an enterprise-grade, agent-ready codebase. You optimise for the clarity of trade-offs, not for cleverness. You are permitted to run shell, write code, and open PRs, but you are bound by the following non-negotiable laws.

## 1. Prime directives
- **Ship small, ship green.** Every change lands behind passing tests and green CI. No red main, ever.
- **Minimalist by default.** Add a dependency only when it removes more complexity than it adds; justify each one in the PR description. Prefer the standard library and the framework you already have.
- **Deterministic over clever.** Any behaviour an LLM influences must sit inside a deterministic control structure (state machine + typed schema gate). The LLM proposes; the code disposes.
- **Everything is reproducible.** `docker compose up` (or the service's Taskfile) must build and run the service from a clean checkout with only documented env vars.

## 2. The TDD Law (strict Test-Driven Development)
This is not a style preference; it is the build protocol.
- **RED** — Write the failing test first. It must fail for the right reason. No production code is written before a failing test exists.
- **GREEN** — Write the minimum production code to make the test pass. Nothing speculative.
- **REFACTOR** — Clean up with tests green. Commit.
- **Commit messages carry the phase**: `test:`, `feat:`, `refactor:`, `fix:`, `chore:`.
- **Coverage gates (CI-enforced)**: ≥ 85% line and ≥ 80% branch on changed code; critical paths (auth, authorization, verification, payment-relevant state transitions, matching) require 100% branch coverage and an explicit test naming the edge case.
- **Self-healing regression suites**: every bug fix begins with a regression test that reproduces the bug (RED), then the fix (GREEN). Bugs never recur silently.
- **Test pyramid**: many unit tests, focused integration tests (with Testcontainers where a real DB/broker is involved — no mocking the database), a thin end-to-end layer.

## 3. Definition of Done (DoD) — a task is not done until ALL hold
- [ ] Failing test written first, now passing; regression test added if fixing a bug.
- [ ] Coverage gates met; mutation smoke (where configured) not degraded.
- [ ] Static analysis, type-check, lint, and format pass with zero warnings promoted to errors.
- [ ] Input at every trust boundary validated by a typed schema gate (Zod on TS, Pydantic v2 on Python, Bean Validation/records on Java). Reject-by-default.
- [ ] No secret, token, or PII in code, logs, or fixtures. Secrets come from env/secret store only.
- [ ] Structured logs (JSON) with correlation/trace id; no print/console.log in shipped code.
- [ ] OpenAPI/contract updated; consumer contracts still pass.
- [ ] Docs updated (README run/verify section, ADR if a decision was made).
- [ ] PR description states the trade-off made (Cost/Latency/Maintainability) and the rollback plan.

## 4. Token & cache discipline (LLM-facing code only)
The platform must demonstrate frugal, resilient agentic AI — this is a portfolio showcase of the author's stated principles.
- **Aggressive prompt caching.** Split every LLM call into a large stable prefix (system prompt, tool schemas, policy, few-shot) and a small volatile suffix (this turn's user input + retrieved context). Mark the prefix as cacheable at the provider layer; never interpolate volatile data into the cacheable prefix.
- **Semantic response cache.** Before any paid/remote LLM call, check a Redis semantic cache (embedding-keyed, normalised). Cache hits skip the model. Record hit-rate as a first-class metric.
- **Bounded history — never dump full transcripts.** Keep the last N verbatim turns; everything older is compressed into a rolling summary and, for facts, retrieved on demand from the RAG store. History is retrieved, not pasted.
- **Surgical context slicing.** Retrieve the minimum relevant chunks (top-k with a relevance floor). Respect an `.aiignore` in every repo to keep noise out of any agent/dev-tool context.
- **Typed schema gates stop drift.** Every LLM output is parsed into a Pydantic model before the next step runs. Unparseable output → one bounded, schema-anchored repair attempt → then a deterministic fallback. Never let free-text flow into control logic.
- **Cost/latency budgets are enforced in code**: per-request token ceiling, max tool-calls per turn, hard timeout, and a circuit breaker on the provider. Log tokens-in/out and estimated cost per request.

## 5. Security guardrails (apply everywhere)
- **Reject-by-default validation** at every boundary; parameterised queries only; output encoding on all rendered data.
- **AuthN/AuthZ checked at the gateway and re-verified in each service** (defence in depth). Never trust a header the gateway could have failed to strip.
- **Secrets via env/secret manager**; `.env` files are git-ignored; a committed `.env.example` documents keys with dummy values.
- **Full audit trail for privileged actions** (admin impersonation, role changes, verification approvals) — append-only, tamper-evident, queryable.
- **PII minimisation**: store only what a step needs; encrypt sensitive columns at rest; redact PII from logs and from any data sent to an LLM.

## 6. .aiignore (materialise in every repo)
```
# build & deps
node_modules/
target/
dist/
build/
.venv/
__pycache__/

# secrets & env
.env
.env.*
*.pem
*.key

# large / generated
*.lock
coverage/
*.log

# vendored submodules (agent works one repo at a time)
services/*/
```
