"""
Analytics and forecast-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from enum import Enum


class ForecastDataPoint(BaseModel):
    """Single forecast data point."""
    date: date
    predicted_cost: float
    lower_bound: float
    upper_bound: float
    confidence_level: float = Field(default=0.95)
    
    class Config:
        from_attributes = True


class ForecastResponse(BaseModel):
    """Response for forecast API."""
    historical_data: List[dict]  # Last 30 days actual
    forecast_data: List[ForecastDataPoint]
    model_used: str
    accuracy_metrics: dict
    total_forecasted_cost: float
    average_daily_forecast: float
    trend: str  # increasing, decreasing, stable
    generated_at: str


class RecommendationType(str, Enum):
    RIGHTSIZING = "rightsizing"
    IDLE_RESOURCE = "idle_resource"
    RESERVED_INSTANCE = "reserved_instance"
    SPOT_INSTANCE = "spot_instance"
    STORAGE_OPTIMIZATION = "storage_optimization"
    DELETE_UNUSED = "delete_unused"
    REGION_OPTIMIZATION = "region_optimization"


class RecommendationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recommendation(BaseModel):
    """Cost optimization recommendation."""
    id: str
    type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    
    # Impact
    estimated_monthly_savings: float
    estimated_annual_savings: float
    confidence_score: float = Field(..., ge=0, le=1)
    
    # Resource context
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    resource_type: Optional[str] = None
    service_name: Optional[str] = None
    subscription_id: Optional[str] = None
    
    # Action
    action_required: str
    implementation_effort: str  # low, medium, high
    
    # Metadata
    generated_at: str
    valid_until: Optional[str] = None
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Response for recommendations API."""
    data: List[Recommendation]
    total_count: int
    total_potential_savings: float
    by_type: dict
    by_priority: dict
