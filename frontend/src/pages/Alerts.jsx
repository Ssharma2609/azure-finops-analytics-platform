import { useEffect, useState } from 'react';
import { api } from '../services/api';
import './Alerts.css';

export default function Alerts() {
  const [anomalies, setAnomalies] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = { days: 30 };

        const [anomalyData, recomData] = await Promise.all([
          api.detectCostAnomaly(params),
          api.getRecommendations(params),
        ]);

        setAnomalies(anomalyData);
        setRecommendations(recomData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="alerts-container"><div className="loading">Loading alerts...</div></div>;
  }

  if (error) {
    return (
      <div className="alerts-container">
        <div className="error">
          <h2>Error Loading Alerts</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const anomalyList = anomalies?.data || [];
  const recommendationList = recommendations?.data || [];

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return 'severity-high';
      case 'medium':
        return 'severity-medium';
      case 'low':
        return 'severity-low';
      default:
        return 'severity-info';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return '🔴';
      case 'medium':
        return '🟡';
      case 'low':
        return '🟢';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className="alerts-container">
      <div className="header">
        <h1>Alerts & Recommendations</h1>
      </div>

      <div className="alerts-grid">
        <div className="alerts-section">
          <h2>🚨 Cost Anomalies</h2>
          {anomalyList.length > 0 ? (
            <div className="anomalies-list">
              {anomalyList.map((anomaly, index) => (
                <div key={index} className={`anomaly-card ${getSeverityColor(anomaly.severity)}`}>
                  <div className="anomaly-header">
                    <div className="anomaly-icon">{getSeverityIcon(anomaly.severity)}</div>
                    <div className="anomaly-title">{anomaly.resource_name}</div>
                  </div>
                  <div className="anomaly-details">
                    <div className="detail-row">
                      <span className="detail-label">Service:</span>
                      <span className="detail-value">{anomaly.service_name}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Detected Value:</span>
                      <span className="detail-value">${anomaly.detected_value?.toFixed(2) || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Expected Value:</span>
                      <span className="detail-value">${anomaly.expected_value?.toFixed(2) || 'N/A'}</span>
                    </div>
                    {anomaly.deviation_percent && (
                      <div className="detail-row">
                        <span className="detail-label">Deviation:</span>
                        <span className="detail-value deviation">{anomaly.deviation_percent.toFixed(1)}%</span>
                      </div>
                    )}
                  </div>
                  <div className="anomaly-description">{anomaly.description}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">✓</div>
              <div className="empty-text">No anomalies detected</div>
              <div className="empty-subtext">Your costs are within expected range</div>
            </div>
          )}
        </div>

        <div className="alerts-section">
          <h2>💡 Recommendations</h2>
          {recommendationList.length > 0 ? (
            <div className="recommendations-list">
              {recommendationList.map((rec, index) => (
                <div key={index} className={`recommendation-card ${getSeverityColor(rec.priority)}`}>
                  <div className="recommendation-header">
                    <div className="recommendation-icon">{getSeverityIcon(rec.priority)}</div>
                    <div className="recommendation-title">{rec.title}</div>
                  </div>
                  <div className="recommendation-body">
                    <p className="recommendation-description">{rec.description}</p>
                    {rec.resource_name && (
                      <div className="affected-resources">
                        <div className="affected-label">Resource: {rec.resource_name}</div>
                      </div>
                    )}
                    {rec.estimated_monthly_savings && (
                      <div className="potential-savings">
                        <div className="savings-label">Monthly Savings:</div>
                        <div className="savings-value">${rec.estimated_monthly_savings?.toFixed(2) || 'TBD'}</div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">✓</div>
              <div className="empty-text">No recommendations</div>
              <div className="empty-subtext">Your cost optimization is on track</div>
            </div>
          )}
        </div>
      </div>

      <div className="summary-section">
        <h2>Summary</h2>
        <div className="summary-stats">
          <div className="summary-stat">
            <div className="stat-label">Total Anomalies</div>
            <div className="stat-count">{anomalyList.length}</div>
          </div>
          <div className="summary-stat">
            <div className="stat-label">Critical Issues</div>
            <div className="stat-count critical">
              {anomalyList.filter((a) => a.severity?.toLowerCase() === 'high').length}
            </div>
          </div>
          <div className="summary-stat">
            <div className="stat-label">Recommendations</div>
            <div className="stat-count">{recommendationList.length}</div>
          </div>
          <div className="summary-stat">
            <div className="stat-label">Total Savings Potential</div>
            <div className="stat-count savings">
              ${recommendationList
                .reduce((sum, rec) => sum + (rec.estimated_monthly_savings || 0), 0)
                .toFixed(2)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
