import { useQuery, useMutation } from '@tanstack/react-query';
import { logisticsApi } from '../../api';
import { formatDateTime } from '../../utils/helpers';

export default function DispatcherHomePage() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['routes'],
    queryFn: () => logisticsApi.getRoutes().then((r) => r.data),
  });

  const routes = data?.results ?? [];

  return (
    <div>
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">Dispatch Routes</h1>
          <p className="page-subtitle">Your assigned delivery routes</p>
        </div>
        <button className="btn btn-secondary" onClick={() => refetch()}>🔄 Refresh</button>
      </div>

      {isLoading ? (
        <div className="loading-center"><span className="spinner" /> Loading routes…</div>
      ) : routes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🚛</div>
          <div className="empty-state-title">No routes assigned</div>
          <p>Routes will appear here once the logistics engine generates them.</p>
        </div>
      ) : (
        <div className="grid-2">
          {routes.map((route) => (
            <RouteCard key={route.id} route={route} />
          ))}
        </div>
      )}
    </div>
  );
}

function RouteCard({ route }) {
  const [briefing, setBriefing] = useState(null);
  const [loadingBriefing, setLoadingBriefing] = useState(false);

  const statusMap = {
    planned: { class: 'badge-blue', label: 'Planned' },
    in_transit: { class: 'badge-amber', label: 'In Transit' },
    delivered: { class: 'badge-green', label: 'Delivered' },
  };
  const s = statusMap[route.status] || { class: 'badge-gray', label: route.status };

  async function loadBriefing() {
    setLoadingBriefing(true);
    try {
      const res = await logisticsApi.getRouteBriefing(route.id);
      setBriefing(res.data.briefing);
    } catch {
      setBriefing('Could not load AI briefing.');
    } finally {
      setLoadingBriefing(false);
    }
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-3)' }}>
        <div className="font-semibold">Route #{route.id}</div>
        <span className={`badge ${s.class}`}>{s.label}</span>
      </div>
      <div className="text-sm text-muted" style={{ marginBottom: 'var(--space-4)' }}>
        Created: {formatDateTime(route.created_at)}
      </div>

      {briefing && (
        <div className="alert alert-info" style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-sm)' }}>
          🤖 {briefing}
        </div>
      )}

      <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
        <button className="btn btn-secondary btn-sm" onClick={loadBriefing} disabled={loadingBriefing}>
          {loadingBriefing ? <span className="spinner" style={{ width: 14, height: 14 }} /> : '🤖 AI Briefing'}
        </button>
      </div>
    </div>
  );
}

import { useState } from 'react';
