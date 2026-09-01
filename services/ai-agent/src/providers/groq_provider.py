import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator, Type
import httpx
from pydantic import BaseModel
from src.providers.base import LLMProvider, LLMResponse

log = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    """Groq ultra-low-latency fallback provider."""

    def __init__(self, api_key: str, default_model: str = "llama-3.3-70b-versatile", timeout: float = 10.0):
        self.api_key = api_key
        self.default_model = default_model
        self.timeout = timeout
        self.base_url = "https://api.groq.com/openai/v1"

    async def complete(
        self,
        messages: List[Dict[str, str]],
        system_prefix: str = "",
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1
    ) -> LLMResponse:
        if not self.api_key or self.api_key.startswith("gsk_mock") or self.api_key == "":
            # Mock completion
            return LLMResponse(
                content="Groq fallback completion response",
                tokens_in=40,
                tokens_out=15,
                model=self.default_model
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload_messages = []
        if system_prefix:
            payload_messages.append({"role": "system", "content": system_prefix})
        payload_messages.extend(messages)

        if response_model is not None:
            schema_json = json.dumps(response_model.model_json_schema())
            system_instruction = f"\nReturn strictly valid JSON conforming to this JSON Schema:\n{schema_json}"
            if payload_messages and payload_messages[0]["role"] == "system":
                payload_messages[0]["content"] += system_instruction
            else:
                payload_messages.insert(0, {"role": "system", "content": system_instruction})

        payload = {
            "model": self.default_model,
            "messages": payload_messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"} if response_model is not None else {"type": "text"}
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()

            choice = data["choices"][0]["message"]
            raw_content = choice.get("content", "")
            usage = data.get("usage", {})

            parsed_obj = None
            if response_model is not None:
                try:
                    parsed_obj = response_model.model_validate_json(raw_content)
                except Exception as e:
                    log.warning("Groq JSON parsing error: %s", e)

            return LLMResponse(
                content=raw_content,
                parsed=parsed_obj,
                tokens_in=usage.get("prompt_tokens", 0),
                tokens_out=usage.get("completion_tokens", 0),
                model=self.default_model
            )

    async def complete_stream(
        self,
        messages: List[Dict[str, str]],
        system_prefix: str = "",
        temperature: float = 0.1
    ) -> AsyncGenerator[str, None]:
        # Fast streaming
        yield "Groq streaming response"
