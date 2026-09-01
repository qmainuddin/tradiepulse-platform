import uuid
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import settings
from src.schemas.state import AgentState, ChatMessage, TradeType
from src.schemas.schemas import AgentTurnResponse
from src.channels.channel import TextChannel
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

app = FastAPI(
    title="TradiePulse AI Agent Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
openrouter = OpenRouterProvider(api_key=settings.openrouter_api_key, default_model=settings.openrouter_default_model)
groq = GroqProvider(api_key=settings.groq_api_key, default_model=settings.groq_fallback_model)
router = MultiModelRouter(primary=openrouter, fallback=groq)

semantic_cache = SemanticCache(similarity_threshold=settings.semantic_cache_threshold)
history_manager = BoundedHistoryManager(max_verbatim_turns=4)
budget_governor = TokenBudgetGovernor(token_ceiling=settings.token_ceiling_per_request)
interaction_logger = InteractionLogger(qdrant_url=settings.qdrant_url)
rag_store = SessionRAGStore(qdrant_url=settings.qdrant_url)
event_publisher = EventPublisher(rabbitmq_url=settings.rabbitmq_url)
rag_consumer = RAGSessionIngestConsumer(rag_store=rag_store)
matching_client = SpatialMatchingClient(database_url=settings.database_url)

workflow = TradiePulseAgentWorkflow(
    router=router,
    semantic_cache=semantic_cache,
    history_manager=history_manager,
    budget_governor=budget_governor,
    interaction_logger=interaction_logger,
    rag_store=rag_store,
    event_publisher=event_publisher,
    matching_client=matching_client
)

class ChatTurnRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    media_urls: List[str] = []

@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "ai-agent",
        "environment": settings.environment
    }

@app.get("/metrics")
def get_metrics():
    cache_m = semantic_cache.get_metrics()
    budget_m = budget_governor.get_metrics()
    return {
        **cache_m,
        **budget_m
    }

@app.post("/api/chat", response_model=AgentTurnResponse)
async def process_chat(
    req: ChatTurnRequest,
    x_user_id: Optional[str] = Header(default="anonymous-customer"),
    x_correlation_id: Optional[str] = Header(default=None)
):
    session_id = req.session_id or str(uuid.uuid4())
    
    state = AgentState(
        session_id=session_id,
        customer_id=x_user_id,
        current_user_input=req.message,
        media_urls=req.media_urls
    )

    response = await workflow.execute_turn(state)
    return response

@app.post("/api/chat/upload")
async def upload_chat_image(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    # Validate MIME type (JPEG/PNG/WEBP) and size (<= 10MB)
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid image type. Allowed: JPEG, PNG, WEBP.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image exceeds maximum 10MB limit.")

    # Storage URL mock / Supabase upload reference
    mock_url = f"https://tradiepulse-media.supabase.co/chat/{session_id}/{file.filename}"
    return {
        "url": mock_url,
        "filename": file.filename,
        "size_bytes": len(content)
    }
