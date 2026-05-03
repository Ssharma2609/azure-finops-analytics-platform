import { Link } from 'react-router-dom';
import './Layout.css';

export default function Layout({ children }) {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>💰 Cost Simulator</h1>
        </div>
        <nav className="sidebar-nav">
          <Link to="/" className="nav-link">
            📊 Dashboard
          </Link>
          <Link to="/trends" className="nav-link">
            📈 Cost Trends
          </Link>
          <Link to="/resources" className="nav-link">
            🏗️ Resources
          </Link>
          <Link to="/alerts" className="nav-link">
            🚨 Alerts
          </Link>
        </nav>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
