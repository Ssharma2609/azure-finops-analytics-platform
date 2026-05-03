"""
Resource Group model representing Azure resource groups.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class ResourceGroup(Base):
    __tablename__ = "resource_groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    tags = Column(JSON, default=dict)  # {"env": "prod", "team": "platform"}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="resource_groups")
    resources = relationship("Resource", back_populates="resource_group", cascade="all, delete-orphan")
    
    # Composite unique constraint
    __table_args__ = (
        {"extend_existing": True},
    )
    
    def __repr__(self):
        return f"<ResourceGroup(name={self.name}, region={self.region})>"
