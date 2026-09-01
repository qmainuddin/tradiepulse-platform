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


if __name__ == "__main__":
    unittest.main()
