"""
Service model representing Azure service types.
"""
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Service(Base):
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False)  # Compute, Storage, Database, etc.
    description = Column(String(500))
    base_unit_cost = Column(Float, default=0.0)  # Base cost per unit
    unit_type = Column(String(50))  # hours, GB, requests, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resources = relationship("Resource", back_populates="service")
    
    def __repr__(self):
        return f"<Service(name={self.name}, category={self.category})>"
