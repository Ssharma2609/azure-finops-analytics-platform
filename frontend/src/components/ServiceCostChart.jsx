import { useEffect, useState } from "react";
import {
    Bar,
    BarChart,
    CartesianGrid,
    Legend,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

const ServiceCostChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/cost/by-service")
      .then((res) => res.json())
      .then((result) => {
        setData(result.data || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch service analytics", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p>Loading service analytics...</p>;
  }

  return (
    <div
      style={{
        background: "#ffffff",
        padding: "20px",
        borderRadius: "12px",
        marginTop: "30px",
      }}
    >
      <h2
        style={{
          marginBottom: "20px",
          color: "#333",
        }}
      >
        Azure Cost by Service
      </h2>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="service_name" />

          <YAxis />

          <Tooltip />

          <Legend />

          <Bar
            dataKey="total_cost"
            fill="#a855f7"
            radius={[6, 6, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ServiceCostChart;