"""
Anomaly detection engine using statistical methods.
"""
from typing import List, Tuple
from datetime import date
import numpy as np
from dataclasses import dataclass


@dataclass
class AnomalyResult:
    """Result of anomaly detection for a single point."""
    date: date
    actual_cost: float
    expected_cost: float
    deviation: float
    deviation_percent: float
    is_anomaly: bool
    confidence: float


class AnomalyDetector:
    """
    Detects cost anomalies using statistical methods.
    
    Uses a combination of:
    - Z-score analysis
    - Moving average deviation
    - Seasonal adjustment (day of week)
    """
    
    def __init__(
        self,
        threshold: float = 2.5,
        window_size: int = 14,
        min_data_points: int = 7,
    ):
        self.threshold = threshold
        self.window_size = window_size
        self.min_data_points = min_data_points
    
    def detect(self, data: List[Tuple[date, float]]) -> List[dict]:
        """
        Detect anomalies in cost time series data.
        
        Args:
            data: List of (date, cost) tuples sorted by date
            
        Returns:
            List of detected anomalies with details
        """
        if len(data) < self.min_data_points:
            return []
        
        dates = [d[0] for d in data]
        costs = np.array([d[1] for d in data])
        
        anomalies = []
        
        # Calculate moving statistics
        for i in range(self.window_size, len(costs)):
            window = costs[max(0, i - self.window_size):i]
            current_cost = costs[i]
            current_date = dates[i]
            
            # Calculate expected value using moving average
            mean = np.mean(window)
            std = np.std(window)
            
            if std == 0:
                std = 0.01  # Avoid division by zero
            
            # Calculate z-score
            z_score = (current_cost - mean) / std
            
            # Determine if anomaly
            is_anomaly = abs(z_score) > self.threshold
            
            if is_anomaly:
                deviation = current_cost - mean
                deviation_percent = (deviation / mean) * 100 if mean > 0 else 0
                
                # Calculate confidence based on z-score magnitude
                confidence = min(1.0, abs(z_score) / (self.threshold * 2))
                
                anomalies.append({
                    "date": current_date,
                    "actual_cost": float(current_cost),
                    "expected_cost": float(mean),
                    "deviation": float(deviation),
                    "deviation_percent": float(deviation_percent),
                    "confidence": float(confidence),
                    "z_score": float(z_score),
                })
        
        # Sort by deviation magnitude (most significant first)
        anomalies.sort(key=lambda x: abs(x["deviation_percent"]), reverse=True)
        
        return anomalies
    
    def detect_with_seasonality(
        self,
        data: List[Tuple[date, float]],
    ) -> List[dict]:
        """
        Detect anomalies with day-of-week seasonality adjustment.
        """
        if len(data) < 14:
            return self.detect(data)
        
        dates = [d[0] for d in data]
        costs = np.array([d[1] for d in data])
        
        # Calculate day-of-week patterns
        dow_costs = {i: [] for i in range(7)}
        for d, c in data:
            dow_costs[d.weekday()].append(c)
        
        dow_means = {
            dow: np.mean(costs_list) if costs_list else 0
            for dow, costs_list in dow_costs.items()
        }
        
        overall_mean = np.mean(costs)
        
        # Calculate seasonal factors
        seasonal_factors = {
            dow: mean / overall_mean if overall_mean > 0 else 1.0
            for dow, mean in dow_means.items()
        }
        
        # Deseasonalize data
        deseasonalized = []
        for d, c in data:
            factor = seasonal_factors.get(d.weekday(), 1.0)
            deseasonalized.append((d, c / factor if factor > 0 else c))
        
        # Detect anomalies on deseasonalized data
        raw_anomalies = self.detect(deseasonalized)
        
        # Re-seasonalize the expected values
        for anomaly in raw_anomalies:
            factor = seasonal_factors.get(anomaly["date"].weekday(), 1.0)
            anomaly["expected_cost"] *= factor
            anomaly["deviation"] = anomaly["actual_cost"] - anomaly["expected_cost"]
            if anomaly["expected_cost"] > 0:
                anomaly["deviation_percent"] = (
                    anomaly["deviation"] / anomaly["expected_cost"]
                ) * 100
        
        return raw_anomalies
