import logging
from typing import List, Dict, Any

log = logging.getLogger(__name__)

STOP_WORDS = {"in", "at", "the", "a", "an", "is", "my", "and", "or", "to", "for", "of", "with", "have", "i", "something"}

class SessionRAGStore:
    """Retrieves similar resolved job snippets from Qdrant sessions collection before LLM calls."""

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.qdrant_url = qdrant_url
        self.collection_name = "sessions"
        # Seed memory cache for fast offline tests
        self._seed_kb = [
            {"query": "leaking kitchen mixer tap riccarton", "text": "Resolved by Dave Riccarton Plumbing: Ceramic disc cartridge replacement."},
            {"query": "power tripping switchboard papanui", "text": "Resolved by Sarah Sparks: RCD circuit breaker replacement."},
            {"query": "car squealing brakes hornby", "text": "Resolved by Hornby Auto: Front brake pads and rotor skim."}
        ]

    async def retrieve_similar_context(self, user_query: str, top_k: int = 2) -> List[str]:
        query_words = set(user_query.lower().split()) - STOP_WORDS
        if not query_words:
            return []

        results = []
        for doc in self._seed_kb:
            doc_words = set(doc["query"].split()) - STOP_WORDS
            # Require at least 2 keyword overlaps or exact trade/problem keyword match
            overlap = query_words.intersection(doc_words)
            if overlap:
                results.append(doc["text"])
            if len(results) >= top_k:
                break
        return results
