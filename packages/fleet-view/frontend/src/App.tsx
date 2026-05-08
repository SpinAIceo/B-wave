import { useState } from 'react';
import './styles.css';
import Dashboard from './pages/Dashboard';
import FleetMap from './pages/FleetMap';
import VesselList from './pages/VesselList';
import Reports from './pages/Reports';
import LogViewer from './pages/LogViewer';
import LanguageSwitcher from './components/LanguageSwitcher';
import { useT } from './lib/i18n';

type Page = 'dashboard' | 'map' | 'vessels' | 'reports' | 'logs';

export default function App() {
  const t = useT();
  const [page, setPage] = useState<Page>('dashboard');

  const NAV_ITEMS: { id: Page; label: string; icon: string }[] = [
    { id: 'dashboard', label: t('navDashboard'), icon: '📊' },
    { id: 'map', label: t('navFleetMap'), icon: '🗺️' },
    { id: 'vessels', label: t('navVessels'), icon: '🚢' },
    { id: 'reports', label: t('navReports'), icon: '📋' },
    { id: 'logs', label: t('navLogs'), icon: '🔴' },
  ];

  const renderPage = () => {
    switch (page) {
      case 'dashboard': return <Dashboard />;
      case 'map': return <FleetMap />;
      case 'vessels': return <VesselList />;
      case 'reports': return <Reports />;
      case 'logs': return <LogViewer />;
    }
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>B-Wave</h1>
          <span>{t('appSubtitle')}</span>
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
          <div className="topbar-actions" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <LanguageSwitcher />
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
