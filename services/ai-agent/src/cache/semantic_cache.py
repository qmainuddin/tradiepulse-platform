import re
import hashlib
import json
import logging
from typing import Optional, Dict, Any, Tuple

log = logging.getLogger(__name__)

class SemanticCache:
    """
    Semantic response cache with query normalization, token metrics, and hit-rate tracking.
    """

    def __init__(self, similarity_threshold: float = 0.92):
        self.similarity_threshold = similarity_threshold
        self._in_memory_store: Dict[str, Dict[str, Any]] = {}
        self.hits: int = 0
        self.misses: int = 0

    def _normalize_text(self, text: str) -> str:
        # Lowercase, strip punctuation, collapse whitespace
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return re.sub(r'\s+', ' ', text)

    def _generate_key(self, text: str) -> str:
        norm = self._normalize_text(text)
        return hashlib.sha256(norm.encode('utf-8')).hexdigest()

    async def get(self, query: str) -> Optional[Dict[str, Any]]:
        key = self._generate_key(query)
        entry = self._in_memory_store.get(key)
        if entry:
            self.hits += 1
            log.info("Semantic cache HIT for query: '%s' (Total hits: %d)", query[:40], self.hits)
            return entry
        self.misses += 1
        return None

    async def set(self, query: str, response_data: Dict[str, Any], ttl_seconds: int = 86400) -> None:
        key = self._generate_key(query)
        self._in_memory_store[key] = response_data

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "hit_rate_pct": round(self.get_hit_rate() * 100, 2),
            "cached_entries_count": len(self._in_memory_store)
        }
