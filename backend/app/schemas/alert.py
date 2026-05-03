"""
Alert and anomaly-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    COST_SPIKE = "cost_spike"
    BUDGET_EXCEEDED = "budget_exceeded"
    UNUSUAL_ACTIVITY = "unusual_activity"
    IDLE_RESOURCE = "idle_resource"
    ANOMALY_DETECTED = "anomaly_detected"


class AnomalyDetail(BaseModel):
    """Details of a detected anomaly."""
    id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    
    # Context
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    subscription_id: Optional[str] = None
    service_name: Optional[str] = None
    
    # Metrics
    detected_value: float
    expected_value: float
    deviation_percent: float
    confidence_score: float = Field(..., ge=0, le=1)
    
    # Time
    detected_at: datetime
    anomaly_date: date
    
    # Status
    is_acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class AnomalyResponse(BaseModel):
    """Response for anomaly alerts API."""
    data: List[AnomalyDetail]
    total_count: int
    unacknowledged_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class AlertStats(BaseModel):
    """Alert statistics summary."""
    total_alerts: int
    by_severity: dict
    by_type: dict
    trend: str  # increasing, decreasing, stable
