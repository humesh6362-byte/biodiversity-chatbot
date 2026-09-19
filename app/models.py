from typing import List, Optional
from pydantic import BaseModel, Field


class StructuredInput(BaseModel):
    """Optional structured environmental data the user (or an upstream system) can supply
    directly, instead of / in addition to free text. All fields optional — the extractor
    also pulls these out of free text when the user just types a sentence."""

    soil_organic_carbon_pct: Optional[float] = None
    soil_ph: Optional[float] = None
    rainfall: Optional[str] = None  # e.g. "low", "high", or a mm/year figure as text
    land_use_type: Optional[str] = None  # e.g. "monoculture wheat", "agroforestry"
    crop: Optional[str] = None
    region: Optional[str] = None
    temperature: Optional[str] = None
    pollution_level: Optional[str] = None
    deforestation_rate: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    structured_input: Optional[StructuredInput] = None


class RetrievedSource(BaseModel):
    text: str
    source: str
    score: float


class Recommendation(BaseModel):
    action: str
    reasoning: str
    impacted_metrics: List[str]
    estimated_improvement: Optional[str] = None
    time_horizon: str  # short | medium | long
    confidence: Optional[str] = None  # low | medium | high
    reference: str


class ChatResponse(BaseModel):
    session_id: str
    reply_type: str  # "clarifying_question" | "recommendation"
    message: str
    follow_up_question: Optional[str] = None
    known_variables: dict
    recommendations: List[Recommendation] = Field(default_factory=list)
    sources: List[RetrievedSource] = Field(default_factory=list)
