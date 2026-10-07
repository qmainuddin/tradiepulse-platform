import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator, Type
import httpx
from pydantic import BaseModel
from src.providers.base import LLMProvider, LLMResponse

log = logging.getLogger(__name__)

class OpenRouterProvider(LLMProvider):
    """OpenRouter Multi-Model Router Provider with aggressive prompt caching."""

    def __init__(self, api_key: str, default_model: str = "meta-llama/llama-3.3-70b-instruct:free", timeout: float = 30.0):
        self.api_key = api_key or ""
        self.default_model = default_model
        self.timeout = timeout
        self.base_url = "https://openrouter.ai/api/v1"

    async def complete(
        self,
        messages: List[Dict[str, str]],
        system_prefix: str = "",
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1
    ) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://tradiepulse.mainuddintalukdar.cloud",
            "X-Title": "TradiePulse Conversational AI"
        }

        # Build payload with stable system prefix marked for prompt caching
        payload_messages = []
        if system_prefix:
            payload_messages.append({"role": "system", "content": system_prefix})
        payload_messages.extend(messages)

        if response_model is not None:
            schema_json = json.dumps(response_model.model_json_schema())
            system_instruction = f"\nYou MUST respond strictly in valid JSON conforming to this JSON Schema:\n{schema_json}\nReturn ONLY the JSON object, with no markdown code blocks or commentary."
            if payload_messages and payload_messages[0]["role"] == "system":
                payload_messages[0]["content"] += system_instruction
            else:
                payload_messages.insert(0, {"role": "system", "content": system_instruction})

        payload = {
            "model": self.default_model,
            "messages": payload_messages,
            "temperature": temperature
        }

        # If using mock key or local development without live paid key, return deterministic mock
        if not self.api_key or "mock" in self.api_key.lower() or self.api_key.startswith("sk-or-mock") or self.api_key == "":
            return self._mock_completion(messages, response_model)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()

            choice = data["choices"][0]["message"]
            raw_content = choice.get("content", "")
            usage = data.get("usage", {})
            tokens_in = usage.get("prompt_tokens", 0)
            tokens_out = usage.get("completion_tokens", 0)

            parsed_obj = None
            if response_model is not None:
                parsed_obj = self._parse_json(raw_content, response_model)

            return LLMResponse(
                content=raw_content,
                parsed=parsed_obj,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                model=self.default_model,
                cost_usd=(tokens_in * 0.00000015) + (tokens_out * 0.0000006)
            )

    async def complete_stream(
        self,
        messages: List[Dict[str, str]],
        system_prefix: str = "",
        temperature: float = 0.1
    ) -> AsyncGenerator[str, None]:
        if not self.api_key or "mock" in self.api_key.lower() or self.api_key.startswith("sk-or-mock"):
            for word in ["Kia ", "ora! ", "I'm ", "connecting ", "you ", "with ", "a ", "local ", "tradie."]:
                yield word
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload_messages = []
        if system_prefix:
            payload_messages.append({"role": "system", "content": system_prefix})
        payload_messages.extend(messages)

        payload = {
            "model": self.default_model,
            "messages": payload_messages,
            "temperature": temperature,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue

    def _parse_json(self, text: str, model_cls: Type[BaseModel]) -> Optional[BaseModel]:
        try:
            cleaned = text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            data = json.loads(cleaned)
            return model_cls.model_validate(data)
        except Exception as e:
            log.warning("Failed to parse JSON into model %s: %s", model_cls.__name__, e)
            return None

    def _mock_completion(self, messages: List[Dict[str, str]], response_model: Optional[Type[BaseModel]]) -> LLMResponse:
        raw_msg = " ".join([m.get("content", "") for m in messages])
        user_line = raw_msg
        for line in raw_msg.split("\n"):
            if line.startswith("Customer Input:"):
                user_line = line[15:].strip()
                break

        user_text = user_line.lower()
        
        if response_model is not None and response_model.__name__ == "IntakeClassification":
            is_plumber = any(w in user_text for w in ["plumb", "tap", "leak", "pipe", "drain", "toilet", "water", "sink", "cylinder", "dripping", "blocked", "hot water", "basin"])
            is_electrician = any(w in user_text for w in ["electr", "spark", "wire", "power", "switch", "light", "fuse", "socket", "tripping", "board", "solar", "circuit", "ev charger"])
            is_mechanic = any(w in user_text for w in ["mechan", "car", "engine", "brake", "wof", "auto", "vehicle", "clutch", "tyre", "tire", "battery", "oil", "transmission", "suspension"])

            if is_plumber:
                trade = "plumber"
            elif is_electrician:
                trade = "electrician"
            elif is_mechanic:
                trade = "mechanic"
            else:
                trade = None
            
            is_ambiguous = trade is None
            clarification = "Could you please clarify what needs fixing? (For example: leaking tap, faulty power point, or car engine issue)" if is_ambiguous else None
            
            mock_data = {
                "trade": trade,
                "confidence": 0.95 if trade else 0.2,
                "problem_summary": "Customer reported issue: " + user_text[:60],
                "is_ambiguous": is_ambiguous,
                "clarification_needed": clarification
            }
            return LLMResponse(
                content=json.dumps(mock_data),
                parsed=response_model.model_validate(mock_data),
                tokens_in=120,
                tokens_out=45,
                model=self.default_model
            )
        
        if response_model is not None and response_model.__name__ == "LocationExtraction":
            suburbs = {
                "riccarton": (-43.5310, 172.5970, "Riccarton, Christchurch"),
                "papanui": (-43.4980, 172.6050, "Papanui, Christchurch"),
                "hornby": (-43.5410, 172.5270, "Hornby, Christchurch"),
                "st albans": (-43.5120, 172.6350, "St Albans, Christchurch"),
                "fendalton": (-43.5150, 172.6020, "Fendalton, Christchurch"),
                "merivale": (-43.5140, 172.6240, "Merivale, Christchurch"),
                "linwood": (-43.5350, 172.6680, "Linwood, Christchurch"),
                "rangiora": (-43.3031, 172.5954, "Rangiora, Canterbury"),
                "rolleston": (-43.5930, 172.3800, "Rolleston, Canterbury"),
            }
            matched_loc = "Christchurch"
            matched_lat = -43.5321
            matched_lon = 172.6362

            for sub, (lat, lon, name) in suburbs.items():
                if sub in user_text:
                    matched_loc = name
                    matched_lat = lat
                    matched_lon = lon
                    break

            mock_data = {
                "location_name": matched_loc,
                "latitude": matched_lat,
                "longitude": matched_lon,
                "is_canterbury_region": True
            }
            return LLMResponse(
                content=json.dumps(mock_data),
                parsed=response_model.model_validate(mock_data),
                tokens_in=80,
                tokens_out=30,
                model=self.default_model
            )

        return LLMResponse(
            content="I can connect you with the nearest qualified tradesperson in Christchurch.",
            tokens_in=50,
            tokens_out=20,
            model=self.default_model
        )
