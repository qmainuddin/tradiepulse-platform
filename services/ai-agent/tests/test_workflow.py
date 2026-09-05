import unittest
import asyncio
from src.schemas.state import AgentState, TradeType
from src.providers.openrouter import OpenRouterProvider
from src.providers.groq_provider import GroqProvider
from src.providers.router import MultiModelRouter
from src.cache.semantic_cache import SemanticCache
from src.cache.bounded_history import BoundedHistoryManager
from src.cache.budget_governor import TokenBudgetGovernor
from src.rag.interaction_logger import InteractionLogger
from src.rag.session_rag import SessionRAGStore
from src.rag.broker import EventPublisher, RAGSessionIngestConsumer
from src.rag.matching_client import SpatialMatchingClient
from src.agent.graph import TradiePulseAgentWorkflow

class TestTradiePulseWorkflow(unittest.TestCase):

    def setUp(self):
        self.openrouter = OpenRouterProvider(api_key="sk-or-mock-key")
        self.groq = GroqProvider(api_key="gsk_mock_key")
        self.router = MultiModelRouter(primary=self.openrouter, fallback=self.groq)
        self.semantic_cache = SemanticCache(similarity_threshold=0.92)
        self.history_manager = BoundedHistoryManager(max_verbatim_turns=4)
        self.budget_governor = TokenBudgetGovernor(token_ceiling=4096)
        self.interaction_logger = InteractionLogger()
        self.rag_store = SessionRAGStore()
        self.event_publisher = EventPublisher()
        self.matching_client = SpatialMatchingClient()

        self.workflow = TradiePulseAgentWorkflow(
            router=self.router,
            semantic_cache=self.semantic_cache,
            history_manager=self.history_manager,
            budget_governor=self.budget_governor,
            interaction_logger=self.interaction_logger,
            rag_store=self.rag_store,
            event_publisher=self.event_publisher,
            matching_client=self.matching_client
        )

    def test_full_plumber_matching_conversation(self):
        async def run_test():
            state = AgentState(
                session_id="session-test-01",
                customer_id="cust-123",
                current_user_input="My kitchen tap is leaking in Riccarton, Christchurch."
            )

            # Turn 1: Process user problem
            response = await self.workflow.execute_turn(state)

            # Assertions
            self.assertEqual(response.stage, "propose_match")
            self.assertEqual(response.trade, TradeType.PLUMBER)
            self.assertEqual(response.location, "Christchurch")
            self.assertGreaterEqual(len(response.matched_tradies), 1)
            self.assertIn("Dave Riccarton Plumbing", response.message)
            self.assertFalse(response.cache_hit)

            # Verify session completion event was published
            self.assertEqual(len(self.event_publisher.published_events), 1)
            self.assertEqual(self.event_publisher.published_events[0]["trade"], "plumber")

            # Turn 2: Exact same input -> Should trigger Semantic Cache HIT
            state2 = AgentState(
                session_id="session-test-02",
                customer_id="cust-456",
                current_user_input="my kitchen tap is leaking in riccarton, christchurch"
            )
            response2 = await self.workflow.execute_turn(state2)
            self.assertTrue(response2.cache_hit)
            self.assertEqual(response2.trade, TradeType.PLUMBER)

        asyncio.run(run_test())

    def test_electrician_matching_flow(self):
        async def run_test():
            state = AgentState(
                session_id="session-test-elec",
                customer_id="cust-elec-1",
                current_user_input="Need an electrician, power tripping in switchboard in Papanui."
            )
            response = await self.workflow.execute_turn(state)
            self.assertEqual(response.stage, "propose_match")
            self.assertEqual(response.trade, TradeType.ELECTRICIAN)
            self.assertEqual(response.location, "Christchurch")
            self.assertGreaterEqual(len(response.matched_tradies), 1)

        asyncio.run(run_test())

    def test_mechanic_matching_flow(self):
        async def run_test():
            state = AgentState(
                session_id="session-test-mech",
                customer_id="cust-mech-1",
                current_user_input="Car won't start, need a mechanic in Hornby, Christchurch."
            )
            response = await self.workflow.execute_turn(state)
            self.assertEqual(response.stage, "propose_match")
            self.assertEqual(response.trade, TradeType.MECHANIC)
            self.assertEqual(response.location, "Christchurch")
            self.assertGreaterEqual(len(response.matched_tradies), 1)

        asyncio.run(run_test())

    def test_ambiguous_request_triggers_clarification(self):
        async def run_test():
            state = AgentState(
                session_id="session-test-03",
                customer_id="cust-789",
                current_user_input="Something is broken at home."
            )

            response = await self.workflow.execute_turn(state)
            self.assertEqual(response.stage, "clarify")
            self.assertIsNone(response.trade)
            self.assertTrue("clarify" in response.message.lower() or "tell" in response.message.lower())

        asyncio.run(run_test())

    def test_workflow_budget_tracking_and_metrics(self):
        async def run_test():
            state = AgentState(
                session_id="session-metrics-01",
                customer_id="cust-metrics",
                current_user_input="Hot water cylinder leak in St Albans."
            )
            await self.workflow.execute_turn(state)
            metrics = self.budget_governor.get_metrics()
            self.assertGreater(metrics["total_tokens"], 0)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
