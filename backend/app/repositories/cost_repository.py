"""
Repository for cost and usage data operations.
"""
from typing import List, Optional, Tuple
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, asc
from uuid import UUID

from app.repositories.base import BaseRepository
from app.models.cost_usage import CostUsage
from app.models.resource import Resource
from app.models.service import Service
from app.models.resource_group import ResourceGroup
from app.models.subscription import Subscription


class CostRepository(BaseRepository[CostUsage]):
    """Repository for cost usage operations with analytics queries."""
    
    def __init__(self, db: Session):
        super().__init__(CostUsage, db)
    
    def get_cost_summary(
        self,
        start_date: date,
        end_date: date,
        subscription_ids: Optional[List[str]] = None,
        service_names: Optional[List[str]] = None,
    ) -> dict:
        """Get aggregated cost summary for a period."""
        query = (
            self.db.query(
                func.sum(CostUsage.cost).label("total_cost"),
                func.avg(CostUsage.cost).label("avg_cost"),
                func.min(CostUsage.cost).label("min_cost"),
                func.max(CostUsage.cost).label("max_cost"),
                func.count(func.distinct(CostUsage.usage_date)).label("total_days"),
            )
            .join(Resource, CostUsage.resource_id == Resource.id)
            .join(ResourceGroup, Resource.resource_group_id == ResourceGroup.id)
            .join(Subscription, ResourceGroup.subscription_id == Subscription.id)
            .filter(CostUsage.usage_date >= start_date)
            .filter(CostUsage.usage_date <= end_date)
        )
        
        if subscription_ids:
            query = query.filter(Subscription.subscription_id.in_(subscription_ids))
        
        if service_names:
            query = query.join(Service, Resource.service_id == Service.id)
            query = query.filter(Service.name.in_(service_names))
        
        result = query.first()
        
        return {
            "total_cost": float(result.total_cost or 0),
            "avg_daily_cost": float(result.avg_cost or 0),
            "min_daily_cost": float(result.min_cost or 0),
            "max_daily_cost": float(result.max_cost or 0),
            "total_days": int(result.total_days or 0),
        }
    
    def get_daily_cost_trend(
        self,
        start_date: date,
        end_date: date,
        subscription_ids: Optional[List[str]] = None,
    ) -> List[dict]:
        """Get daily cost trend data."""
        query = (
            self.db.query(
                CostUsage.usage_date,
                func.sum(CostUsage.cost).label("cost"),
                func.sum(CostUsage.usage_quantity).label("usage_quantity"),
                func.count(func.distinct(CostUsage.resource_id)).label("resource_count"),
            )
            .filter(CostUsage.usage_date >= start_date)
            .filter(CostUsage.usage_date <= end_date)
            .group_by(CostUsage.usage_date)
            .order_by(CostUsage.usage_date)
        )
        
        if subscription_ids:
            query = (
                query.join(Resource, CostUsage.resource_id == Resource.id)
                .join(ResourceGroup, Resource.resource_group_id == ResourceGroup.id)
                .join(Subscription, ResourceGroup.subscription_id == Subscription.id)
                .filter(Subscription.subscription_id.in_(subscription_ids))
            )
        
        results = query.all()
        
        return [
            {
                "date": r.usage_date,
                "cost": float(r.cost),
                "usage_quantity": float(r.usage_quantity),
                "resource_count": int(r.resource_count),
            }
            for r in results
        ]
    
    def get_cost_by_service(
        self,
        start_date: date,
        end_date: date,
        subscription_ids: Optional[List[str]] = None,
    ) -> List[dict]:
        """Get cost breakdown by service."""
        query = (
            self.db.query(
                Service.name.label("service_name"),
                Service.category.label("service_category"),
                func.sum(CostUsage.cost).label("total_cost"),
                func.count(func.distinct(Resource.id)).label("resource_count"),
            )
            .join(Resource, CostUsage.resource_id == Resource.id)
            .join(Service, Resource.service_id == Service.id)
            .filter(CostUsage.usage_date >= start_date)
            .filter(CostUsage.usage_date <= end_date)
            .group_by(Service.name, Service.category)
            .order_by(desc("total_cost"))
        )
        
        if subscription_ids:
            query = (
                query.join(ResourceGroup, Resource.resource_group_id == ResourceGroup.id)
                .join(Subscription, ResourceGroup.subscription_id == Subscription.id)
                .filter(Subscription.subscription_id.in_(subscription_ids))
            )
        
        results = query.all()
        total_cost = sum(r.total_cost for r in results)
        
        return [
            {
                "service_name": r.service_name,
                "service_category": r.service_category,
                "total_cost": float(r.total_cost),
                "percentage_of_total": float(r.total_cost / total_cost * 100) if total_cost > 0 else 0,
                "resource_count": int(r.resource_count),
                "avg_cost_per_resource": float(r.total_cost / r.resource_count) if r.resource_count > 0 else 0,
            }
            for r in results
        ]
    
    def get_cost_by_subscription(
        self,
        start_date: date,
        end_date: date,
    ) -> List[dict]:
        """Get cost breakdown by subscription."""
        query = (
            self.db.query(
                Subscription.subscription_id,
                Subscription.name.label("subscription_name"),
                Subscription.environment,
                Subscription.budget_limit,
                func.sum(CostUsage.cost).label("total_cost"),
                func.count(func.distinct(Resource.id)).label("resource_count"),
            )
            .join(Resource, CostUsage.resource_id == Resource.id)
            .join(ResourceGroup, Resource.resource_group_id == ResourceGroup.id)
            .join(Subscription, ResourceGroup.subscription_id == Subscription.id)
            .filter(CostUsage.usage_date >= start_date)
            .filter(CostUsage.usage_date <= end_date)
            .group_by(
                Subscription.subscription_id,
                Subscription.name,
                Subscription.environment,
                Subscription.budget_limit,
            )
            .order_by(desc("total_cost"))
        )
        
        results = query.all()
        total_cost = sum(r.total_cost for r in results)
        
        return [
            {
                "subscription_id": r.subscription_id,
                "subscription_name": r.subscription_name,
                "environment": r.environment,
                "total_cost": float(r.total_cost),
                "percentage_of_total": float(r.total_cost / total_cost * 100) if total_cost > 0 else 0,
                "resource_count": int(r.resource_count),
                "budget_limit": float(r.budget_limit) if r.budget_limit else None,
                "budget_utilization": (
                    float(r.total_cost / float(r.budget_limit) * 100)
                    if r.budget_limit
                    else None
                ),
            }
            for r in results
        ]
    
    def get_cost_data_for_analysis(
        self,
        start_date: date,
        end_date: date,
    ) -> List[Tuple[date, float]]:
        """Get raw daily cost data for analytics."""
        query = (
            self.db.query(
                CostUsage.usage_date,
                func.sum(CostUsage.cost).label("daily_cost"),
            )
            .filter(CostUsage.usage_date >= start_date)
            .filter(CostUsage.usage_date <= end_date)
            .group_by(CostUsage.usage_date)
            .order_by(CostUsage.usage_date)
        )
        
        return [(r.usage_date, float(r.daily_cost)) for r in query.all()]
