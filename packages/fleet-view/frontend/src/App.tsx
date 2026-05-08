import { lazy, Suspense, useState } from 'react';
import './styles.css';
import Dashboard from './pages/Dashboard';
import VesselList from './pages/VesselList';
import Reports from './pages/Reports';
import LogViewer from './pages/LogViewer';
import Login from './pages/Login';
import LanguageSwitcher from './components/LanguageSwitcher';
import { useT } from './lib/i18n';
import { useAuth } from './lib/AuthProvider';

// FleetMap pulls in mapbox-gl (~700 KB). Lazy-load so users who never visit
// the map tab don't pay that bandwidth on first load.
const FleetMap = lazy(() => import('./pages/FleetMap'));

type Page = 'dashboard' | 'map' | 'vessels' | 'reports' | 'logs';

export default function App() {
  const t = useT();
  const { isAuthenticated, user, logout } = useAuth();
  const [page, setPage] = useState<Page>('dashboard');

  if (!isAuthenticated) {
    return <Login />;
  }

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
      case 'map':
        return (
          <Suspense fallback={<div>{t('loading')}</div>}>
            <FleetMap />
          </Suspense>
        );
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
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ textAlign: 'right', lineHeight: 1.2 }}>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{user?.username}</div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  {user?.role}
                </div>
              </div>
              <button
                onClick={logout}
                title={t('logout')}
                style={{
                  background: 'transparent', border: '1px solid var(--border)',
                  color: 'var(--text-secondary)', padding: '6px 10px',
                  borderRadius: 6, cursor: 'pointer', fontSize: 12,
                }}
              >
                {t('logout')}
              </button>
            </div>
          </div>
        </header>
        <div className="page-content">
          {renderPage()}
        </div>
      </div>
    </div>
  );
}
