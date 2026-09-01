# ADR 0004: Micro-Frontend Architecture via Module Federation

## Status
Accepted (Locked Decision)

## Context
The user experience encompasses four distinct portal domains: Customer Portal, Tradesperson Portal, Admin Console, and an embeddable Chat Widget. We require independent development, testing, and deployment cycles while delivering a unified, seamless single-page application experience.

## Decision
Use Next.js 14 App Router as the Host Shell, orchestrating React + TypeScript micro-frontend remotes via Webpack/Module Federation:
- `customer-portal`
- `tradie-portal`
- `admin-console`
- `chat-widget` (embeddable)

Shared dependencies (`react`, `react-dom`, `@tanstack/react-query`, `zustand`) are configured as singletons in Module Federation config to eliminate duplicate bundle payloads.

## Consequences & Trade-offs
- **Pros:** Remotes deploy independently without whole-app rebuilds; team autonomy; isolated fault domains.
- **Cons:** Setup complexity and shared dependency coordination. Mitigated by TypeScript project references and shared Zod contracts package.
