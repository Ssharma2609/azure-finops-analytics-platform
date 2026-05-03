"""
Cost-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID


class CostSummary(BaseModel):
    """Summary of cost metrics."""
    total_cost: float = Field(..., description="Total cost for the period")
    average_daily_cost: float = Field(..., description="Average daily cost")
    min_daily_cost: float = Field(..., description="Minimum daily cost")
    max_daily_cost: float = Field(..., description="Maximum daily cost")
    total_days: int = Field(..., description="Number of days in the period")
    currency: str = Field(default="USD")
    period_start: date
    period_end: date
    cost_change_percent: Optional[float] = Field(None, description="Percent change from previous period")
    
    class Config:
        from_attributes = True


class DailyCost(BaseModel):
    """Daily cost data point."""
    date: date
    cost: float
    usage_quantity: float
    resource_count: int
    
    class Config:
        from_attributes = True


class CostTrendResponse(BaseModel):
    """Response for cost trend API."""
    data: List[DailyCost]
    total_records: int
    period_start: date
    period_end: date


class ServiceCost(BaseModel):
    """Cost breakdown by service."""
    service_name: str
    service_category: str
    total_cost: float
    percentage_of_total: float
    resource_count: int
    avg_cost_per_resource: float
    
    class Config:
        from_attributes = True


class ServiceCostResponse(BaseModel):
    """Response for cost by service API."""
    data: List[ServiceCost]
    total_cost: float
    period_start: date
    period_end: date


class SubscriptionCost(BaseModel):
    """Cost breakdown by subscription."""
    subscription_id: str
    subscription_name: str
    environment: str
    total_cost: float
    percentage_of_total: float
    resource_count: int
    budget_limit: Optional[float] = None
    budget_utilization: Optional[float] = None
    
    class Config:
        from_attributes = True


class SubscriptionCostResponse(BaseModel):
    """Response for cost by subscription API."""
    data: List[SubscriptionCost]
    total_cost: float
    period_start: date
    period_end: date


class CostFilter(BaseModel):
    """Query parameters for cost filtering."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    subscription_ids: Optional[List[str]] = None
    service_names: Optional[List[str]] = None
    resource_groups: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    environments: Optional[List[str]] = None
    min_cost: Optional[float] = None
    max_cost: Optional[float] = None
