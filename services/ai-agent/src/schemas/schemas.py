from typing import Optional, List
from pydantic import BaseModel, Field
from src.schemas.state import TradeType

class IntakeClassification(BaseModel):
    trade: Optional[TradeType] = Field(description="Classified trade: plumber, electrician, or mechanic")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    problem_summary: str = Field(description="Concise 1-sentence summary of the customer problem")
    is_ambiguous: bool = Field(description="True if the user input is underspecified or spans multiple trades")
    clarification_needed: Optional[str] = Field(default=None, description="Clarifying question to ask if ambiguous")

class LocationExtraction(BaseModel):
    location_name: str = Field(description="Suburb or city in New Zealand e.g. Riccarton, Christchurch, Rangiora")
    latitude: Optional[float] = Field(default=None, description="Approximate latitude if resolvable")
    longitude: Optional[float] = Field(default=None, description="Approximate longitude if resolvable")
    is_canterbury_region: bool = Field(default=True, description="True if in Christchurch / Canterbury area")

class MatchConfirmation(BaseModel):
    is_confirmed: bool = Field(description="True if customer explicitly confirms booking/connecting with the matched tradie")
    selected_tradie_id: Optional[str] = Field(default=None, description="ID of the tradie chosen by the user")
    user_notes: Optional[str] = Field(default=None, description="Any specific timing or access notes from the customer")

class AgentTurnResponse(BaseModel):
    message: str
    stage: str
    trade: Optional[TradeType] = None
    location: Optional[str] = None
    matched_tradies: List[dict] = Field(default_factory=list)
    cache_hit: bool = False
    tokens_used: int = 0
    estimated_cost_usd: float = 0.0
