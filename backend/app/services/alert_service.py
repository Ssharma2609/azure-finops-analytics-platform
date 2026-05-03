"""
Alert and anomaly detection business logic service.
"""
from typing import Optional, List
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
import uuid

from app.repositories.cost_repository import CostRepository
from app.analytics.anomaly_detector import AnomalyDetector
from app.schemas.alert import (
    AnomalyDetail,
    AnomalyResponse,
    AlertSeverity,
    AlertType,
)
from app.config import settings


class AlertService:
    """Service for alert and anomaly operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cost_repo = CostRepository(db)
        self.anomaly_detector = AnomalyDetector(
            threshold=settings.ANOMALY_THRESHOLD
        )
    
    def get_anomalies(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        severity: Optional[AlertSeverity] = None,
    ) -> AnomalyResponse:
        """Detect and return cost anomalies."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get cost data for analysis
        cost_data = self.cost_repo.get_cost_data_for_analysis(
            start_date=start_date,
            end_date=end_date,
        )
        
        if len(cost_data) < 7:
            return AnomalyResponse(
                data=[],
                total_count=0,
                unacknowledged_count=0,
                critical_count=0,
                high_count=0,
                medium_count=0,
                low_count=0,
            )
        
        # Detect anomalies
        detected = self.anomaly_detector.detect(cost_data)
        
        # Convert to AnomalyDetail objects
        anomalies = []
        for anomaly in detected:
            detail = AnomalyDetail(
                id=str(uuid.uuid4()),
                alert_type=AlertType.COST_SPIKE if anomaly["deviation"] > 0 else AlertType.ANOMALY_DETECTED,
                severity=self._calculate_severity(anomaly["deviation_percent"]),
                title=f"Cost {'spike' if anomaly['deviation'] > 0 else 'drop'} detected",
                description=self._generate_description(anomaly),
                detected_value=anomaly["actual_cost"],
                expected_value=anomaly["expected_cost"],
                deviation_percent=anomaly["deviation_percent"],
                confidence_score=anomaly["confidence"],
                detected_at=datetime.utcnow(),
                anomaly_date=anomaly["date"],
                is_acknowledged=False,
            )
            anomalies.append(detail)
        
        # Filter by severity if specified
        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]
        
        # Count by severity
        severity_counts = {
            "critical": sum(1 for a in anomalies if a.severity == AlertSeverity.CRITICAL),
            "high": sum(1 for a in anomalies if a.severity == AlertSeverity.HIGH),
            "medium": sum(1 for a in anomalies if a.severity == AlertSeverity.MEDIUM),
            "low": sum(1 for a in anomalies if a.severity == AlertSeverity.LOW),
        }
        
        return AnomalyResponse(
            data=anomalies,
            total_count=len(anomalies),
            unacknowledged_count=sum(1 for a in anomalies if not a.is_acknowledged),
            critical_count=severity_counts["critical"],
            high_count=severity_counts["high"],
            medium_count=severity_counts["medium"],
            low_count=severity_counts["low"],
        )
    
    def _calculate_severity(self, deviation_percent: float) -> AlertSeverity:
        """Calculate alert severity based on deviation percentage."""
        abs_deviation = abs(deviation_percent)
        if abs_deviation >= 100:
            return AlertSeverity.CRITICAL
        elif abs_deviation >= 50:
            return AlertSeverity.HIGH
        elif abs_deviation >= 25:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _generate_description(self, anomaly: dict) -> str:
        """Generate human-readable anomaly description."""
        direction = "higher" if anomaly["deviation"] > 0 else "lower"
        return (
            f"Daily cost was {abs(anomaly['deviation_percent']):.1f}% {direction} than expected. "
            f"Actual: ${anomaly['actual_cost']:.2f}, Expected: ${anomaly['expected_cost']:.2f}"
        )
