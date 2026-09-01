from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List
import asyncio

class Channel(ABC):
    """Transport-agnostic channel port. The core agent graph is completely decoupled from HTTP/SSE/WebSocket/Voice."""
    
    @abstractmethod
    async def send_token(self, token: str) -> None:
        """Stream a single generated token to the client."""
        pass

    @abstractmethod
    async def send_message(self, content: str, metadata: Dict[str, Any] = None) -> None:
        """Send a complete message block."""
        pass

    @abstractmethod
    async def send_proposal(self, candidates: List[Dict[str, Any]]) -> None:
        """Send structured candidate tradie cards."""
        pass


class TextChannel(Channel):
    """Text-based channel adapter for SSE and WebSockets."""

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._is_closed: bool = False

    async def send_token(self, token: str) -> None:
        await self._queue.put({"type": "token", "data": token})

    async def send_message(self, content: str, metadata: Dict[str, Any] = None) -> None:
        await self._queue.put({"type": "message", "data": content, "metadata": metadata or {}})

    async def send_proposal(self, candidates: List[Dict[str, Any]]) -> None:
        await self._queue.put({"type": "proposal", "data": candidates})

    async def close(self) -> None:
        self._is_closed = True
        await self._queue.put({"type": "done"})

    async def event_generator(self) -> AsyncGenerator[Dict[str, Any], None]:
        while not self._is_closed or not self._queue.empty():
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                yield event
                if event.get("type") == "done":
                    break
            except asyncio.TimeoutError:
                if self._is_closed and self._queue.empty():
                    break
                continue


class VoiceChannel(Channel):
    """Phase 2 Transport Seam for bidirectional audio streaming (WebRTC / Live API)."""
    
    async def send_token(self, token: str) -> None:
        # Phase 2: Convert tokens to TTS audio frames
        pass

    async def send_message(self, content: str, metadata: Dict[str, Any] = None) -> None:
        pass

    async def send_proposal(self, candidates: List[Dict[str, Any]]) -> None:
        pass
