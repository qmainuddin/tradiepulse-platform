import logging
from typing import Dict, Any, Tuple
from src.schemas.state import AgentState, TradeType, ChatMessage
from src.schemas.schemas import IntakeClassification, LocationExtraction, MatchConfirmation, AgentTurnResponse
from src.agent.gates import TypedSchemaGate
from src.cache.prompt_caching import construct_cached_prompt
from src.cache.semantic_cache import SemanticCache
from src.cache.bounded_history import BoundedHistoryManager
from src.cache.budget_governor import TokenBudgetGovernor
from src.rag.interaction_logger import InteractionLogger
from src.rag.session_rag import SessionRAGStore
from src.rag.broker import EventPublisher
from src.rag.matching_client import SpatialMatchingClient
from src.providers.router import MultiModelRouter

log = logging.getLogger(__name__)

class TradiePulseAgentWorkflow:
    """
    Deterministic conversational agent state machine.
    Nodes: intake -> clarify -> classify_trade -> extract_location -> retrieve_rag -> propose_match -> confirm -> handoff
    """

    def __init__(
        self,
        router: MultiModelRouter,
        semantic_cache: SemanticCache,
        history_manager: BoundedHistoryManager,
        budget_governor: TokenBudgetGovernor,
        interaction_logger: InteractionLogger,
        rag_store: SessionRAGStore,
        event_publisher: EventPublisher,
        matching_client: SpatialMatchingClient
    ):
        self.router = router
        self.semantic_cache = semantic_cache
        self.history_manager = history_manager
        self.budget_governor = budget_governor
        self.interaction_logger = interaction_logger
        self.rag_store = rag_store
        self.event_publisher = event_publisher
        self.matching_client = matching_client

    async def execute_turn(self, state: AgentState) -> AgentTurnResponse:
        user_input = state.current_user_input.strip()
        state.step_history.append("intake")

        # 1. Check Semantic Cache
        cached_entry = await self.semantic_cache.get(user_input)
        if cached_entry:
            state.cache_hit = True
            log.info("Returning semantic cache hit for session %s", state.session_id)
            return AgentTurnResponse(
                message=cached_entry.get("message", ""),
                stage=cached_entry.get("stage", "propose_match"),
                trade=TradeType(cached_entry.get("trade")) if cached_entry.get("trade") else None,
                location=cached_entry.get("location"),
                matched_tradies=cached_entry.get("matched_tradies", []),
                cache_hit=True,
                tokens_used=0,
                estimated_cost_usd=0.0
            )

        # 2. Bounded History & Token Budget
        verbatim_msgs, rolling_summary = self.history_manager.process_history(state.messages)
        self.budget_governor.check_request_budget(len(user_input) * 2)

        # 3. Retrieve RAG context first
        rag_snippets = await self.rag_store.retrieve_similar_context(user_input)
        state.rag_context = rag_snippets

        # 4. Classify Trade via Typed Schema Gate
        stable_prefix, messages = construct_cached_prompt(user_input, rag_snippets, rolling_summary)
        llm_res = await self.router.complete(messages, system_prefix=stable_prefix, response_model=IntakeClassification)
        
        state.tokens_in += llm_res.tokens_in
        state.tokens_out += llm_res.tokens_out
        state.estimated_cost_usd += llm_res.cost_usd
        self.budget_governor.record_usage(llm_res.tokens_in, llm_res.tokens_out, llm_res.cost_usd)

        classification, was_repaired = await TypedSchemaGate.parse_and_validate(
            llm_res.content,
            IntakeClassification,
            router=self.router,
            messages=messages
        )

        # Handle ambiguous classification -> deterministic clarify node
        if classification is None or classification.is_ambiguous or classification.trade is None:
            state.step_history.append("clarify")
            clarification_msg = classification.clarification_needed if (classification and classification.clarification_needed) \
                else "Could you please clarify what needs fixing? (For example: leaking tap, faulty power point, or car engine issue)"
            
            await self.interaction_logger.log_interaction(
                state.session_id, user_input, stable_prefix, llm_res.model,
                clarification_msg, llm_res.tokens_in, llm_res.tokens_out, 150, False, llm_res.cost_usd
            )
            return AgentTurnResponse(
                message=clarification_msg,
                stage="clarify",
                tokens_used=state.tokens_in + state.tokens_out,
                estimated_cost_usd=state.estimated_cost_usd
            )

        state.trade = classification.trade
        state.problem_summary = classification.problem_summary
        state.step_history.append("classify_trade")

        # 5. Extract Location
        loc_res = await self.router.complete(messages, system_prefix=stable_prefix, response_model=LocationExtraction)
        loc_data, _ = await TypedSchemaGate.parse_and_validate(
            loc_res.content,
            LocationExtraction,
            router=self.router,
            messages=messages
        )

        state.location_name = loc_data.location_name if loc_data else "Christchurch"
        state.latitude = loc_data.latitude if (loc_data and loc_data.latitude) else -43.5321
        state.longitude = loc_data.longitude if (loc_data and loc_data.longitude) else 172.6362
        state.step_history.append("extract_location")

        # 6. Spatial Nearest-Qualified Matching (PostGIS engine)
        state.step_history.append("propose_match")
        candidates = await self.matching_client.find_nearest_qualified(
            trade=state.trade,
            latitude=state.latitude,
            longitude=state.longitude
        )
        state.matched_tradies = candidates

        # Format proposal response
        if candidates:
            top_tradie = candidates[0]
            proposal_msg = f"I found {len(candidates)} verified {state.trade.value}s near {state.location_name}. Top recommendation: **{top_tradie.business_name}** ({top_tradie.rating_avg}★, {round(top_tradie.distance_meters / 1000, 1)} km away). Would you like to connect?"
        else:
            proposal_msg = f"We have registered your {state.trade.value} request for {state.location_name}. Our dispatch team is finding an available specialist now."

        # Cache response
        await self.semantic_cache.set(user_input, {
            "message": proposal_msg,
            "stage": "propose_match",
            "trade": state.trade.value if state.trade else None,
            "location": state.location_name,
            "matched_tradies": [c.model_dump() for c in candidates]
        })

        # Publish session event
        await self.event_publisher.publish_session_completed(
            state.session_id, user_input, state.trade.value, state.location_name
        )

        await self.interaction_logger.log_interaction(
            state.session_id, user_input, stable_prefix, llm_res.model,
            proposal_msg, state.tokens_in, state.tokens_out, 200, False, state.estimated_cost_usd
        )

        return AgentTurnResponse(
            message=proposal_msg,
            stage="propose_match",
            trade=state.trade,
            location=state.location_name,
            matched_tradies=[c.model_dump() for c in candidates],
            cache_hit=False,
            tokens_used=state.tokens_in + state.tokens_out,
            estimated_cost_usd=state.estimated_cost_usd
        )
