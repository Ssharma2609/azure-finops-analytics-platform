"""
API routes package.
"""
from fastapi import APIRouter

from app.api.routes import cost, resources, alerts, analytics, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(cost.router, prefix="/cost", tags=["Cost Analysis"])
api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
