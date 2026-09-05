import unittest
import asyncio
from unittest.mock import AsyncMock
from src.agent.gates import TypedSchemaGate
from src.schemas.schemas import IntakeClassification, LocationExtraction, MatchConfirmation
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

    def test_bounded_repair_success(self):
        async def run_test():
            corrupted_json = "I think the trade is plumber with high confidence"
            repaired_model = IntakeClassification(
                trade=TradeType.PLUMBER,
                confidence=0.88,
                problem_summary="Burst pipe under bathroom vanity",
                is_ambiguous=False,
                clarification_needed=None
            )

            mock_response = AsyncMock()
            mock_response.parsed = repaired_model

            mock_router = AsyncMock()
            mock_router.complete.return_value = mock_response

            messages = [{"role": "user", "content": "Help with burst pipe"}]
            parsed, was_repaired = await TypedSchemaGate.parse_and_validate(
                corrupted_json,
                IntakeClassification,
                router=mock_router,
                messages=messages
            )

            self.assertIsNotNone(parsed)
            self.assertTrue(was_repaired)
            self.assertEqual(parsed.trade, TradeType.PLUMBER)
            self.assertEqual(parsed.confidence, 0.88)
            mock_router.complete.assert_called_once()

        asyncio.run(run_test())

    def test_location_extraction_schema_validation(self):
        async def run_test():
            valid_loc_json = """{
                "location_name": "Riccarton, Christchurch",
                "latitude": -43.531,
                "longitude": 172.597,
                "is_canterbury_region": true
            }"""
            parsed, was_repaired = await TypedSchemaGate.parse_and_validate(valid_loc_json, LocationExtraction)
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.location_name, "Riccarton, Christchurch")
            self.assertEqual(parsed.latitude, -43.531)
            self.assertTrue(parsed.is_canterbury_region)
            self.assertFalse(was_repaired)

        asyncio.run(run_test())

    def test_match_confirmation_schema_validation(self):
        async def run_test():
            valid_conf_json = """{
                "is_confirmed": true,
                "selected_tradie_id": "tradie-uuid-8899",
                "user_notes": "Please call before arrival"
            }"""
            parsed, was_repaired = await TypedSchemaGate.parse_and_validate(valid_conf_json, MatchConfirmation)
            self.assertIsNotNone(parsed)
            self.assertTrue(parsed.is_confirmed)
            self.assertEqual(parsed.selected_tradie_id, "tradie-uuid-8899")
            self.assertEqual(parsed.user_notes, "Please call before arrival")
            self.assertFalse(was_repaired)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
