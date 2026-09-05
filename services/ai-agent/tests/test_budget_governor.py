import unittest
from src.cache.budget_governor import TokenBudgetGovernor

class TestTokenBudgetGovernor(unittest.TestCase):

    def setUp(self):
        self.governor = TokenBudgetGovernor(token_ceiling=4096, max_tool_calls=5)

    def test_within_budget_passes(self):
        self.assertTrue(self.governor.check_request_budget(1200))
        self.assertTrue(self.governor.check_request_budget(4096))

    def test_exceeding_budget_rejected(self):
        self.assertFalse(self.governor.check_request_budget(4097))
        self.assertFalse(self.governor.check_request_budget(8000))

    def test_record_usage_and_metrics(self):
        self.governor.record_usage(tokens_in=350, tokens_out=150, cost_usd=0.00125)
        self.governor.record_usage(tokens_in=500, tokens_out=200, cost_usd=0.00210)

        metrics = self.governor.get_metrics()
        self.assertEqual(metrics["total_tokens_in"], 850)
        self.assertEqual(metrics["total_tokens_out"], 350)
        self.assertEqual(metrics["total_tokens"], 1200)
        self.assertEqual(metrics["total_cost_usd"], 0.00335)


if __name__ == "__main__":
    unittest.main()
