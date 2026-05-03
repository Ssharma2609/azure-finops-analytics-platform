"""
Cost analysis business logic service.
"""
from typing import Optional, List
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.repositories.cost_repository import CostRepository
from app.schemas.cost import (
    CostSummary,
    CostTrendResponse,
    ServiceCostResponse,
    SubscriptionCostResponse,
    DailyCost,
    ServiceCost,
    SubscriptionCost,
)


class CostService:
    """Service for cost analysis operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cost_repo = CostRepository(db)
    
    def get_cost_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        subscription_ids: Optional[List[str]] = None,
        service_names: Optional[List[str]] = None,
    ) -> CostSummary:
        """Get cost summary with optional filters."""
        # Default to last 30 days
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get current period summary
        current_summary = self.cost_repo.get_cost_summary(
            start_date=start_date,
            end_date=end_date,
            subscription_ids=subscription_ids,
            service_names=service_names,
        )
        
        # Get previous period for comparison
        period_days = (end_date - start_date).days
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_days)
        
        prev_summary = self.cost_repo.get_cost_summary(
            start_date=prev_start,
            end_date=prev_end,
            subscription_ids=subscription_ids,
            service_names=service_names,
        )
        
        # Calculate change percentage
        cost_change = None
        if prev_summary["total_cost"] > 0:
            cost_change = (
                (current_summary["total_cost"] - prev_summary["total_cost"])
                / prev_summary["total_cost"]
                * 100
            )
        
        return CostSummary(
            total_cost=current_summary["total_cost"],
            average_daily_cost=current_summary["avg_daily_cost"],
            min_daily_cost=current_summary["min_daily_cost"],
            max_daily_cost=current_summary["max_daily_cost"],
            total_days=current_summary["total_days"],
            currency="USD",
            period_start=start_date,
            period_end=end_date,
            cost_change_percent=cost_change,
        )
    
    def get_cost_trend(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        subscription_ids: Optional[List[str]] = None,
    ) -> CostTrendResponse:
        """Get daily cost trend data."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        trend_data = self.cost_repo.get_daily_cost_trend(
            start_date=start_date,
            end_date=end_date,
            subscription_ids=subscription_ids,
        )
        
        daily_costs = [
            DailyCost(
                date=d["date"],
                cost=d["cost"],
                usage_quantity=d["usage_quantity"],
                resource_count=d["resource_count"],
            )
            for d in trend_data
        ]
        
        return CostTrendResponse(
            data=daily_costs,
            total_records=len(daily_costs),
            period_start=start_date,
            period_end=end_date,
        )
    
    def get_cost_by_service(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        subscription_ids: Optional[List[str]] = None,
    ) -> ServiceCostResponse:
        """Get cost breakdown by service."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        service_data = self.cost_repo.get_cost_by_service(
            start_date=start_date,
            end_date=end_date,
            subscription_ids=subscription_ids,
        )
        
        service_costs = [ServiceCost(**d) for d in service_data]
        total_cost = sum(s.total_cost for s in service_costs)
        
        return ServiceCostResponse(
            data=service_costs,
            total_cost=total_cost,
            period_start=start_date,
            period_end=end_date,
        )
    
    def get_cost_by_subscription(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> SubscriptionCostResponse:
        """Get cost breakdown by subscription."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        subscription_data = self.cost_repo.get_cost_by_subscription(
            start_date=start_date,
            end_date=end_date,
        )
        
        subscription_costs = [SubscriptionCost(**d) for d in subscription_data]
        total_cost = sum(s.total_cost for s in subscription_costs)
        
        return SubscriptionCostResponse(
            data=subscription_costs,
            total_cost=total_cost,
            period_start=start_date,
            period_end=end_date,
        )
