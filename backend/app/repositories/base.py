"""
Base repository with common CRUD operations.
"""
from typing import TypeVar, Generic, Type, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common database operations."""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """Count total records."""
        return self.db.query(func.count(self.model.id)).scalar()
    
    def create(self, obj_data: dict) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def create_many(self, objects_data: List[dict]) -> List[ModelType]:
        """Create multiple records efficiently."""
        db_objects = [self.model(**data) for data in objects_data]
        self.db.add_all(db_objects)
        self.db.commit()
        return db_objects
    
    def update(self, id: UUID, obj_data: dict) -> Optional[ModelType]:
        """Update an existing record."""
        db_obj = self.get_by_id(id)
        if db_obj:
            for key, value in obj_data.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
