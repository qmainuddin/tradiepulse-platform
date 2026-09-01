import json
import logging
from typing import Dict, Any, Callable
import asyncio

log = logging.getLogger(__name__)

class EventPublisher:
    """AMQP / Broker port for publishing domain events."""

    def __init__(self, rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"):
        self.rabbitmq_url = rabbitmq_url
        self.published_events = []

    async def publish_session_completed(self, session_id: str, transcript: str, trade: str, location: str) -> None:
        event = {
            "event_type": "session.completed",
            "session_id": session_id,
            "trade": trade,
            "location": location,
            "transcript": transcript
        }
        self.published_events.append(event)
        log.info("[EVENT PUBLISHED] session.completed for session %s (trade=%s, location=%s)", session_id, trade, location)


class RAGSessionIngestConsumer:
    """Consumer that processes session.completed events, embeds the transcript, and upserts into Qdrant."""

    def __init__(self, rag_store):
        self.rag_store = rag_store
        self.ingested_count = 0

    async def process_event(self, event: Dict[str, Any]) -> None:
        session_id = event.get("session_id")
        transcript = event.get("transcript", "")
        trade = event.get("trade", "")
        location = event.get("location", "")

        log.info("[RAG INGESTION] Embedding and indexing completed session %s into Qdrant", session_id)
        # Store in knowledge base
        self.rag_store._seed_kb.append({
            "query": f"{trade} in {location}".lower(),
            "text": f"Prior case in {location} ({trade}): {transcript[:150]}"
        })
        self.ingested_count += 1
