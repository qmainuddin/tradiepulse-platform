import logging
import time
from typing import Dict, Any, Optional
from src.rag.pii_redactor import PIIRedactor

log = logging.getLogger(__name__)

class InteractionLogger:
    """Mid-layer logger writing sanitized pre/post LLM payloads to Qdrant interactions collection."""

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.qdrant_url = qdrant_url
        self.interactions_collection = "interactions"

    async def log_interaction(
        self,
        session_id: str,
        user_message: str,
        system_prefix: str,
        model_name: str,
        response_content: str,
        tokens_in: int,
        tokens_out: int,
        latency_ms: int,
        cache_hit: bool,
        cost_usd: float
    ) -> None:
        sanitized_user_msg = PIIRedactor.redact(user_message)
        sanitized_response = PIIRedactor.redact(response_content)

        payload = {
            "session_id": session_id,
            "timestamp": time.time(),
            "user_message": sanitized_user_msg,
            "model": model_name,
            "response": sanitized_response,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "latency_ms": latency_ms,
            "cache_hit": cache_hit,
            "cost_usd": cost_usd
        }

        log.info("[INTERACTION LOG] session=%s model=%s tokens_in=%d tokens_out=%d latency=%dms cache_hit=%s cost=$%.6f",
                 session_id, model_name, tokens_in, tokens_out, latency_ms, cache_hit, cost_usd)
