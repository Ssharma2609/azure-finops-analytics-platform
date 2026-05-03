"""
Analytics and forecasting API endpoints.
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import ForecastResponse, RecommendationResponse

router = APIRouter()


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    forecast_days: int = Query(7, ge=1, le=30, description="Days to forecast"),
    history_days: int = Query(60, ge=14, le=180, description="Historical days for model"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get cost forecast for upcoming days.
    
    Uses historical data to predict future costs with confidence intervals.
    """
    return service.get_forecast(
        forecast_days=forecast_days,
        history_days=history_days,
    )


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get cost optimization recommendations.
    
    Analyzes usage patterns to suggest cost-saving opportunities.
    """
    return service.get_recommendations(
        start_date=start_date,
        end_date=end_date,
    )
