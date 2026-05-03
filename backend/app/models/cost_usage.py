"""
Cost and Usage model for tracking daily resource costs.
"""
from sqlalchemy import Column, Float, DateTime, ForeignKey, String, Date, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class CostUsage(Base):
    __tablename__ = "cost_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False, index=True)
    
    # Time dimension
    usage_date = Column(Date, nullable=False, index=True)
    
    # Cost metrics
    cost = Column(Float, nullable=False, default=0.0)
    pretax_cost = Column(Float, default=0.0)
    usage_quantity = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    
    # Billing details
    billing_currency = Column(String(10), default="USD")
    meter_category = Column(String(100))
    meter_subcategory = Column(String(100))
    meter_name = Column(String(255))
    
    # Usage details
    consumed_quantity = Column(Float, default=0.0)
    resource_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resource = relationship("Resource", back_populates="cost_records")
    
    # Indexes for analytics queries
    __table_args__ = (
        Index("ix_cost_usage_date_resource", "usage_date", "resource_id"),
        Index("ix_cost_usage_date_cost", "usage_date", "cost"),
    )
    
    def __repr__(self):
        return f"<CostUsage(date={self.usage_date}, cost={self.cost})>"
