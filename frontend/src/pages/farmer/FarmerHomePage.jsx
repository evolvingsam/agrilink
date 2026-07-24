import { useQuery } from '@tanstack/react-query';
import { marketApi } from '../../api';
import { useAuthStore } from '../../store/authStore';
import { formatNGN, getTrendIcon, getTrendClass } from '../../utils/helpers';
import { Link } from 'react-router-dom';
import './FarmerHome.css';

export default function FarmerHomePage() {
  const user = useAuthStore((s) => s.user);

  const { data: trends, isLoading } = useQuery({
    queryKey: ['market-trends'],
    queryFn: () => marketApi.getTrends().then((r) => r.data),
    staleTime: 5 * 60 * 1000,
  });

  const alert = trends?.data?.summary_alert;
  const trendList = trends?.data?.trends ?? [];

  return (
    <div className="farmer-home">
      {/* Greeting */}
      <div className="home-greeting">
        <h1 className="page-title">
          Good day, {user?.first_name || user?.username} 🌾
        </h1>
        <p className="page-subtitle">
          Welcome to your AgriLink dashboard. Manage your listings, check prices, and get AI guidance.
        </p>
      </div>

      {/* Market Alert Banner */}
      {isLoading ? null : alert && (
        <div className="market-alert-banner">
          <span className="market-alert-icon">📊</span>
          <div>
            <div className="market-alert-label">Market Intelligence</div>
            <div className="market-alert-text">{alert}</div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2 className="section-title">Quick Actions</h2>
        <div className="quick-action-grid">
          <Link to="/listings/new" className="quick-action-card">
            <span className="quick-action-icon">➕</span>
            <span className="quick-action-label">New Listing</span>
          </Link>
          <Link to="/chat" className="quick-action-card">
            <span className="quick-action-icon">🤖</span>
            <span className="quick-action-label">AI Assistant</span>
          </Link>
          <Link to="/market" className="quick-action-card">
            <span className="quick-action-icon">📈</span>
            <span className="quick-action-label">Prices</span>
          </Link>
          <Link to="/payments" className="quick-action-card">
            <span className="quick-action-icon">💳</span>
            <span className="quick-action-label">Payments</span>
          </Link>
        </div>
      </div>

      {/* Market Trends Preview */}
      <div className="trends-section">
        <div className="section-header">
          <h2 className="section-title">Today's Market Trends</h2>
          <Link to="/market" className="btn btn-secondary btn-sm">View All Prices</Link>
        </div>

        {isLoading ? (
          <div className="loading-center"><span className="spinner" /> Loading trends…</div>
        ) : trendList.length === 0 ? (
          <div className="alert alert-info">No market trend data available yet.</div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Crop</th>
                  <th>Avg Price / kg</th>
                  <th>7-Day Change</th>
                  <th>Direction</th>
                </tr>
              </thead>
              <tbody>
                {trendList.map((t) => (
                  <tr key={t.crop_name}>
                    <td className="font-medium">{t.crop_name}</td>
                    <td>{formatNGN(t.current_avg_price_per_kg)}</td>
                    <td className={getTrendClass(t.trend_direction)}>
                      {getTrendIcon(t.trend_direction)} {t.trend_percentage}
                    </td>
                    <td>
                      <span className={`badge ${t.trend_direction === 'up' ? 'badge-green' : t.trend_direction === 'down' ? 'badge-red' : 'badge-gray'}`}>
                        {t.trend_direction}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
