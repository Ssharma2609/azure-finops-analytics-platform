"""
Health check endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "Azure Cost Intelligence Simulator"}


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check including database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ready" if db_status == "connected" else "not_ready",
        "database": db_status,
    }
