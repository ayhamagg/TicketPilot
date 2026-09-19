from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services import ticket_service

router = APIRouter()


@router.get("/")
def get_statistics(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    return ticket_service.get_statistics(db)