from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.ticket import AIAnalysis, AnalysisStatusEnum, CategoryEnum, PriorityEnum
from app.schemas.analysis import AnalysisResponse
from app.services import ticket_service
from app.services import ai_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def run_analysis(ticket_id: int, db: Session) -> AIAnalysis:
    """Core analysis logic — used by both analyze and retry endpoints."""

    # Step 1: Get the ticket
    ticket = ticket_service.get_ticket(db, ticket_id)

    # Step 2: Create a PENDING analysis record immediately
    analysis = AIAnalysis(
        ticket_id=ticket_id,
        status=AnalysisStatusEnum.pending,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    try:
        # Step 3: Send to Claude API
        result = ai_service.analyze_ticket(ticket.title, ticket.description)

        # Step 4: Get similar tickets (exclude current ticket)
        recent_tickets = db.query(ticket_service.Ticket).filter(
            ticket_service.Ticket.id != ticket_id
        ).order_by(ticket_service.Ticket.created_at.desc()).limit(20).all()

        existing = [
            {"id": t.id, "title": t.title, "description": t.description}
            for t in recent_tickets
        ]

        new_ticket_text = f"{ticket.title} {ticket.description}"
        similar = ai_service.find_similar_tickets(new_ticket_text, existing)

        # Step 5: Update analysis with results
        analysis.status = AnalysisStatusEnum.success
        analysis.category = CategoryEnum(result["category"])
        analysis.category_confidence = result["category_confidence"]
        analysis.summary = result["summary"]
        analysis.priority_suggestion = PriorityEnum(result["priority_suggestion"])
        analysis.similar_tickets = similar

        # Step 6: Update the ticket's category with AI result
        ticket.category = CategoryEnum(result["category"])

        db.commit()
        db.refresh(analysis)
        logger.info(f"Analysis successful for ticket {ticket_id}")

    except Exception as e:
        # Step 7: If anything fails, mark analysis as failed
        analysis.status = AnalysisStatusEnum.failed
        analysis.error_message = str(e)
        db.commit()
        db.refresh(analysis)
        logger.error(f"Analysis failed for ticket {ticket_id}: {e}")

    return analysis


@router.post("/{ticket_id}/analyze", response_model=AnalysisResponse, status_code=201)
def analyze_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Run AI analysis on a ticket."""
    return run_analysis(ticket_id, db)


@router.post("/{ticket_id}/analyze/retry", response_model=AnalysisResponse, status_code=201)
def retry_analysis(ticket_id: int, db: Session = Depends(get_db)):
    """Retry AI analysis on a ticket that previously failed."""
    # Verify ticket exists first
    ticket_service.get_ticket(db, ticket_id)
    return run_analysis(ticket_id, db)