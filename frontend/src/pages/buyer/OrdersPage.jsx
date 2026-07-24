import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ordersApi, matchingApi } from '../../api';
import { formatNGN, formatDate, formatDateTime } from '../../utils/helpers';

function OrderRow({ order }) {
  const [expanded, setExpanded] = useState(false);

  const { data: matches } = useQuery({
    queryKey: ['matches', order.id],
    queryFn: () => matchingApi.getResults(order.id).then((r) => r.data),
    enabled: expanded,
  });

  const statusClass = {
    OPEN: 'badge-blue',
    MATCHED: 'badge-amber',
    COMPLETED: 'badge-green',
    CANCELLED: 'badge-red',
  }[order.status] || 'badge-gray';

  return (
    <>
      <tr style={{ cursor: 'pointer' }} onClick={() => setExpanded((x) => !x)}>
        <td className="font-medium">#{order.id}</td>
        <td>{order.crop_name || `Crop #${order.crop_type}`}</td>
        <td>{order.quantity_kg} kg</td>
        <td>{formatNGN(order.max_price_per_kg)}/kg max</td>
        <td><span className={`badge ${statusClass}`}>{order.status}</span></td>
        <td className="text-sm text-muted">{formatDateTime(order.created_at)}</td>
        <td>{expanded ? '▲' : '▼'}</td>
      </tr>
      {expanded && (
        <tr>
          <td colSpan={7} style={{ background: 'var(--color-field)', padding: 'var(--space-4)' }}>
            <strong style={{ fontSize: 'var(--text-sm)' }}>Matched Listings:</strong>
            {!matches ? (
              <span className="text-muted text-sm" style={{ marginLeft: 8 }}>Loading…</span>
            ) : matches.length === 0 ? (
              <span className="text-muted text-sm" style={{ marginLeft: 8 }}>No matches yet. The matching engine will run shortly.</span>
            ) : (
              <div style={{ marginTop: 'var(--space-3)', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                {matches.map((m) => (
                  <div key={m.id} style={{ fontSize: 'var(--text-sm)', display: 'flex', gap: 'var(--space-4)' }}>
                    <span>🌾 Farmer: {m.farmer_name}</span>
                    <span>{formatNGN(m.price_per_kg)}/kg</span>
                    <span>Grade {m.quality_grade}</span>
                    <span className={`badge ${m.status === 'delivered' ? 'badge-green' : 'badge-amber'}`}>{m.status}</span>
                  </div>
                ))}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  );
}

export default function OrdersPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['orders', page],
    queryFn: () => ordersApi.getOrders({ page }).then((r) => r.data),
    keepPreviousData: true,
  });

  const orders = data?.results ?? [];
  const totalPages = data?.count ? Math.ceil(data.count / 20) : 1;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Orders</h1>
        <p className="page-subtitle">Click any row to expand and see matched farmer listings</p>
      </div>

      {isLoading ? (
        <div className="loading-center"><span className="spinner" /> Loading orders…</div>
      ) : orders.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <div className="empty-state-title">No orders yet</div>
          <p>Place your first order from the marketplace.</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Crop</th>
                  <th>Qty</th>
                  <th>Max Price</th>
                  <th>Status</th>
                  <th>Placed</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => <OrderRow key={o.id} order={o} />)}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button className="pagination-btn" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>← Prev</button>
              <span className="text-sm text-muted">Page {page} of {totalPages}</span>
              <button className="pagination-btn" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next →</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
