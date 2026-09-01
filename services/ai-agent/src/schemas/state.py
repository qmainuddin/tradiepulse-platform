from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TradeType(str, Enum):
    PLUMBER = "plumber"
    ELECTRICIAN = "electrician"
    MECHANIC = "mechanic"

class ChatMessage(BaseModel):
    role: str # 'user', 'assistant', 'system'
    content: str
    media_urls: List[str] = Field(default_factory=list)
    timestamp: Optional[str] = None

class CandidateTradie(BaseModel):
    tradie_id: str
    name: str
    business_name: str
    trade: TradeType
    distance_meters: float
    service_radius_km: int
    rating_avg: float
    rating_count: int
    hourly_rate_nzd: Optional[float] = None
    phone: Optional[str] = None

class AgentState(BaseModel):
    session_id: str
    customer_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    current_user_input: str = ""
    media_urls: List[str] = Field(default_factory=list)
    
    # Classification & Entity Extraction
    trade: Optional[TradeType] = None
    trade_confidence: float = 0.0
    problem_summary: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # RAG & Matching
    rag_context: List[str] = Field(default_factory=list)
    matched_tradies: List[CandidateTradie] = Field(default_factory=list)
    selected_tradie_id: Optional[str] = None
    
    # Control Flow State
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    is_confirmed: bool = False
    is_handed_off: bool = False
    
    # Observability & Metrics
    tokens_in: int = 0
    tokens_out: int = 0
    estimated_cost_usd: float = 0.0
    cache_hit: bool = False
    circuit_breaker_active: bool = False
    step_history: List[str] = Field(default_factory=list)
