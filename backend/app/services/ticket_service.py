from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.ticket import Ticket, StatusEnum, PriorityEnum, CategoryEnum, ChannelEnum
from app.schemas.ticket import TicketCreate, TicketUpdate
from fastapi import HTTPException


def create_ticket(db: Session, data: TicketCreate) -> Ticket:
    """Create a new ticket and save it to the database."""
    ticket = Ticket(
        title=data.title,
        description=data.description,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        customer_id=data.customer_id,
        channel=data.channel,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: int) -> Ticket:
    """Get a single ticket by ID. Raises 404 if not found."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


def get_tickets(
    db: Session,
    page: int = 1,
    limit: int = 20,
    status: StatusEnum = None,
    priority: PriorityEnum = None,
    category: CategoryEnum = None,
    channel: ChannelEnum = None,
    search: str = None,
    sort_by: str = "created_at",
    order: str = "desc",
):
    """Get a paginated, filtered, searchable list of tickets."""
    query = db.query(Ticket)

    # Filtering
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if channel:
        query = query.filter(Ticket.channel == channel)

    # Search across multiple fields
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Ticket.title.ilike(search_term),
                Ticket.description.ilike(search_term),
                Ticket.customer_name.ilike(search_term),
                Ticket.customer_email.ilike(search_term),
            )
        )

    # Total count before pagination
    total = query.count()

    # Sorting
    sort_column = getattr(Ticket, sort_by, Ticket.created_at)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    offset = (page - 1) * limit
    tickets = query.offset(offset).limit(limit).all()

    total_pages = (total + limit - 1) // limit

    return {
        "items": tickets,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
    }


def update_ticket(db: Session, ticket_id: int, data: TicketUpdate) -> Ticket:
    """Update specific fields on a ticket."""
    ticket = get_ticket(db, ticket_id)

    # Only update fields that were actually provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket_id: int) -> None:
    """Delete a ticket by ID."""
    ticket = get_ticket(db, ticket_id)
    db.delete(ticket)
    db.commit()


def get_statistics(db: Session) -> dict:
    """Get dashboard statistics."""
    total = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == StatusEnum.open).count()
    high_priority = db.query(Ticket).filter(Ticket.priority == PriorityEnum.high).count()
    urgent = db.query(Ticket).filter(Ticket.priority == PriorityEnum.urgent).count()
    resolved = db.query(Ticket).filter(Ticket.status == StatusEnum.resolved).count()

    # Category distribution
    category_counts = (
        db.query(Ticket.category, func.count(Ticket.id))
        .group_by(Ticket.category)
        .all()
    )

    return {
        "total_tickets": total,
        "open_tickets": open_tickets,
        "high_priority_tickets": high_priority,
        "urgent_tickets": urgent,
        "resolved_tickets": resolved,
        "category_distribution": {
            str(cat.value) if cat else "uncategorized": count
            for cat, count in category_counts
        },
    }