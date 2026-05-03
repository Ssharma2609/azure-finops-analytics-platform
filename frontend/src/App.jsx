import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css';
import Layout from './components/Layout';
import Alerts from './pages/Alerts';
import CostTrends from './pages/CostTrends';
import Dashboard from './pages/Dashboard';
import Resources from './pages/Resources';
import ServiceAnalytics from "./pages/ServiceAnalytics";

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/trends" element={<CostTrends />} />
      <Route path="/resources" element={<Resources />} />
      <Route path="/alerts" element={<Alerts />} />
      <Route path="/services" element={<ServiceAnalytics />} />
    </Routes>
  );
}

export default function App() {
  return (
    <Router>
      <Layout>
        <AppRoutes />
      </Layout>
    </Router>
  );
}
