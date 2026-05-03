

"""
Cost analysis API endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.cost_service import CostService
from app.schemas.cost import (
    CostSummary,
    CostTrendResponse,
    ServiceCostResponse,
    SubscriptionCostResponse,
)

router = APIRouter()


def get_cost_service(db: Session = Depends(get_db)) -> CostService:
    return CostService(db)


@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    start_date: Optional[date] = Query(None, description="Start date (defaults to 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to today)"),
    subscription_ids: Optional[List[str]] = Query(None, description="Filter by subscription IDs"),
    service_names: Optional[List[str]] = Query(None, description="Filter by service names"),
    service: CostService = Depends(get_cost_service),
):
    """
    Get cost summary with aggregated metrics.
    
    Returns total cost, average daily cost, min/max daily costs,
    and comparison with previous period.
    """
    return service.get_cost_summary(
        start_date=start_date,
        end_date=end_date,
        subscription_ids=subscription_ids,
        service_names=service_names,
    )


@router.get("/trend", response_model=CostTrendResponse)
async def get_cost_trend(
    days: int = Query(30, description="Number of days"),
    subscription_ids: Optional[List[str]] = Query(
        None,
        description="Filter by subscription IDs"
    ),
    service: CostService = Depends(get_cost_service),
):
    end = date.today()
    start = end - timedelta(days=days)

    return service.get_cost_trend(
        start_date=start,
        end_date=end,
        subscription_ids=subscription_ids,
    )


@router.get("/by-service", response_model=ServiceCostResponse)
async def get_cost_by_service(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    subscription_ids: Optional[List[str]] = Query(None, description="Filter by subscription IDs"),
    service: CostService = Depends(get_cost_service),
):
    """
    Get cost breakdown by Azure service.
    
    Returns aggregated costs per service with percentage of total.
    """
    return service.get_cost_by_service(
        start_date=start_date,
        end_date=end_date,
        subscription_ids=subscription_ids,
    )


@router.get("/by-subscription", response_model=SubscriptionCostResponse)
async def get_cost_by_subscription(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    service: CostService = Depends(get_cost_service),
):
    """
    Get cost breakdown by subscription.
    
    Returns aggregated costs per subscription with budget utilization.
    """
    return service.get_cost_by_subscription(
        start_date=start_date,
        end_date=end_date,
    )
