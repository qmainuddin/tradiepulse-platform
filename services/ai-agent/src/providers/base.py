from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator, Type
from pydantic import BaseModel

class LLMResponse(BaseModel):
    content: str
    parsed: Optional[Any] = None
    tokens_in: int = 0
    tokens_out: int = 0
    model: str = ""
    cost_usd: float = 0.0
    cached: bool = False

class LLMProvider(ABC):
    """Abstract LLM Provider interface allowing hot-swappable AI backends."""

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        system_prefix: str = "",
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1
    ) -> LLMResponse:
        """Execute a completion with optional Pydantic schema enforcement."""
        pass

    @abstractmethod
    async def complete_stream(
        self,
        messages: List[Dict[str, str]],
        system_prefix: str = "",
        temperature: float = 0.1
    ) -> AsyncGenerator[str, None]:
        """Stream tokens back to the caller."""
        pass
