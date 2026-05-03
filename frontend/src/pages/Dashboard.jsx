import { useMemo } from 'react';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';

import './Dashboard.css';

export default function Dashboard() {
  const dashboardApiCall = useMemo(
    () => async () => {
      const [summary, byService, resources] = await Promise.all([
        api.getCostSummary(),
        api.getCostByService(),
        api.getTopExpensiveResources(),
      ]);

      return {
        summary,
        byService,
        resources,
      };
    },
    []
  );

  const {
    data,
    loading,
    error,
  } = useApi(dashboardApiCall);

  const costSummary = data?.summary || {};
  const costByService = data?.byService?.data || [];
  const topResources = data?.resources?.data || [];

  if (loading) {
    return (
      <div className="dashboard-container">
        <LoadingState message="Loading dashboard analytics..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <ErrorState
          title="Error Loading Dashboard"
          message={error}
        />
      </div>
    );
  }

  const totalCost = costSummary?.total_cost || 0;
  const changePercent = costSummary?.cost_change_percent || 0;

  return (
    <div className="dashboard-container">
      <h1>Cost Overview</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div>Total Cost</div>

          <div>
            ${totalCost.toFixed(2)}
          </div>

          <div>
            {changePercent.toFixed(1)}%
          </div>
        </div>

        <div className="stat-card">
          <div>Services</div>

          <div>
            {costByService.length}
          </div>
        </div>

        <div className="stat-card">
          <div>Resources</div>

          <div>
            {topResources.length}
          </div>
        </div>
      </div>

      <h2>Top Services</h2>

      {costByService.slice(0, 5).map((service) => (
        <div key={service.service_name}>
          {service.service_name} - $
          {service.total_cost.toFixed(2)}
        </div>
      ))}

      <h2>Top Resources</h2>

      {topResources.slice(0, 5).map((resource) => (
        <div key={resource.resource_id}>
          {resource.name} - $
          {resource.total_cost.toFixed(2)}
        </div>
      ))}
    </div>
  );
}