from pydantic import BaseModel, Field
from typing import List, Optional

class ShotPredictionRequest(BaseModel):
    x: float = Field(..., description="Pitch coordinate X (0 to 120)")
    y: float = Field(..., description="Pitch coordinate Y (0 to 80)")
    body_part: str = Field("Foot", description="Body part used: Foot, Head, Other")
    technique: str = Field("Normal", description="Technique: Normal, Volley, Half Volley, Lob")
    shot_type: str = Field("Open Play", description="Type: Open Play, Free Kick, Penalty")
    under_pressure: bool = Field(False, description="Whether the player was under defensive pressure")

class AssistantRequest(BaseModel):
    query: str = Field(..., description="Tactical question for the AI Assistant")

class Citation(BaseModel):
    source_id: int
    citation: str
    snippet: str

class AssistantResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
