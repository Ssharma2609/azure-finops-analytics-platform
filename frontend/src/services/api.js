const API_BASE_URL = import.meta.env.VITE_API_URL;

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log("API CALL:", url);
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Health Endpoints
  health() {
    return this.request('/health');
  }

  ready() {
    return this.request('/health/ready');
  }

  // Cost Endpoints
  getCostSummary(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/cost/summary${query ? '?' + query : ''}`);
  }

  getCostTrends(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/cost/trend${query ? '?' + query : ''}`);
  }

  getCostByService(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/cost/by-service${query ? '?' + query : ''}`);
  }

  getCostBySubscription(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/cost/by-subscription${query ? '?' + query : ''}`);
  }

  // Resource Endpoints
  getTopExpensiveResources(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/resources/top-expensive${query ? '?' + query : ''}`);
  }

  getResourceDetail(resourceId, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/resources/${resourceId}${query ? '?' + query : ''}`);
  }

  // Alert Endpoints
  detectCostAnomaly(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/alerts/anomalies${query ? '?' + query : ''}`);
  }

  // Analytics Endpoints
  forecastCosts(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/analytics/forecast${query ? '?' + query : ''}`);
  }

  getRecommendations(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/analytics/recommendations${query ? '?' + query : ''}`);
  }
}

export const api = new ApiClient();
