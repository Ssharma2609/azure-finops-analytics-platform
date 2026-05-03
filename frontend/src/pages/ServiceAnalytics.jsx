import axios from "axios";
import { useEffect, useState } from "react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const COLORS = [
  "#a855f7",
  "#9333ea",
  "#c084fc",
  "#d8b4fe",
  "#7e22ce",
  "#6b21a8",
  "#8b5cf6",
  "#7c3aed",
];

const ServiceAnalytics = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  const [summary, setSummary] = useState({
    totalCost: 0,
    totalServices: 0,
    topService: "",
    topServiceCost: 0,
  });

  useEffect(() => {
    fetchServiceData();
  }, []);

  const fetchServiceData = async () => {
    try {
      setLoading(true);

      const response = await axios.get(
        "http://localhost:8000/api/v1/cost/by-service"
      );

      const data = response.data.data || [];

      setServices(data);

      if (data.length > 0) {
        const highest = data.reduce((prev, current) =>
          current.total_cost > prev.total_cost ? current : prev
        );

        const totalCost = data.reduce(
          (sum, item) => sum + item.total_cost,
          0
        );

        setSummary({
          totalCost,
          totalServices: data.length,
          topService: highest.service_name,
          topServiceCost: highest.total_cost,
        });
      }
    } catch (error) {
      console.error("Failed to fetch service analytics", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return `$${Number(value).toLocaleString(undefined, {
      maximumFractionDigits: 0,
    })}`;
  };

  if (loading) {
    return (
      <div
        style={{
          color: "white",
          padding: "40px",
          fontSize: "24px",
        }}
      >
        Loading Service Analytics...
      </div>
    );
  }

  return (
    <div
      style={{
        background: "#0f172a",
        minHeight: "100vh",
        padding: "30px",
        color: "white",
      }}
    >
      {/* HEADER */}
      <div style={{ marginBottom: "30px" }}>
        <h1
          style={{
            fontSize: "48px",
            fontWeight: "700",
            marginBottom: "10px",
          }}
        >
          Service Cost Analytics
        </h1>

        <p
          style={{
            color: "#94a3b8",
            fontSize: "18px",
          }}
        >
          Azure service spending intelligence dashboard
        </p>
      </div>

      {/* SUMMARY CARDS */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "20px",
          marginBottom: "40px",
        }}
      >
        <div className="summary-card">
          <h3>Total Cost</h3>
          <h2>{formatCurrency(summary.totalCost)}</h2>
        </div>

        <div className="summary-card">
          <h3>Total Services</h3>
          <h2>{summary.totalServices}</h2>
        </div>

        <div className="summary-card">
          <h3>Top Cost Service</h3>
          <h2>{summary.topService}</h2>
        </div>

        <div className="summary-card">
          <h3>Top Service Cost</h3>
          <h2>{formatCurrency(summary.topServiceCost)}</h2>
        </div>
      </div>

      {/* BAR CHART */}
      <div
        style={{
          background: "#1e293b",
          borderRadius: "20px",
          padding: "25px",
          marginBottom: "40px",
        }}
      >
        <h2
          style={{
            marginBottom: "20px",
            fontSize: "28px",
          }}
        >
          Cost By Azure Service
        </h2>

        <ResponsiveContainer width="100%" height={500}>
          <BarChart  
            data={services}
            margin={{
              top: 20,
              right: 30,
              left: 40,
              bottom: 100,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#334155"
            />

            <XAxis
              dataKey="service_name"
              stroke="#cbd5e1"
              angle={-20}
              textAnchor="end"
              interval={0}
              height={100}
              tick={{ fontSize: 11 }}
            />

            <YAxis
              stroke="#cbd5e1"
              tickFormatter={(value) => `$${value / 1000}k`}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                border: "1px solid #7c3aed",
                borderRadius: "10px",
                color: "#fff",
              }}
              formatter={(value) => [
                `$${Number(value).toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`,
                "Total Cost",
              ]}
            />

            <Legend />

            <Bar
              dataKey="total_cost"
              radius={[8, 8, 0, 0]}
            >
              {services.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* TABLE */}
      <div
        style={{
          background: "#1e293b",
          borderRadius: "20px",
          padding: "25px",
        }}
      >
        <h2
          style={{
            marginBottom: "20px",
            fontSize: "28px",
          }}
        >
          Service Breakdown
        </h2>

        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >
            <thead>
              <tr
                style={{
                  borderBottom: "1px solid #334155",
                }}
              >
                <th className="table-head">Service</th>
                <th className="table-head">Category</th>
                <th className="table-head">Total Cost</th>
                <th className="table-head">Resources</th>
                <th className="table-head">% Of Total</th>
              </tr>
            </thead>

            <tbody>
              {services.map((service, index) => (
                <tr
                  key={index}
                  style={{
                    borderBottom: "1px solid #334155",
                  }}
                >
                  <td className="table-cell">
                    {service.service_name}
                  </td>

                  <td className="table-cell">
                    {service.service_category}
                  </td>

                  <td className="table-cell">
                    {formatCurrency(service.total_cost)}
                  </td>

                  <td className="table-cell">
                    {service.resource_count}
                  </td>

                  <td className="table-cell">
                    {Number(
                      service.percentage_of_total
                    ).toFixed(2)}
                    %
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* STYLES */}
      <style>{`
        .summary-card {
          background: #1e293b;
          padding: 25px;
          border-radius: 20px;
          border: 1px solid #334155;
        }

        .summary-card h3 {
          color: #94a3b8;
          margin-bottom: 15px;
          font-size: 18px;
        }

        .summary-card h2 {
          color: #c084fc;
          font-size: 32px;
          margin: 0;
        }

        .table-head {
          text-align: left;
          padding: 16px;
          color: #cbd5e1;
          font-size: 16px;
        }

        .table-cell {
          padding: 16px;
          color: white;
        }
      `}</style>
    </div>
  );
};

export default ServiceAnalytics;