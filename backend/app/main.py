# TicketPilot - AI-Powered Customer Support Ticket Management System
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import tickets, statistics, analysis, github

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Customer Support Ticket Management System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(analysis.router, prefix="/api/tickets", tags=["analysis"])
app.include_router(github.router, prefix="/api/tickets", tags=["github"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])


@app.get("/health")
def health_check():
    """Simple endpoint to verify the API is running."""
    return {"status": "ok", "app": settings.APP_NAME}