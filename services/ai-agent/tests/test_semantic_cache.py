import unittest
import asyncio
from src.cache.semantic_cache import SemanticCache

class TestSemanticCache(unittest.TestCase):

    def setUp(self):
        self.cache = SemanticCache(similarity_threshold=0.92)

    def test_cache_miss_then_hit_with_normalized_query(self):
        async def run_test():
            query1 = "I have a leaking tap in Riccarton, Christchurch!"
            query2 = "i have a leaking tap in riccarton christchurch"

            # 1. First lookup: Miss
            entry1 = await self.cache.get(query1)
            self.assertIsNone(entry1)
            self.assertEqual(self.cache.hits, 0)
            self.assertEqual(self.cache.misses, 1)

            # 2. Store response
            payload = {"message": "Matched with Dave Riccarton Plumbing", "trade": "plumber"}
            await self.cache.set(query1, payload)

            # 3. Second lookup with different punctuation/casing: Hit
            entry2 = await self.cache.get(query2)
            self.assertIsNotNone(entry2)
            self.assertEqual(entry2["trade"], "plumber")
            self.assertEqual(self.cache.hits, 1)
            self.assertEqual(self.cache.misses, 1)
            self.assertEqual(self.cache.get_hit_rate(), 0.5)

        asyncio.run(run_test())

    def test_distinct_queries_do_not_collide(self):
        async def run_test():
            plumber_query = "Plumber needed for clogged toilet in St Albans"
            electrician_query = "Electrician needed for flickering lights in St Albans"

            await self.cache.set(plumber_query, {"trade": "plumber"})

            # Query electrician: should miss
            entry = await self.cache.get(electrician_query)
            self.assertIsNone(entry)

            # Query plumber: should hit
            hit_entry = await self.cache.get(plumber_query)
            self.assertIsNotNone(hit_entry)
            self.assertEqual(hit_entry["trade"], "plumber")

        asyncio.run(run_test())

    def test_get_metrics_reporting(self):
        async def run_test():
            metrics_initial = self.cache.get_metrics()
            self.assertEqual(metrics_initial["cache_hits"], 0)
            self.assertEqual(metrics_initial["cache_misses"], 0)
            self.assertEqual(metrics_initial["hit_rate_pct"], 0.0)
            self.assertEqual(metrics_initial["cached_entries_count"], 0)

            # 1 miss + 1 set + 2 hits
            await self.cache.get("Query A")
            await self.cache.set("Query A", {"res": "A"})
            await self.cache.get("Query A")
            await self.cache.get("query a")

            metrics = self.cache.get_metrics()
            self.assertEqual(metrics["cache_hits"], 2)
            self.assertEqual(metrics["cache_misses"], 1)
            self.assertEqual(metrics["hit_rate_pct"], 66.67)
            self.assertEqual(metrics["cached_entries_count"], 1)

        asyncio.run(run_test())

    def test_whitespace_and_punctuation_normalization(self):
        async def run_test():
            q1 = "  Need   an  electrician???   NOW!!  "
            q2 = "need an electrician now"
            await self.cache.set(q1, {"matched": True})
            entry = await self.cache.get(q2)
            self.assertIsNotNone(entry)
            self.assertTrue(entry["matched"])

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
