"""
Resource management API endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.resource_service import ResourceService
from app.schemas.resource import TopExpensiveResponse, ResourceDetail

router = APIRouter()


def get_resource_service(db: Session = Depends(get_db)) -> ResourceService:
    return ResourceService(db)


@router.get("/top-expensive", response_model=TopExpensiveResponse)
async def get_top_expensive_resources(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(10, ge=1, le=100, description="Number of resources to return"),
    subscription_ids: Optional[List[str]] = Query(None, description="Filter by subscription IDs"),
    service_names: Optional[List[str]] = Query(None, description="Filter by service names"),
    service: ResourceService = Depends(get_resource_service),
):
    """
    Get top expensive resources by total cost.
    
    Returns the highest-cost resources with detailed metrics.
    """
    return service.get_top_expensive_resources(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        subscription_ids=subscription_ids,
        service_names=service_names,
    )


@router.get("/{resource_id}", response_model=ResourceDetail)
async def get_resource_details(
    resource_id: str,
    service: ResourceService = Depends(get_resource_service),
):
    """
    Get detailed information about a specific resource.
    """
    resource = service.get_resource_details(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource
