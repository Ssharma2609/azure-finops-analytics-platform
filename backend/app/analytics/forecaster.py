"""
Cost forecasting engine using statistical methods.
"""
from typing import List, Tuple, Dict, Any
from datetime import date, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


class CostForecaster:
    """
    Forecasts future costs using multiple methods.
    
    Methods:
    - Moving average
    - Linear regression
    - Polynomial regression (for trends)
    
    Automatically selects best method based on data characteristics.
    """
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
    
    def forecast(
        self,
        historical_data: List[Tuple[date, float]],
        forecast_days: int = 7,
    ) -> Dict[str, Any]:
        """
        Generate cost forecast.
        
        Args:
            historical_data: List of (date, cost) tuples
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with predictions and model metadata
        """
        if len(historical_data) < 7:
            return self._insufficient_data_response()
        
        dates = [d[0] for d in historical_data]
        costs = np.array([d[1] for d in historical_data])
        
        # Try different models and select best
        models = {
            "moving_average": self._moving_average_forecast,
            "linear_regression": self._linear_regression_forecast,
            "weighted_average": self._weighted_average_forecast,
        }
        
        best_model = None
        best_accuracy = float("inf")
        best_predictions = None
        
        for name, method in models.items():
            try:
                result = method(dates, costs, forecast_days)
                # Use in-sample error as proxy for accuracy
                if result["mae"] < best_accuracy:
                    best_accuracy = result["mae"]
                    best_model = name
                    best_predictions = result
            except Exception:
                continue
        
        if best_predictions is None:
            best_predictions = self._moving_average_forecast(dates, costs, forecast_days)
            best_model = "moving_average"
        
        return {
            "predictions": best_predictions["forecast"],
            "model": best_model,
            "accuracy": {
                "mae": best_predictions["mae"],
                "rmse": best_predictions["rmse"],
                "mape": best_predictions.get("mape", 0),
            },
        }
    
    def _moving_average_forecast(
        self,
        dates: List[date],
        costs: np.ndarray,
        forecast_days: int,
        window: int = 7,
    ) -> Dict[str, Any]:
        """Simple moving average forecast."""
        # Calculate moving average for validation
        ma_values = []
        for i in range(window, len(costs)):
            ma_values.append(np.mean(costs[i-window:i]))
        
        actuals = costs[window:]
        mae = np.mean(np.abs(actuals - ma_values))
        rmse = np.sqrt(np.mean((actuals - ma_values) ** 2))
        
        # Forecast future values
        last_window = costs[-window:]
        forecast_value = np.mean(last_window)
        std = np.std(last_window)
        
        # Generate forecasts
        forecasts = []
        last_date = dates[-1]
        
        for i in range(1, forecast_days + 1):
            forecast_date = last_date + timedelta(days=i)
            margin = 1.96 * std  # 95% confidence
            
            forecasts.append({
                "date": forecast_date,
                "predicted": float(forecast_value),
                "lower_bound": float(max(0, forecast_value - margin)),
                "upper_bound": float(forecast_value + margin),
            })
        
        return {
            "forecast": forecasts,
            "mae": float(mae),
            "rmse": float(rmse),
        }
    
    def _weighted_average_forecast(
        self,
        dates: List[date],
        costs: np.ndarray,
        forecast_days: int,
        window: int = 14,
    ) -> Dict[str, Any]:
        """Exponentially weighted moving average forecast."""
        # More recent data gets higher weight
        weights = np.exp(np.linspace(-1, 0, min(window, len(costs))))
        weights = weights / weights.sum()
        
        recent_costs = costs[-len(weights):]
        forecast_value = np.average(recent_costs, weights=weights)
        std = np.std(costs[-window:]) if len(costs) >= window else np.std(costs)
        
        # Calculate validation metrics
        if len(costs) > window:
            errors = []
            for i in range(window, len(costs)):
                w = np.exp(np.linspace(-1, 0, min(window, i)))
                w = w / w.sum()
                pred = np.average(costs[max(0, i-window):i][-len(w):], weights=w)
                errors.append(abs(costs[i] - pred))
            mae = np.mean(errors)
            rmse = np.sqrt(np.mean(np.array(errors) ** 2))
        else:
            mae = std
            rmse = std
        
        # Generate forecasts with trend
        trend = 0
        if len(costs) >= 14:
            recent_mean = np.mean(costs[-7:])
            older_mean = np.mean(costs[-14:-7])
            if older_mean > 0:
                trend = (recent_mean - older_mean) / older_mean
        
        forecasts = []
        last_date = dates[-1]
        
        for i in range(1, forecast_days + 1):
            forecast_date = last_date + timedelta(days=i)
            adjusted_value = forecast_value * (1 + trend * i / 7)
            margin = 1.96 * std * (1 + 0.1 * i)  # Increasing uncertainty
            
            forecasts.append({
                "date": forecast_date,
                "predicted": float(adjusted_value),
                "lower_bound": float(max(0, adjusted_value - margin)),
                "upper_bound": float(adjusted_value + margin),
            })
        
        return {
            "forecast": forecasts,
            "mae": float(mae),
            "rmse": float(rmse),
        }
    
    def _linear_regression_forecast(
        self,
        dates: List[date],
        costs: np.ndarray,
        forecast_days: int,
    ) -> Dict[str, Any]:
        """Linear regression forecast."""
        X = np.arange(len(costs)).reshape(-1, 1)
        y = costs
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate metrics
        predictions = model.predict(X)
        mae = np.mean(np.abs(y - predictions))
        rmse = np.sqrt(np.mean((y - predictions) ** 2))
        mape = np.mean(np.abs((y - predictions) / y)) * 100
        
        # Calculate residual std for confidence intervals
        residuals = y - predictions
        std = np.std(residuals)
        
        # Generate forecasts
        forecasts = []
        last_date = dates[-1]
        start_idx = len(costs)
        
        for i in range(forecast_days):
            forecast_date = last_date + timedelta(days=i + 1)
            forecast_idx = start_idx + i
            predicted = model.predict([[forecast_idx]])[0]
            margin = 1.96 * std * (1 + 0.05 * i)
            
            forecasts.append({
                "date": forecast_date,
                "predicted": float(max(0, predicted)),
                "lower_bound": float(max(0, predicted - margin)),
                "upper_bound": float(predicted + margin),
            })
        
        return {
            "forecast": forecasts,
            "mae": float(mae),
            "rmse": float(rmse),
            "mape": float(mape),
        }
    
    def _insufficient_data_response(self) -> Dict[str, Any]:
        """Return empty response when data is insufficient."""
        return {
            "predictions": [],
            "model": "insufficient_data",
            "accuracy": {"mae": 0, "rmse": 0, "mape": 0},
        }
 