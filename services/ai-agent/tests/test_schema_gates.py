import unittest
import asyncio
from src.agent.gates import TypedSchemaGate
from src.schemas.schemas import IntakeClassification
from src.schemas.state import TradeType

class TestSchemaGates(unittest.TestCase):

    def test_direct_valid_json_parsing(self):
        async def run_test():
            raw_json = '{"trade": "plumber", "confidence": 0.95, "problem_summary": "Kitchen mixer tap dripping", "is_ambiguous": false, "clarification_needed": null}'
            parsed, was_repaired = await TypedSchemaGate.parse_and_validate(raw_json, IntakeClassification)
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.trade, TradeType.PLUMBER)
            self.assertEqual(parsed.confidence, 0.95)
            self.assertFalse(was_repaired)

        asyncio.run(run_test())

    def test_markdown_fence_cleaning(self):
        async def run_test():
            raw_markdown = """```json
{
    "trade": "electrician",
    "confidence": 0.90,
    "problem_summary": "Fuse board tripping in garage",
    "is_ambiguous": false,
    "clarification_needed": null
}
```"""
            parsed, was_repaired = await TypedSchemaGate.parse_and_validate(raw_markdown, IntakeClassification)
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.trade, TradeType.ELECTRICIAN)
            self.assertFalse(was_repaired)

        asyncio.run(run_test())

    def test_invalid_json_returns_none_when_no_router(self):
        async def run_test():
            corrupted_json = '{"trade": "plumber", "confidence": "HIGH_CONFIDENCE_NOT_A_FLOAT"}'
            parsed, was_repaired = await TypedSchemaGate.parse_and_validate(corrupted_json, IntakeClassification)
            self.assertIsNone(parsed)
            self.assertFalse(was_repaired)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
