"""
Repository for subscription data operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.repositories.base import BaseRepository
from app.models.subscription import Subscription
from app.models.resource_group import ResourceGroup


class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for subscription operations."""
    
    def __init__(self, db: Session):
        super().__init__(Subscription, db)
    
    def get_by_subscription_id(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by Azure subscription ID."""
        return (
            self.db.query(Subscription)
            .filter(Subscription.subscription_id == subscription_id)
            .first()
        )
    
    def get_all_active(self) -> List[Subscription]:
        """Get all active subscriptions."""
        return (
            self.db.query(Subscription)
            .filter(Subscription.is_active == True)
            .all()
        )
    
    def get_subscriptions_with_stats(self) -> List[dict]:
        """Get subscriptions with resource group counts."""
        query = (
            self.db.query(
                Subscription,
                func.count(ResourceGroup.id).label("resource_group_count"),
            )
            .outerjoin(ResourceGroup, Subscription.id == ResourceGroup.subscription_id)
            .group_by(Subscription.id)
        )
        
        return [
            {
                "subscription_id": sub.subscription_id,
                "name": sub.name,
                "state": sub.state,
                "environment": sub.environment,
                "owner_email": sub.owner_email,
                "budget_limit": sub.budget_limit,
                "is_active": sub.is_active,
                "resource_group_count": count,
            }
            for sub, count in query.all()
        ]
