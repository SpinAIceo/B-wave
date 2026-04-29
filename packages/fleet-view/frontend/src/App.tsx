import { useState } from 'react';
import './styles.css';
import Dashboard from './pages/Dashboard';
import FleetMap from './pages/FleetMap';
import VesselList from './pages/VesselList';
import Reports from './pages/Reports';

type Page = 'dashboard' | 'map' | 'vessels' | 'reports';

const NAV_ITEMS: { id: Page; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'map', label: 'Fleet Map', icon: '🗺️' },
  { id: 'vessels', label: 'Vessels', icon: '🚢' },
  { id: 'reports', label: 'Reports', icon: '📋' },
];

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');

  const renderPage = () => {
    switch (page) {
      case 'dashboard': return <Dashboard />;
      case 'map': return <FleetMap />;
      case 'vessels': return <VesselList />;
      case 'reports': return <Reports />;
    }
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>B-Wave</h1>
          <span>Fleet View Dashboard</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              className={`nav-item ${page === item.id ? 'active' : ''}`}
              onClick={() => setPage(item.id)}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <div className="main-content">
        <header className="topbar">
          <span className="topbar-title">
            {NAV_ITEMS.find(n => n.id === page)?.label}
          </span>
          <div className="topbar-actions">
            <span style={{ cursor: 'pointer', fontSize: 20 }}>🔔</span>
            <span
              style={{
                width: 32, height: 32, borderRadius: '50%',
                background: 'var(--primary)', display: 'inline-flex',
                alignItems: 'center', justifyContent: 'center',
                fontSize: 14, fontWeight: 700,
              }}
            >
              SM
            </span>
          </div>
        </header>
        <div className="page-content">
          {renderPage()}
        </div>
      </div>
    </div>
  );
}
