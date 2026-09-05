import unittest
from src.cache.bounded_history import BoundedHistoryManager
from src.schemas.state import ChatMessage

class TestBoundedHistory(unittest.TestCase):

    def setUp(self):
        self.manager = BoundedHistoryManager(max_verbatim_turns=4)

    def test_history_under_ceiling_remains_uncompressed(self):
        messages = [
            ChatMessage(role="user", content="Hello", timestamp="2026-09-05T00:00:00Z"),
            ChatMessage(role="assistant", content="Hi! How can I help?", timestamp="2026-09-05T00:00:01Z"),
            ChatMessage(role="user", content="Need a plumber", timestamp="2026-09-05T00:00:02Z"),
        ]
        verbatim, summary = self.manager.process_history(messages)
        self.assertEqual(len(verbatim), 3)
        self.assertEqual(summary, "")

    def test_history_exceeding_ceiling_compresses_older_turns(self):
        messages = [
            ChatMessage(role="user", content="Turn 1: Broken pipe", timestamp="2026-09-05T00:00:00Z"),
            ChatMessage(role="assistant", content="Turn 1 Response: Where are you?", timestamp="2026-09-05T00:00:01Z"),
            ChatMessage(role="user", content="Turn 2: In Riccarton", timestamp="2026-09-05T00:00:02Z"),
            ChatMessage(role="assistant", content="Turn 2 Response: Tap or toilet?", timestamp="2026-09-05T00:00:03Z"),
            ChatMessage(role="user", content="Turn 3: Tap", timestamp="2026-09-05T00:00:04Z"),
            ChatMessage(role="assistant", content="Turn 3 Response: Checking availability", timestamp="2026-09-05T00:00:05Z"),
        ]
        verbatim, summary = self.manager.process_history(messages)

        # Should keep exactly the last 4 verbatim
        self.assertEqual(len(verbatim), 4)
        self.assertEqual(verbatim[0].content, "Turn 2: In Riccarton")
        self.assertEqual(verbatim[-1].content, "Turn 3 Response: Checking availability")

        # Older 2 messages should be compressed into rolling summary
        self.assertIn("Prior turns summary:", summary)
        self.assertIn("Turn 1: Broken pipe", summary)
        self.assertIn("Turn 1 Response: Where are you?", summary)


if __name__ == "__main__":
    unittest.main()
