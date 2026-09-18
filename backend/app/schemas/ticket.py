from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from app.models.ticket import StatusEnum, PriorityEnum, CategoryEnum, ChannelEnum


# --- Request Schemas (what we receive) ---

class TicketCreate(BaseModel):
    title: str
    description: str
    customer_name: str
    customer_email: EmailStr
    customer_id: Optional[str] = None
    channel: ChannelEnum = ChannelEnum.other

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters")
        if len(v) > 255:
            raise ValueError("Title must be less than 255 characters")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_must_not_be_empty(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters")
        return v.strip()

    @field_validator("customer_name")
    @classmethod
    def name_must_not_be_empty(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Customer name must be at least 2 characters")
        return v.strip()


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    category: Optional[CategoryEnum] = None


# --- Response Schemas (what we return) ---

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    customer_name: str
    customer_email: str
    customer_id: Optional[str]
    channel: ChannelEnum
    status: StatusEnum
    priority: PriorityEnum
    category: Optional[CategoryEnum]
    github_issue_id: Optional[int]
    github_issue_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    page: int
    limit: int
    total: int
    total_pages: int