import { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { api } from '../services/api';
import './Resources.css';

const COLORS = [
  '#aa3bff',
  '#8b5cf6',
  '#a78bfa',
  '#c4b5fd',
  '#ddd6fe',
  '#9333ea',
  '#7c3aed',
  '#6d28d9',
];

export default function Resources() {
  const [resources, setResources] = useState(null);
  const [costByService, setCostByService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('cost');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = { days: 30 };

        const [resourcesData, servicesData] = await Promise.all([
          api.getTopExpensiveResources({
            ...params,
            limit: 100,
          }),
          api.getCostByService(params),
        ]);

        setResources(resourcesData);
        setCostByService(servicesData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="resources-container">
        <div className="loading">Loading resources...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="resources-container">
        <div className="error">
          <h2>Error Loading Resources</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const resourceList = resources?.data || [];
  const chartData = costByService?.data?.slice(0, 8) || [];

  const sortedResources = [...resourceList].sort((a, b) => {
    if (sortBy === 'cost') {
      return b.total_cost - a.total_cost;
    }

    if (sortBy === 'name') {
      return a.name.localeCompare(b.name);
    }

    if (sortBy === 'service') {
      return a.service_name.localeCompare(b.service_name);
    }

    return 0;
  });

  const topResources = sortedResources.slice(0, 20);

  const totalResourceCost = resourceList.reduce(
    (sum, r) => sum + r.total_cost,
    0
  );

  return (
    <div
      className="resources-container"
      style={{
        background: '#0f172a',
        minHeight: '100vh',
        color: '#ffffff',
        padding: '20px',
      }}
    >
      {/* HEADER */}
      <div
        className="header"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '30px',
          flexWrap: 'wrap',
          gap: '20px',
        }}
      >
        <h1
          style={{
            color: '#ffffff',
            fontSize: '42px',
            fontWeight: '700',
          }}
        >
          Resource Analysis
        </h1>

        <div className="filters">
          <label
            style={{
              color: '#ffffff',
              marginRight: '10px',
              fontWeight: '600',
            }}
          >
            Sort by:
          </label>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
            style={{
              background: '#1e293b',
              color: '#ffffff',
              border: '1px solid #334155',
              padding: '10px',
              borderRadius: '8px',
            }}
          >
            <option value="cost">Cost (High to Low)</option>
            <option value="name">Name (A to Z)</option>
            <option value="service">Service (A to Z)</option>
          </select>
        </div>
      </div>

      {/* CHARTS */}
      <div
        className="charts-grid"
        style={{
          display: 'grid',
          gap: '30px',
        }}
      >
        {/* BAR CHART */}
        <div
          className="chart-card"
          style={{
            background: '#1e293b',
            borderRadius: '20px',
            padding: '25px',
          }}
        >
          <h2
            style={{
              color: '#ffffff',
              fontSize: '28px',
              fontWeight: '700',
              marginBottom: '20px',
            }}
          >
            Top 8 Services by Cost
          </h2>

          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#334155"
              />

              <XAxis
                dataKey="service_name"
                tick={{
                  fill: '#ffffff',
                  fontSize: 12,
                }}
                angle={-35}
                textAnchor="end"
                height={90}
              />

              <YAxis
                tick={{
                  fill: '#ffffff',
                  fontSize: 12,
                }}
              />

              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #7c3aed',
                  borderRadius: '10px',
                  color: '#ffffff',
                }}
                labelStyle={{
                  color: '#ffffff',
                }}
                formatter={(value) => [
                  `$${Number(value).toFixed(2)}`,
                  'Total Cost',
                ]}
              />

              <Bar
                dataKey="total_cost"
                radius={[10, 10, 0, 0]}
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* PIE CHART */}
        {chartData.length > 0 && (
          <div
            className="chart-card"
            style={{
              background: '#1e293b',
              borderRadius: '20px',
              padding: '25px',
            }}
          >
            <h2
              style={{
                color: '#ffffff',
                fontSize: '28px',
                fontWeight: '700',
                marginBottom: '20px',
              }}
            >
              Service Cost Distribution
            </h2>

            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  outerRadius={120}
                  dataKey="total_cost"
                  label={({ percent }) =>
                    `${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>

                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #7c3aed',
                    borderRadius: '10px',
                    color: '#ffffff',
                  }}
                  formatter={(value) => [
                    `$${Number(value).toFixed(2)}`,
                    'Total Cost',
                  ]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* TABLE SECTION */}
      <div
        className="resources-section"
        style={{
          marginTop: '40px',
        }}
      >
        <h2
          style={{
            color: '#ffffff',
            fontSize: '32px',
            fontWeight: '700',
            marginBottom: '20px',
          }}
        >
          Top {Math.min(20, resourceList.length)} Expensive Resources
        </h2>

        <div
          className="resources-table"
          style={{
            background: '#1e293b',
            borderRadius: '16px',
            overflow: 'hidden',
          }}
        >
          {/* TABLE HEADER */}
          <div
            className="table-header"
            style={{
              display: 'grid',
              gridTemplateColumns: '80px 2fr 2fr 1fr 1fr',
              padding: '20px',
              background: '#111827',
              color: '#ffffff',
              fontWeight: '700',
              borderBottom: '1px solid #334155',
            }}
          >
            <div>#</div>
            <div>RESOURCE NAME</div>
            <div>SERVICE</div>
            <div>COST (30D)</div>
            <div>% OF TOTAL</div>
          </div>

          {/* TABLE ROWS */}
          {topResources.map((resource, index) => (
            <div
              key={resource.resource_id}
              className="table-row"
              style={{
                display: 'grid',
                gridTemplateColumns: '80px 2fr 2fr 1fr 1fr',
                padding: '20px',
                borderBottom: '1px solid #334155',
                alignItems: 'center',
              }}
            >
              <div
                style={{
                  color: '#a855f7',
                  fontWeight: '700',
                  fontSize: '24px',
                }}
              >
                {index + 1}
              </div>

              <div
                style={{
                  color: '#ffffff',
                  fontWeight: '600',
                }}
              >
                {resource.name}
              </div>

              <div
                style={{
                  color: '#cbd5e1',
                }}
              >
                {resource.service_name}
              </div>

              <div
                style={{
                  color: '#c084fc',
                  fontWeight: '700',
                }}
              >
                ${resource.total_cost.toFixed(2)}
              </div>

              <div
                style={{
                  color: '#e2e8f0',
                }}
              >
                {totalResourceCost > 0
                  ? (
                      (resource.total_cost / totalResourceCost) *
                      100
                    ).toFixed(1)
                  : '0'}
                %
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SUMMARY CARDS */}
      <div
        className="summary-cards"
        style={{
          display: 'grid',
          gridTemplateColumns:
            'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px',
          marginTop: '40px',
        }}
      >
        <div
          className="summary-card"
          style={{
            background: '#1e293b',
            padding: '25px',
            borderRadius: '16px',
            border: '1px solid #334155',
          }}
        >
          <div
            style={{
              color: '#cbd5e1',
              fontSize: '16px',
              marginBottom: '10px',
            }}
          >
            Total Resources
          </div>

          <div
            style={{
              color: '#ffffff',
              fontSize: '32px',
              fontWeight: '700',
            }}
          >
            {resourceList.length}
          </div>
        </div>

        <div
          className="summary-card"
          style={{
            background: '#1e293b',
            padding: '25px',
            borderRadius: '16px',
            border: '1px solid #334155',
          }}
        >
          <div
            style={{
              color: '#cbd5e1',
              fontSize: '16px',
              marginBottom: '10px',
            }}
          >
            Total Cost (30d)
          </div>

          <div
            style={{
              color: '#a855f7',
              fontSize: '32px',
              fontWeight: '700',
            }}
          >
            ${totalResourceCost.toFixed(2)}
          </div>
        </div>

        <div
          className="summary-card"
          style={{
            background: '#1e293b',
            padding: '25px',
            borderRadius: '16px',
            border: '1px solid #334155',
          }}
        >
          <div
            style={{
              color: '#cbd5e1',
              fontSize: '16px',
              marginBottom: '10px',
            }}
          >
            Average Cost per Resource
          </div>

          <div
            style={{
              color: '#ffffff',
              fontSize: '32px',
              fontWeight: '700',
            }}
          >
            $
            {resourceList.length > 0
              ? (
                  totalResourceCost / resourceList.length
                ).toFixed(2)
              : '0'}
          </div>
        </div>

        <div
          className="summary-card"
          style={{
            background: '#1e293b',
            padding: '25px',
            borderRadius: '16px',
            border: '1px solid #334155',
          }}
        >
          <div
            style={{
              color: '#cbd5e1',
              fontSize: '16px',
              marginBottom: '10px',
            }}
          >
            Unique Services
          </div>

          <div
            style={{
              color: '#ffffff',
              fontSize: '32px',
              fontWeight: '700',
            }}
          >
            {costByService?.data?.length || 0}
          </div>
        </div>
      </div>
    </div>
  );
}