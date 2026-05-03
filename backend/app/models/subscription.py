"""
Subscription model representing Azure subscriptions.
"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    state = Column(String(50), default="Active")
    environment = Column(String(50), default="production")  # production, development, test
    owner_email = Column(String(255))
    budget_limit = Column(String(50))  # Monthly budget
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resource_groups = relationship("ResourceGroup", back_populates="subscription", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Subscription(id={self.subscription_id}, name={self.name})>"
