import axios from 'axios';
import { useMemo } from 'react';

import { useFilter } from '../context/FilterContext';
import { useApi } from '../hooks/useApi';

import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_URL;

const CostTrends = () => {
  const { dateRange, setDateRange } = useFilter();

  const days =
    dateRange === '7d'
      ? 7
      : dateRange === '90d'
      ? 90
      : 30;

  const trendApiCall = useMemo(
    () => async () => {
      const [trendResponse, forecastResponse] =
        await Promise.all([
          axios.get(
            `${API_BASE_URL}/cost/trend?days=${days}`
          ),

          axios.get(
            `${API_BASE_URL}/analytics/forecast`
          ),
        ]);

      return {
        trend: trendResponse.data,
        forecast: forecastResponse.data,
      };
    },
    [days]
  );

  const {
    data,
    loading,
    error,
  } = useApi(trendApiCall, [days]);

  const historicalData =
    data?.trend?.data?.map((item) => ({
      ...item,
      cost: Number(item.cost),
    })) || [];

  const forecastData =
    data?.forecast?.forecast_data?.map((item) => ({
      date: item.date,
      predicted_cost: Number(item.predicted_cost),
      lower_bound: Number(item.lower_bound),
      upper_bound: Number(item.upper_bound),
    })) || [];

  const costs = historicalData.map(
    (item) => item.cost
  );

  const total = costs.reduce(
    (acc, value) => acc + value,
    0
  );

  const summary = {
    total,
    average: costs.length
      ? total / costs.length
      : 0,
    highest: costs.length
      ? Math.max(...costs)
      : 0,
    lowest: costs.length
      ? Math.min(...costs)
      : 0,
  };

  const formatCurrency = (value) => {
    return `$${value.toFixed(2)}`;
  };

  if (loading) {
    return (
      <div
        style={{
          background: '#0f111a',
          minHeight: '100vh',
        }}
      >
        <LoadingState message="Loading cost analytics..." />
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          background: '#0f111a',
          minHeight: '100vh',
          padding: '30px',
        }}
      >
        <ErrorState
          title="Failed to Load Cost Trends"
          message={error}
        />
      </div>
    );
  }

  return (
    <div
      style={{
        padding: '30px',
        background: '#0f111a',
        minHeight: '100vh',
        color: 'white',
      }}
    >
      {/* HEADER */}

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '30px',
        }}
      >
        <h1
          style={{
            fontSize: '52px',
            fontWeight: '700',
            margin: 0,
          }}
        >
          Cost Trends & Forecast
        </h1>

        <div
          style={{
            display: 'flex',
            gap: '12px',
          }}
        >
          {[7, 30, 90].map((value) => (
            <button
              key={value}
              onClick={() => {
                if (value === 7) {
                  setDateRange('7d');
                }

                if (value === 30) {
                  setDateRange('30d');
                }

                if (value === 90) {
                  setDateRange('90d');
                }
              }}
              style={{
                padding: '12px 24px',
                borderRadius: '10px',
                border: 'none',
                cursor: 'pointer',
                background:
                  days === value
                    ? '#a855f7'
                    : '#ffffff',
                color:
                  days === value
                    ? '#ffffff'
                    : '#555',
                fontWeight: '600',
                fontSize: '16px',
              }}
            >
              {value} Days
            </button>
          ))}
        </div>
      </div>

      {/* DAILY TREND CHART */}

      <div
        style={{
          background: '#1e293b',
          borderRadius: '24px',
          padding: '25px',
          marginBottom: '40px',
          border: '1px solid #334155',
          boxShadow: '0 10px 30px rgba(0,0,0,0.35)',
        }}
      >
        <h2
          style={{
            color: '#f8fafc',
            marginBottom: '20px',
          }}
        >
          Daily Cost Trend
        </h2>

        <ResponsiveContainer width="100%" height={420}>
          <AreaChart data={historicalData}>
            <defs>
              <linearGradient
                id="costGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="0%"
                  stopColor="#a855f7"
                  stopOpacity={0.8}
                />

                <stop
                  offset="100%"
                  stopColor="#a855f7"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="5 5"
              stroke="#334155"
            />

            <XAxis
              dataKey="date"
              tick={{ fill: '#cbd5e1' }}
              axisLine={{ stroke: '#475569' }}
              tickLine={{ stroke: '#475569' }}
            />

            <YAxis
              tick={{ fill: '#cbd5e1' }}
              axisLine={{ stroke: '#475569' }}
              tickLine={{ stroke: '#475569' }}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid #7c3aed',
                borderRadius: '12px',
                color: '#ffffff',
              }}
            />

            <Area
              type="monotone"
              dataKey="cost"
              stroke="#a855f7"
              fill="url(#costGradient)"
              strokeWidth={3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* FORECAST CHART */}

      <div
        style={{
          background: '#1e293b',
          borderRadius: '24px',
          padding: '25px',
          marginBottom: '40px',
          border: '1px solid #334155',
          boxShadow: '0 10px 30px rgba(0,0,0,0.35)',
        }}
      >
        <h2
          style={{
            color: '#f8fafc',
            marginBottom: '20px',
          }}
        >
          Cost Forecast (Next 7 Days)
        </h2>

        <ResponsiveContainer width="100%" height={420}>
          <LineChart data={forecastData}>
            <CartesianGrid
              strokeDasharray="5 5"
              stroke="#334155"
            />

            <XAxis
              dataKey="date"
              tick={{ fill: '#cbd5e1' }}
              axisLine={{ stroke: '#475569' }}
              tickLine={{ stroke: '#475569' }}
            />

            <YAxis
              tick={{ fill: '#cbd5e1' }}
              axisLine={{ stroke: '#475569' }}
              tickLine={{ stroke: '#475569' }}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid #7c3aed',
                borderRadius: '12px',
                color: '#ffffff',
              }}
            />

            <Legend />

            <Line
              type="monotone"
              dataKey="predicted_cost"
              name="Forecast"
              stroke="#8b5cf6"
              strokeWidth={4}
              dot={{
                r: 5,
              }}
            />

            <Line
              type="monotone"
              dataKey="lower_bound"
              name="Lower Bound"
              stroke="#06b6d4"
              strokeWidth={3}
              strokeDasharray="5 5"
              dot={false}
            />

            <Line
              type="monotone"
              dataKey="upper_bound"
              name="Upper Bound"
              stroke="#f59e0b"
              strokeWidth={3}
              strokeDasharray="5 5"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* SUMMARY SECTION */}

      <div>
        <h2
          style={{
            marginBottom: '25px',
            fontSize: '36px',
          }}
        >
          Summary Statistics
        </h2>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns:
              'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '24px',
          }}
        >
          <div style={cardStyle}>
            <p style={labelStyle}>
              CURRENT PERIOD TOTAL
            </p>

            <h2 style={valueStyle}>
              {formatCurrency(summary.total)}
            </h2>
          </div>

          <div style={cardStyle}>
            <p style={labelStyle}>
              DAILY AVERAGE
            </p>

            <h2 style={valueStyle}>
              {formatCurrency(summary.average)}
            </h2>
          </div>

          <div style={cardStyle}>
            <p style={labelStyle}>
              HIGHEST DAILY COST
            </p>

            <h2 style={valueStyle}>
              {formatCurrency(summary.highest)}
            </h2>
          </div>

          <div style={cardStyle}>
            <p style={labelStyle}>
              LOWEST DAILY COST
            </p>

            <h2 style={valueStyle}>
              {formatCurrency(summary.lowest)}
            </h2>
          </div>
        </div>
      </div>
    </div>
  );
};

const cardStyle = {
  background: '#1e293b',
  border: '1px solid #334155',
  boxShadow: '0 10px 30px rgba(0,0,0,0.35)',
  borderRadius: '18px',
  padding: '35px',
  textAlign: 'center',
};

const labelStyle = {
  color: '#cbd5e1',
  fontSize: '14px',
  fontWeight: '600',
  marginBottom: '12px',
};

const valueStyle = {
  color: '#a855f7',
  fontSize: '42px',
  fontWeight: '700',
  margin: 0,
};

export default CostTrends;