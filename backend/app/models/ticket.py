from sqlalchemy import (
    Column, Integer, String, Text, Float,
    DateTime, Enum, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database.connection import Base


# --- Enums ---
# These define the allowed values for certain fields
# Using enums means the database will reject any invalid value

class ChannelEnum(str, enum.Enum):
    email = "email"
    website = "website"
    chat = "chat"
    phone = "phone"
    other = "other"


class StatusEnum(str, enum.Enum):
    open = "OPEN"
    in_progress = "IN_PROGRESS"
    resolved = "RESOLVED"
    closed = "CLOSED"


class PriorityEnum(str, enum.Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    urgent = "URGENT"


class CategoryEnum(str, enum.Enum):
    billing = "BILLING"
    technical = "TECHNICAL"
    account = "ACCOUNT"
    shipping = "SHIPPING"
    refund = "REFUND"
    security = "SECURITY"
    other = "OTHER"


class AnalysisStatusEnum(str, enum.Enum):
    pending = "PENDING"
    success = "SUCCESS"
    failed = "FAILED"


# --- Database Models ---

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False, index=True)
    customer_id = Column(String(100), nullable=True)
    channel = Column(Enum(ChannelEnum), nullable=False, default=ChannelEnum.other)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.open, index=True)
    priority = Column(Enum(PriorityEnum), nullable=False, default=PriorityEnum.medium, index=True)
    category = Column(Enum(CategoryEnum), nullable=True, index=True)
    github_issue_id = Column(Integer, nullable=True)
    github_issue_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship — one ticket can have many analysis attempts
    analyses = relationship("AIAnalysis", back_populates="ticket", cascade="all, delete-orphan")


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    status = Column(Enum(AnalysisStatusEnum), nullable=False, default=AnalysisStatusEnum.pending)
    category = Column(Enum(CategoryEnum), nullable=True)
    category_confidence = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    priority_suggestion = Column(Enum(PriorityEnum), nullable=True)
    similar_tickets = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to the ticket
    ticket = relationship("Ticket", back_populates="analyses")