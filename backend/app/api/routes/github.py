from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services import ticket_service, github_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{ticket_id}/github-issue", status_code=201)
def create_github_issue(ticket_id: int, db: Session = Depends(get_db)):
    """Convert a support ticket into a GitHub Issue."""

    # Step 1: Get the ticket
    ticket = ticket_service.get_ticket(db, ticket_id)

    # Step 2: Check it hasn't already been converted
    if ticket.github_issue_id:
        raise HTTPException(
            status_code=400,
            detail=f"Ticket {ticket_id} already has a GitHub issue: {ticket.github_issue_url}"
        )

    # Step 3: Create the GitHub issue
    try:
        result = github_service.create_github_issue(ticket)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"GitHub issue creation failed for ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=502,
            detail="GitHub API is unavailable. The ticket was not affected."
        )

    # Step 4: Save the GitHub issue info to the ticket
    ticket.github_issue_id = result["github_issue_id"]
    ticket.github_issue_url = result["github_issue_url"]
    db.commit()
    db.refresh(ticket)

    logger.info(f"GitHub issue created for ticket {ticket_id}: {result['github_issue_url']}")

    return {
        "ticket_id": ticket_id,
        "github_issue_id": result["github_issue_id"],
        "github_issue_url": result["github_issue_url"],
        "status": "CREATED"
    }