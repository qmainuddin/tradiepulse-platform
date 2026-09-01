# ADR 0002: RabbitMQ Event Broker with Broker-Agnostic Port

## Status
Accepted (Locked Decision)

## Context
Asynchronous events (e.g., `session.completed` triggering RAG ingestion) require reliable messaging. The production environment is a single Hostinger VPS running Docker Compose.

## Decision
Use **RabbitMQ** (Alpine container) with a broker-agnostic `EventPublisher` / `EventConsumer` port interface in the application code.

## Consequences & Trade-offs
- **Cost & RAM:** RabbitMQ consumes ~50MB RAM compared to Apache Kafka/Zookeeper/KRaft consuming ~1GB+ on a single VPS.
- **Latency & Reliability:** AMQP 0-9-1 with persistent message delivery guarantees high throughput and low resource footprint.
- **Maintainability & Portability:** Designing the `EventBroker` interface cleanly allows a zero-code-change drop-in swap to Kafka or Cloud Pub/Sub if scale requires multi-node clustering in Phase 2.
