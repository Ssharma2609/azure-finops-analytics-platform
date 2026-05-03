"""
Scheduled background tasks for analytics and data generation.
"""
import logging
from datetime import date, timedelta
from celery import shared_task

from app.database import SessionLocal
from app.services.alert_service import AlertService
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


@shared_task(name="tasks.scheduled_tasks.generate_daily_data")
def generate_daily_data():
    """
    Generate synthetic cost data for the current day.
    
    This simulates real-time data ingestion in a production system.
    """
    logger.info("Starting daily data generation task")
    
    # Import here to avoid circular imports
    from scripts.generate_data import (
        generate_daily_cost,
        AZURE_SERVICES,
    )
    from app.models import Resource, CostUsage, ResourceGroup, Subscription
    
    db = SessionLocal()
    
    try:
        today = date.today()
        
        # Get all active resources
        resources = (
            db.query(Resource)
            .filter(Resource.is_active == True)
            .all()
        )
        
        records_created = 0
        
        for resource in resources:
            # Find service config
            svc_config = next(
                (s for s in AZURE_SERVICES if s["name"].replace(" ", "") == resource.resource_type),
                None
            )
            
            if not svc_config:
                continue
            
            # Get environment
            rg = db.query(ResourceGroup).filter(ResourceGroup.id == resource.resource_group_id).first()
            sub = db.query(Subscription).filter(Subscription.id == rg.subscription_id).first()
            
            base_cost = svc_config["base_cost"]
            daily_cost = generate_daily_cost(
                base_cost=base_cost,
                day_index=0,
                total_days=1,
                env=sub.environment if sub else "development",
                add_spike=True,
                add_trend=False,
            )
            
            cost_record = CostUsage(
                resource_id=resource.id,
                usage_date=today,
                cost=daily_cost,
                pretax_cost=daily_cost * 0.85,
                usage_quantity=24.0,
                unit_price=daily_cost / 24.0,
                billing_currency="USD",
                meter_category=svc_config["category"],
                meter_subcategory=svc_config["name"],
            )
            db.add(cost_record)
            records_created += 1
        
        db.commit()
        logger.info(f"Generated {records_created} cost records for {today}")
        
        return {"status": "success", "records": records_created}
        
    except Exception as e:
        logger.error(f"Daily data generation failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@shared_task(name="tasks.scheduled_tasks.run_anomaly_detection")
def run_anomaly_detection():
    """
    Run anomaly detection on recent cost data.
    
    This task identifies cost spikes and unusual patterns.
    """
    logger.info("Starting anomaly detection task")
    
    db = SessionLocal()
    
    try:
        alert_service = AlertService(db)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=14)
        
        result = alert_service.get_anomalies(
            start_date=start_date,
            end_date=end_date,
        )
        
        logger.info(
            f"Anomaly detection complete. "
            f"Found {result.total_count} anomalies "
            f"({result.critical_count} critical, {result.high_count} high)"
        )
        
        return {
            "status": "success",
            "total_anomalies": result.total_count,
            "critical": result.critical_count,
            "high": result.high_count,
        }
        
    except Exception as e:
        logger.error(f"Anomaly detection failed: {str(e)}")
        raise
    finally:
        db.close()


@shared_task(name="tasks.scheduled_tasks.refresh_forecast")
def refresh_forecast():
    """
    Refresh cost forecast with latest data.
    
    Updates the 7-day forecast based on recent trends.
    """
    logger.info("Starting forecast refresh task")
    
    db = SessionLocal()
    
    try:
        analytics_service = AnalyticsService(db)
        
        result = analytics_service.get_forecast(
            forecast_days=7,
            history_days=60,
        )
        
        logger.info(
            f"Forecast refresh complete. "
            f"Model: {result.model_used}, "
            f"Total forecast: ${result.total_forecasted_cost:.2f}"
        )
        
        return {
            "status": "success",
            "model": result.model_used,
            "total_forecast": result.total_forecasted_cost,
            "trend": result.trend,
        }
        
    except Exception as e:
        logger.error(f"Forecast refresh failed: {str(e)}")
        raise
    finally:
        db.close()
