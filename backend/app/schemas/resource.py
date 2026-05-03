"""
Resource-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID


class ResourceBase(BaseModel):
    """Base resource schema."""
    resource_id: str
    name: str
    resource_type: str
    sku: Optional[str] = None
    region: str
    tags: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class ResourceDetail(ResourceBase):
    """Detailed resource information."""
    id: UUID
    service_name: str
    service_category: str
    resource_group_name: str
    subscription_name: str
    subscription_id: str
    provisioning_state: str
    is_active: bool
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    last_activity_at: Optional[datetime] = None
    
    # Cost metrics
    total_cost: float = 0.0
    daily_avg_cost: float = 0.0
    cost_trend: str = "stable"  # increasing, decreasing, stable


class TopExpensiveResource(BaseModel):
    """Resource with high cost metrics."""
    resource_id: str
    name: str
    resource_type: str
    service_name: str
    region: str
    subscription_name: str
    resource_group: str
    total_cost: float
    daily_avg_cost: float
    usage_quantity: float
    cost_percentage: float
    tags: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class TopExpensiveResponse(BaseModel):
    """Response for top expensive resources API."""
    data: List[TopExpensiveResource]
    total_cost: float
    period_start: date
    period_end: date
    limit: int


class ResourceFilter(BaseModel):
    """Query parameters for resource filtering."""
    resource_types: Optional[List[str]] = None
    service_names: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    subscription_ids: Optional[List[str]] = None
    is_active: Optional[bool] = None
    tags: Optional[Dict[str, str]] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="total_cost")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
