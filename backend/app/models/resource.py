"""
Resource model representing individual Azure resources.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False, index=True)  # VM, Storage Account, etc.
    sku = Column(String(100))  # Standard_D2_v3, Premium_LRS, etc.
    region = Column(String(100), nullable=False, index=True)
    
    # Foreign keys
    resource_group_id = Column(UUID(as_uuid=True), ForeignKey("resource_groups.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    
    # Resource metadata
    tags = Column(JSON, default=dict)
    properties = Column(JSON, default=dict)  # Size, tier, etc.
    
    # Status
    provisioning_state = Column(String(50), default="Succeeded")
    is_active = Column(Boolean, default=True)
    last_activity_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resource_group = relationship("ResourceGroup", back_populates="resources")
    service = relationship("Service", back_populates="resources")
    cost_records = relationship("CostUsage", back_populates="resource", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_resources_type_region", "resource_type", "region"),
        Index("ix_resources_service_active", "service_id", "is_active"),
    )
    
    def __repr__(self):
        return f"<Resource(name={self.name}, type={self.resource_type})>"
