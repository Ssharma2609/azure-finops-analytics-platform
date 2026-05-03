"""
Repository for resource data operations.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, cast, Text
from uuid import UUID

from app.repositories.base import BaseRepository
from app.models.resource import Resource
from app.models.cost_usage import CostUsage
from app.models.service import Service
from app.models.resource_group import ResourceGroup
from app.models.subscription import Subscription


class ResourceRepository(BaseRepository[Resource]):
    """Repository for resource operations."""
    
    def __init__(self, db: Session):
        super().__init__(Resource, db)
    
    def get_top_expensive_resources(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10,
        subscription_ids: Optional[List[str]] = None,
        service_names: Optional[List[str]] = None,
    ) -> List[dict]:
        """Get top expensive resources by total cost."""
        days = (end_date - start_date).days + 1
        
        query = (
            self.db.query(
                Resource.resource_id,
                Resource.name,
                Resource.resource_type,
                Resource.region,
                cast(Resource.tags, Text).label("tags"),
                Service.name.label("service_name"),
                Subscription.name.label("subscription_name"),
                ResourceGroup.name.label("resource_group"),
                func.sum(CostUsage.cost).label("total_cost"),
                func.sum(CostUsage.usage_quantity).label("usage_quantity"),
            )
            .join(CostUsage, Resource.id == CostUsage.resource_id)
            .join(Service, Resource.service_id == Service.id)
            .join(ResourceGroup, Resource.resource_group_id == ResourceGroup.id)
            .join(Subscription, ResourceGroup.subscription_id == Subscription.id)
            .filter(CostUsage.usage_date >= start_date)
            .filter(CostUsage.usage_date <= end_date)
            .group_by(
                Resource.resource_id,
                Resource.name,
                Resource.resource_type,
                Resource.region,
                cast(Resource.tags, Text),
                Service.name,
                Subscription.name,
                ResourceGroup.name,
            )
            .order_by(desc("total_cost"))
        )
        
        if subscription_ids:
            query = query.filter(Subscription.subscription_id.in_(subscription_ids))
        
        if service_names:
            query = query.filter(Service.name.in_(service_names))
        
        results = query.limit(limit).all()
        
        # Calculate total cost for percentage
        total_query = (
            self.db.query(func.sum(CostUsage.cost))
            .filter(CostUsage.usage_date >= start_date)
            .filter(CostUsage.usage_date <= end_date)
        )
        total_cost = total_query.scalar() or 1
        
        return [
            {
                "resource_id": r.resource_id,
                "name": r.name,
                "resource_type": r.resource_type,
                "service_name": r.service_name,
                "region": r.region,
                "subscription_name": r.subscription_name,
                "resource_group": r.resource_group,
                "total_cost": float(r.total_cost),
                "daily_avg_cost": float(r.total_cost / days),
                "usage_quantity": float(r.usage_quantity),
                "cost_percentage": float(r.total_cost / total_cost * 100),
                "tags": r.tags or {},
            }
            for r in results
        ]
    
    def get_idle_resources(
        self,
        start_date: date,
        end_date: date,
        usage_threshold: float = 0.1,
    ) -> List[dict]:
        """Find resources with very low usage but ongoing costs."""
        query = (
            self.db.query(
                Resource.resource_id,
                Resource.name,
                Resource.resource_type,
                Service.name.label("service_name"),
                Subscription.subscription_id,
                func.sum(CostUsage.cost).label("total_cost"),
                func.avg(CostUsage.usage_quantity).label("avg_usage"),
            )
            .join(CostUsage, Resource.id == CostUsage.resource_id)
            .join(Service, Resource.service_id == Service.id)
            .join(ResourceGroup, Resource.resource_group_id == ResourceGroup.id)
            .join(Subscription, ResourceGroup.subscription_id == Subscription.id)
            .filter(CostUsage.usage_date >= start_date)
            .filter(CostUsage.usage_date <= end_date)
            .filter(Resource.is_active == True)
            .group_by(
                Resource.resource_id,
                Resource.name,
                Resource.resource_type,
                Service.name,
                Subscription.subscription_id,
            )
            .having(func.avg(CostUsage.usage_quantity) < usage_threshold)
            .having(func.sum(CostUsage.cost) > 0)
            .order_by(desc("total_cost"))
        )
        
        return [
            {
                "resource_id": r.resource_id,
                "name": r.name,
                "resource_type": r.resource_type,
                "service_name": r.service_name,
                "subscription_id": r.subscription_id,
                "total_cost": float(r.total_cost),
                "avg_usage": float(r.avg_usage),
            }
            for r in query.all()
        ]
    
    def get_resource_details(self, resource_id: str) -> Optional[dict]:
        """Get detailed information about a specific resource."""
        query = (
            self.db.query(
                Resource,
                Service.name.label("service_name"),
                Service.category.label("service_category"),
                ResourceGroup.name.label("resource_group_name"),
                Subscription.name.label("subscription_name"),
                Subscription.subscription_id,
            )
            .join(Service, Resource.service_id == Service.id)
            .join(ResourceGroup, Resource.resource_group_id == ResourceGroup.id)
            .join(Subscription, ResourceGroup.subscription_id == Subscription.id)
            .filter(Resource.resource_id == resource_id)
        )
        
        result = query.first()
        if not result:
            return None
        
        resource = result[0]
        return {
            "id": resource.id,
            "resource_id": resource.resource_id,
            "name": resource.name,
            "resource_type": resource.resource_type,
            "sku": resource.sku,
            "region": resource.region,
            "tags": resource.tags or {},
            "properties": resource.properties or {},
            "provisioning_state": resource.provisioning_state,
            "is_active": resource.is_active,
            "service_name": result.service_name,
            "service_category": result.service_category,
            "resource_group_name": result.resource_group_name,
            "subscription_name": result.subscription_name,
            "subscription_id": result.subscription_id,
            "created_at": resource.created_at,
            "last_activity_at": resource.last_activity_at,
        }
