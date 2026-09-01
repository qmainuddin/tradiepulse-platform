import json
import logging
from typing import Type, Tuple, Optional
from pydantic import BaseModel, ValidationError

log = logging.getLogger(__name__)

class TypedSchemaGate:
    """
    Guarantees that no free-form unstructured LLM text ever flows into control logic.
    Enforces 1 bounded repair attempt before executing a deterministic fallback.
    """

    @classmethod
    async def parse_and_validate(
        cls,
        raw_output: str,
        target_schema: Type[BaseModel],
        router=None,
        messages=None
    ) -> Tuple[Optional[BaseModel], bool]:
        """
        Returns (parsed_instance, was_repaired).
        """
        # Step 1: Direct JSON parsing
        try:
            cleaned = cls._clean_json(raw_output)
            data = json.loads(cleaned)
            return target_schema.model_validate(data), False
        except (json.JSONDecodeError, ValidationError) as e:
            log.warning("Schema Gate validation failed: %s. Initiating bounded 1-step repair.", e)

        # Step 2: Bounded 1-step Schema-Anchored Repair
        if router is not None and messages is not None:
            try:
                schema_json = json.dumps(target_schema.model_json_schema())
                repair_prompt = f"""Your previous output failed strict JSON Schema validation.
Previous output:
{raw_output}

You must repair this output to strictly conform to this JSON schema:
{schema_json}
Return ONLY the raw JSON object."""
                
                repair_messages = list(messages) + [{"role": "user", "content": repair_prompt}]
                repair_response = await router.complete(repair_messages, response_model=target_schema)
                if repair_response.parsed is not None:
                    log.info("Bounded schema repair succeeded on attempt 1!")
                    return repair_response.parsed, True
            except Exception as repair_err:
                log.error("Bounded repair attempt failed: %s", repair_err)

        # Step 3: Failure
        return None, False

    @staticmethod
    def _clean_json(text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
