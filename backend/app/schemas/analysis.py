from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.ticket import CategoryEnum, PriorityEnum, AnalysisStatusEnum


class SimilarTicket(BaseModel):
    ticket_id: int
    title: str
    similarity_score: float


class AnalysisResponse(BaseModel):
    id: int
    ticket_id: int
    status: AnalysisStatusEnum
    category: Optional[CategoryEnum]
    category_confidence: Optional[float]
    summary: Optional[str]
    priority_suggestion: Optional[PriorityEnum]
    similar_tickets: Optional[list[SimilarTicket]]
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
    