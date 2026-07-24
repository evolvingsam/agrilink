import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { logisticsApi, ordersApi } from '../../api';
import { formatDateTime } from '../../utils/helpers';

export default function DispatcherHomePage() {
  const queryClient = useQueryClient();
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['routes'],
    queryFn: () => logisticsApi.getRoutes().then((r) => r.data),
  });

  const routes = data?.results ?? [];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 className="page-title">Dispatch Routes</h1>
          <p className="page-subtitle">Manage your assigned delivery routes</p>
        </div>
        <button className="btn btn-secondary" onClick={() => refetch()}>🔄 Refresh</button>
      </div>

      {isLoading ? (
        <div className="loading-center"><span className="spinner" /> Loading routes…</div>
      ) : routes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🚛</div>
          <div className="empty-state-title">No routes assigned</div>
          <p>Routes will appear here once buyers have paid for their orders and the logistics engine generates them.</p>
        </div>
      ) : (
        <div className="grid-2">
          {routes.map((route) => (
            <RouteCard key={route.id} route={route} onStatusChange={() => queryClient.invalidateQueries(['routes'])} />
          ))}
        </div>
      )}
    </div>
  );
}

function RouteCard({ route, onStatusChange }) {
  const [briefing, setBriefing] = useState(null);
  const [loadingBriefing, setLoadingBriefing] = useState(false);
  const [notification, setNotification] = useState('');

  const statusMap = {
    planned: { class: 'badge-blue', label: '📋 Planned' },
    in_transit: { class: 'badge-amber', label: '🚛 In Transit' },
    delivered: { class: 'badge-green', label: '✅ Delivered' },
  };
  const s = statusMap[route.status] || { class: 'badge-gray', label: route.status };

  // Collect all order IDs linked to this route via matches
  const orderIds = route.matches?.map((m) => m.order_id).filter(Boolean) ?? [];

  const acceptMutation = useMutation({
    mutationFn: (orderId) => ordersApi.acceptDelivery(orderId),
    onSuccess: () => {
      showNote('Order accepted! Status moved to Delivery in Process.');
      onStatusChange();
    },
    onError: (err) => showNote(err?.response?.data?.error || 'Failed to accept delivery.', true),
  });

  const completeMutation = useMutation({
    mutationFn: (orderId) => ordersApi.completeDelivery(orderId),
    onSuccess: () => {
      showNote('Order marked as delivered and completed! 🎉');
      onStatusChange();
    },
    onError: (err) => showNote(err?.response?.data?.error || 'Failed to complete delivery.', true),
  });

  function showNote(msg, isError = false) {
    setNotification({ msg, isError });
    setTimeout(() => setNotification(''), 4000);
  }

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

  const isPlanned = route.status === 'planned';
  const isInTransit = route.status === 'in_transit';

  return (
    <div className="card">
      {/* Notification */}
      {notification && (
        <div className={`alert ${notification.isError ? 'alert-error' : 'alert-success'}`} style={{ marginBottom: 'var(--space-3)', fontSize: 'var(--text-sm)' }}>
          {notification.msg}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-3)' }}>
        <div className="font-semibold" style={{ fontSize: 'var(--text-lg)' }}>Route #{route.id}</div>
        <span className={`badge ${s.class}`}>{s.label}</span>
      </div>

      <div className="text-sm text-muted" style={{ marginBottom: 'var(--space-2)' }}>
        📅 Created: {formatDateTime(route.created_at)}
      </div>

      {route.estimated_distance_km && (
        <div className="text-sm text-muted" style={{ marginBottom: 'var(--space-3)' }}>
          📍 Est. distance: {Number(route.estimated_distance_km).toFixed(1)} km
        </div>
      )}

      {/* Waypoints summary */}
      {route.route_waypoints?.length > 0 && (
        <div style={{
          background: 'var(--color-field)', borderRadius: 'var(--radius-sm)',
          padding: 'var(--space-3)', marginBottom: 'var(--space-4)', fontSize: 'var(--text-sm)',
        }}>
          <div style={{ fontWeight: 600, marginBottom: 'var(--space-2)' }}>Waypoints:</div>
          {route.route_waypoints.map((wp, i) => (
            <div key={i} style={{ color: 'var(--color-stone)', marginBottom: 4 }}>
              {i + 1}. {wp.name}
            </div>
          ))}
        </div>
      )}

      {briefing && (
        <div className="alert alert-info" style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-sm)' }}>
          🤖 {briefing}
        </div>
      )}

      {/* Action buttons */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {/* AI Briefing */}
        <button className="btn btn-secondary btn-sm" onClick={loadBriefing} disabled={loadingBriefing}>
          {loadingBriefing ? <span className="spinner" style={{ width: 14, height: 14 }} /> : '🤖 AI Briefing'}
        </button>

        {/* Accept for Delivery — available when route is planned/in_transit and there are orders in processing */}
        {(isPlanned || isInTransit) && orderIds.length > 0 && (
          <button
            className="btn btn-primary btn-sm"
            onClick={() => {
              // Accept all orders on this route
              orderIds.forEach((id) => acceptMutation.mutate(id));
            }}
            disabled={acceptMutation.isPending}
          >
            {acceptMutation.isPending ? <span className="spinner" style={{ width: 14, height: 14 }} /> : '🚛 Accept & Start Delivery'}
          </button>
        )}

        {/* Mark as Delivered — available when in_transit */}
        {isInTransit && orderIds.length > 0 && (
          <button
            className="btn btn-secondary btn-sm"
            style={{ borderColor: 'var(--color-leaf)', color: 'var(--color-leaf)' }}
            onClick={() => {
              if (window.confirm('Mark all orders on this route as delivered?')) {
                orderIds.forEach((id) => completeMutation.mutate(id));
              }
            }}
            disabled={completeMutation.isPending}
          >
            {completeMutation.isPending ? <span className="spinner" style={{ width: 14, height: 14 }} /> : '✅ Mark as Delivered'}
          </button>
        )}
      </div>
    </div>
  );
}
