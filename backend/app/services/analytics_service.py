"""
Analytics and forecasting business logic service.
"""
from typing import Optional, List
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
import uuid

from app.repositories.cost_repository import CostRepository
from app.repositories.resource_repository import ResourceRepository
from app.analytics.forecaster import CostForecaster
from app.analytics.recommender import CostRecommender
from app.schemas.analytics import (
    ForecastResponse,
    ForecastDataPoint,
    RecommendationResponse,
    Recommendation,
)
from app.config import settings


class AnalyticsService:
    """Service for analytics and forecasting operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cost_repo = CostRepository(db)
        self.resource_repo = ResourceRepository(db)
        self.forecaster = CostForecaster()
        self.recommender = CostRecommender()
    
    def get_forecast(
        self,
        forecast_days: int = 7,
        history_days: int = 60,
    ) -> ForecastResponse:
        """Generate cost forecast."""
        end_date = date.today()
        start_date = end_date - timedelta(days=history_days)
        
        # Get historical data
        historical_data = self.cost_repo.get_cost_data_for_analysis(
            start_date=start_date,
            end_date=end_date,
        )
        
        if len(historical_data) < 14:
            # Not enough data for meaningful forecast
            return ForecastResponse(
                historical_data=[],
                forecast_data=[],
                model_used="insufficient_data",
                accuracy_metrics={},
                total_forecasted_cost=0,
                average_daily_forecast=0,
                trend="unknown",
                generated_at=datetime.utcnow().isoformat(),
            )
        
        # Generate forecast
        forecast_result = self.forecaster.forecast(
            historical_data=historical_data,
            forecast_days=forecast_days,
        )
        
        # Format historical data for response (last 30 days)
        historical_formatted = [
            {"date": str(d), "cost": c}
            for d, c in historical_data[-30:]
        ]
        
        # Format forecast data
        forecast_points = [
            ForecastDataPoint(
                date=point["date"],
                predicted_cost=point["predicted"],
                lower_bound=point["lower_bound"],
                upper_bound=point["upper_bound"],
                confidence_level=0.95,
            )
            for point in forecast_result["predictions"]
        ]
        
        total_forecast = sum(p.predicted_cost for p in forecast_points)
        avg_forecast = total_forecast / len(forecast_points) if forecast_points else 0
        
        # Determine trend
        if len(forecast_points) >= 2:
            first_half = sum(p.predicted_cost for p in forecast_points[:len(forecast_points)//2])
            second_half = sum(p.predicted_cost for p in forecast_points[len(forecast_points)//2:])
            if second_half > first_half * 1.05:
                trend = "increasing"
            elif second_half < first_half * 0.95:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return ForecastResponse(
            historical_data=historical_formatted,
            forecast_data=forecast_points,
            model_used=forecast_result["model"],
            accuracy_metrics=forecast_result["accuracy"],
            total_forecasted_cost=total_forecast,
            average_daily_forecast=avg_forecast,
            trend=trend,
            generated_at=datetime.utcnow().isoformat(),
        )
    
    def get_recommendations(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> RecommendationResponse:
        """Generate cost optimization recommendations."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get data for recommendation engine
        idle_resources = self.resource_repo.get_idle_resources(
            start_date=start_date,
            end_date=end_date,
        )
        
        service_costs = self.cost_repo.get_cost_by_service(
            start_date=start_date,
            end_date=end_date,
        )
        
        subscription_costs = self.cost_repo.get_cost_by_subscription(
            start_date=start_date,
            end_date=end_date,
        )
        
        # Generate recommendations
        raw_recommendations = self.recommender.generate_recommendations(
            idle_resources=idle_resources,
            service_costs=service_costs,
            subscription_costs=subscription_costs,
        )
        
        recommendations = [
            Recommendation(
                id=str(uuid.uuid4()),
                **rec,
                generated_at=datetime.utcnow().isoformat(),
            )
            for rec in raw_recommendations
        ]
        
        # Calculate totals
        total_savings = sum(r.estimated_monthly_savings for r in recommendations)
        
        by_type = {}
        by_priority = {}
        for rec in recommendations:
            by_type[rec.type.value] = by_type.get(rec.type.value, 0) + 1
            by_priority[rec.priority.value] = by_priority.get(rec.priority.value, 0) + 1
        
        return RecommendationResponse(
            data=recommendations,
            total_count=len(recommendations),
            total_potential_savings=total_savings,
            by_type=by_type,
            by_priority=by_priority,
        )
