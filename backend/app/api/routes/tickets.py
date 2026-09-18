from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketListResponse
from app.models.ticket import StatusEnum, PriorityEnum, CategoryEnum, ChannelEnum
from app.services import ticket_service
from typing import Optional

router = APIRouter()


@router.post("/", response_model=TicketResponse, status_code=201)
def create_ticket(data: TicketCreate, db: Session = Depends(get_db)):
    """Create a new support ticket."""
    return ticket_service.create_ticket(db, data)


@router.get("/", response_model=TicketListResponse)
def list_tickets(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status: Optional[StatusEnum] = None,
    priority: Optional[PriorityEnum] = None,
    category: Optional[CategoryEnum] = None,
    channel: Optional[ChannelEnum] = None,
    search: Optional[str] = Query(default=None, max_length=100),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """List tickets with filtering, search, sorting and pagination."""
    return ticket_service.get_tickets(
        db=db,
        page=page,
        limit=limit,
        status=status,
        priority=priority,
        category=category,
        channel=channel,
        search=search,
        sort_by=sort_by,
        order=order,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get a single ticket by ID."""
    return ticket_service.get_ticket(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, data: TicketUpdate, db: Session = Depends(get_db)):
    """Update a ticket's fields."""
    return ticket_service.update_ticket(db, ticket_id, data)


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Delete a ticket."""
    ticket_service.delete_ticket(db, ticket_id)