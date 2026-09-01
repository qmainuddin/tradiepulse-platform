# ADR 0001: Git Submodules Meta-Repo Topology

## Status
Accepted (Locked Decision)

## Context
TradiePulse consists of 5 microservices (`frontend`, `api-gateway`, `auth-service`, `config-service`, `ai-agent`) and shared infrastructure. We required a topology that allows independent repository ownership, independent CI/CD pipelines, and clear team boundaries while enabling coordinated release orchestration and local single-command execution.

## Decision
Adopt Git Submodules inside a master `tradiepulse-platform` meta-repo.

- Master repo pins exact commit SHAs (no floating branches).
- Git submodules are configured with `push.recurseSubmodules=check` and `submodule.recurse=true`.
- Production `docker-compose.yml` deploys published GHCR container images decoupled from local git submodule checkouts.
- Developer commands are managed via `Taskfile.yml` (`task submodules:sync`, `task submodules:checkout -- main`).

## Consequences & Trade-offs
- **Pros:** Full independence of service repos; clean separation in CI; no nested git clone corruption; single repo for platform integration tests.
- **Cons:** Requires discipline when committing across boundaries (preventing detached HEAD). Mitigated by Taskfile helper scripts.
- **Alternatives Considered & Rejected:**
  - *Monorepo:* Rejected due to tight coupling and repo bloat.
  - *Git Subtree:* Rejected because it vendors child history into the parent repo.
