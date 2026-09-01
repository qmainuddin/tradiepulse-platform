# ADR 0003: OpenRouter Multi-Model Router with Groq Fallback

## Status
Accepted (Locked Decision)

## Context
LLM costs, rate limits, and model deprecations pose operational risks. The AI Agent Service requires support for free and cost-effective multi-model routing with low latency and fallback resiliency.

## Decision
Implement a provider-agnostic `LLMProvider` interface:
1. **Primary Provider:** OpenRouter API (enabling access to free and low-cost models such as Llama 3.3, Mistral, Gemini Flash without SDK lock-in).
2. **Fallback Provider:** Groq API (ultra-low latency Llama 3 models triggered upon circuit-breaker trip or upstream rate limit).
3. **Configuration:** Active model IDs, temperature, and tokens are read dynamically from Spring Cloud Config / environment variables, never hardcoded.

## Consequences & Trade-offs
- **Cost:** Leverages free tier and cost-optimized models.
- **Resilience:** Automatic failover via circuit breaker on timeout or 429/5xx errors.
- **Latency:** Groq fallback provides sub-second inference if primary provider degrades.
