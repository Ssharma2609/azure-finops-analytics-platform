"""
Alert and anomaly API endpoints.
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import AnomalyResponse, AlertSeverity

router = APIRouter()


def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    return AlertService(db)


@router.get("/anomalies", response_model=AnomalyResponse)
async def get_anomalies(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    service: AlertService = Depends(get_alert_service),
):
    """
    Get detected cost anomalies.
    
    Uses statistical analysis to detect unusual cost patterns.
    """
    return service.get_anomalies(
        start_date=start_date,
        end_date=end_date,
        severity=severity,
    )
