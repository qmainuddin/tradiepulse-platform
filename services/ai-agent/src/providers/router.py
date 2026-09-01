import logging
import time
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel
from src.providers.base import LLMProvider, LLMResponse
from src.providers.openrouter import OpenRouterProvider
from src.providers.groq_provider import GroqProvider

log = logging.getLogger(__name__)

class MultiModelRouter:
    """Intelligent multi-model router with automatic circuit breaking and fallback."""

    def __init__(self, primary: OpenRouterProvider, fallback: GroqProvider, failure_threshold: int = 3, recovery_seconds: float = 60.0):
        self.primary = primary
        self.fallback = fallback
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        
        self._consecutive_failures: int = 0
        self._circuit_open_time: Optional[float] = None

    def is_circuit_open(self) -> bool:
        if self._circuit_open_time is None:
            return False
        if time.time() - self._circuit_open_time > self.recovery_seconds:
            # Half-open: attempt recovery
            log.info("Circuit breaker half-open: probing primary provider")
            self._circuit_open_time = None
            self._consecutive_failures = 0
            return False
        return True

    async def complete(
        self,
        messages: List[Dict[str, str]],
        system_prefix: str = "",
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1
    ) -> LLMResponse:
        if not self.is_circuit_open():
            try:
                response = await self.primary.complete(messages, system_prefix, response_model, temperature)
                self._consecutive_failures = 0
                return response
            except Exception as e:
                self._consecutive_failures += 1
                log.warning("Primary provider failed (error count %d): %s", self._consecutive_failures, e)
                if self._consecutive_failures >= self.failure_threshold:
                    log.error("Tripping circuit breaker! Switching to Groq fallback for %d seconds", self.recovery_seconds)
                    self._circuit_open_time = time.time()

        # Fallback provider execution
        log.info("Executing via fallback provider (Groq)")
        response = await self.fallback.complete(messages, system_prefix, response_model, temperature)
        response.model = f"{response.model} (fallback)"
        return response
