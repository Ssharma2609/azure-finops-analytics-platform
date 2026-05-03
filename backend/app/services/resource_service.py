"""
Resource management business logic service.
"""

import json
from typing import Optional, List
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.repositories.resource_repository import ResourceRepository
from app.schemas.resource import (
    TopExpensiveResource,
    TopExpensiveResponse,
    ResourceDetail,
)


class ResourceService:
    """Service for resource operations."""

    def __init__(self, db: Session):
        self.db = db
        self.resource_repo = ResourceRepository(db)

    def get_top_expensive_resources(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10,
        subscription_ids: Optional[List[str]] = None,
        service_names: Optional[List[str]] = None,
    ) -> TopExpensiveResponse:
        """Get top expensive resources."""

        if not end_date:
            end_date = date.today()

        if not start_date:
            start_date = end_date - timedelta(days=30)

        resources_data = self.resource_repo.get_top_expensive_resources(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            subscription_ids=subscription_ids,
            service_names=service_names,
        )

        # Fix JSON string -> dictionary conversion for tags
        resources = []

        for r in resources_data:

            # Convert tags from JSON string to Python dict
            if isinstance(r.get("tags"), str):
                try:
                    r["tags"] = json.loads(r["tags"])
                except Exception:
                    r["tags"] = {}

            resources.append(TopExpensiveResource(**r))

        total_cost = sum(r.total_cost for r in resources)

        return TopExpensiveResponse(
            data=resources,
            total_cost=total_cost,
            period_start=start_date,
            period_end=end_date,
            limit=limit,
        )

    def get_resource_details(self, resource_id: str) -> Optional[ResourceDetail]:
        """Get detailed resource information."""

        data = self.resource_repo.get_resource_details(resource_id)

        if not data:
            return None

        # Convert tags if stored as JSON string
        if isinstance(data.get("tags"), str):
            try:
                data["tags"] = json.loads(data["tags"])
            except Exception:
                data["tags"] = {}

        return ResourceDetail(**data)