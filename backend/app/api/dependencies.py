"""
API dependencies for dependency injection.
"""
from typing import Generator
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.services.cost_service import CostService
from app.services.resource_service import ResourceService
from app.services.analytics_service import AnalyticsService
from app.services.alert_service import AlertService


def get_cost_service(db: Session = next(get_db())) -> CostService:
    return CostService(db)


def get_resource_service(db: Session = next(get_db())) -> ResourceService:
    return ResourceService(db)


def get_analytics_service(db: Session = next(get_db())) -> AnalyticsService:
    return AnalyticsService(db)


def get_alert_service(db: Session = next(get_db())) -> AlertService:
    return AlertService(db)
