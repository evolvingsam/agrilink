import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ordersApi, matchingApi } from '../../api';
import { useAuthStore } from '../../store/authStore';
import { formatNGN, formatDate, formatDateTime } from '../../utils/helpers';

/* ─── Status config ─── */
const STATUS_CONFIG = {
  OPEN: {
    badge: 'badge-blue',
    label: 'Open — No Match Yet',
    icon: '🔍',
    description: 'The AI is looking for a matching produce listing.',
  },
  WAITING_FOR_PAYMENT: {
    badge: 'badge-amber',
    label: 'Awaiting Payment',
    icon: '💳',
    description: 'A match was found! Pay to confirm your order.',
  },
  PROCESSING: {
    badge: 'badge-purple',
    label: 'Processing',
    icon: '⚙️',
    description: 'Payment received. Waiting for a dispatcher to accept delivery.',
  },
  DELIVERY_IN_PROCESS: {
    badge: 'badge-blue',
    label: 'Delivery in Progress',
    icon: '🚛',
    description: 'A dispatcher has picked up your order and is on the way.',
  },
  COMPLETED: {
    badge: 'badge-green',
    label: 'Completed',
    icon: '✅',
    description: 'Order delivered and completed.',
  },
  CANCELLED: {
    badge: 'badge-red',
    label: 'Cancelled',
    icon: '✕',
    description: 'This order was cancelled.',
  },
};

/* ─── Payment modal overlay ─── */
function PaymentModal({ order, onClose, onSuccess }) {
  const queryClient = useQueryClient();
  const { updateWalletBalance } = useAuthStore();
  const [phase, setPhase] = useState('confirm'); // confirm | processing | done | error
  const [errorMsg, setErrorMsg] = useState('');

  const cost = Number(order.quantity_kg) * Number(order.max_price_per_kg);

  async function handlePay() {
    setPhase('processing');
    try {
      const res = await ordersApi.payOrder(order.id);
      // Animate for 2 seconds before showing success
      await new Promise((r) => setTimeout(r, 2000));
      setPhase('done');
      // Update the user wallet in the store so navbar shows new balance immediately
      updateWalletBalance(res.data.new_wallet_balance);
      queryClient.invalidateQueries(['orders']);
      setTimeout(() => {
        onSuccess(res.data.message);
        onClose();
      }, 1500);
    } catch (err) {
      const msg = err?.response?.data?.error || 'Payment failed. Please try again.';
      setErrorMsg(msg);
      setPhase('error');
    }
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 500,
    }}>
      <div style={{
        background: 'var(--color-white)', borderRadius: 'var(--radius-lg)',
        border: 'var(--border-2)', padding: 'var(--space-8)', width: 360,
        maxWidth: '90vw', textAlign: 'center', boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
      }}>
        {phase === 'confirm' && (
          <>
            <div style={{ fontSize: '2.5rem', marginBottom: 'var(--space-3)' }}>💳</div>
            <h2 style={{ marginBottom: 'var(--space-2)', fontSize: 'var(--text-lg)' }}>Confirm Payment</h2>
            <p style={{ color: 'var(--color-stone)', marginBottom: 'var(--space-5)', fontSize: 'var(--text-sm)' }}>
              Order #{order.id} · {order.crop_name} · {order.quantity_kg} kg
            </p>
            <div style={{
              background: 'var(--color-field)', borderRadius: 'var(--radius-sm)',
              padding: 'var(--space-4)', marginBottom: 'var(--space-6)',
            }}>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-stone)' }}>Total to pay</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-leaf)' }}>
                {formatNGN(cost)}
              </div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-stone)', marginTop: 4 }}>
                ({order.quantity_kg} kg × {formatNGN(order.max_price_per_kg)}/kg)
              </div>
            </div>
            <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
              <button className="btn btn-secondary w-full" onClick={onClose}>Cancel</button>
              <button className="btn btn-primary w-full" onClick={handlePay}>Pay Now</button>
            </div>
          </>
        )}

        {phase === 'processing' && (
          <>
            <div style={{ marginBottom: 'var(--space-4)' }}>
              <span className="spinner" style={{ width: 48, height: 48, borderWidth: 4 }} />
            </div>
            <h2 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-2)' }}>Processing Payment…</h2>
            <p style={{ color: 'var(--color-stone)', fontSize: 'var(--text-sm)' }}>
              Please wait while we securely process your transaction.
            </p>
          </>
        )}

        {phase === 'done' && (
          <>
            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-3)', animation: 'pulse 0.5s ease' }}>✅</div>
            <h2 style={{ fontSize: 'var(--text-lg)', color: 'var(--color-leaf)' }}>Payment Successful!</h2>
            <p style={{ color: 'var(--color-stone)', fontSize: 'var(--text-sm)', marginTop: 'var(--space-2)' }}>
              Your order is now being processed. A dispatcher will pick it up shortly.
            </p>
          </>
        )}

        {phase === 'error' && (
          <>
            <div style={{ fontSize: '2.5rem', marginBottom: 'var(--space-3)' }}>⚠️</div>
            <h2 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-2)' }}>Payment Failed</h2>
            <p style={{ color: 'var(--color-rust)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-5)' }}>
              {errorMsg}
            </p>
            <button className="btn btn-secondary w-full" onClick={onClose}>Close</button>
          </>
        )}
      </div>
    </div>
  );
}

/* ─── Status timeline bar ─── */
const PIPELINE = ['open', 'waiting_for_payment', 'processing', 'delivery_in_process', 'completed'];
const PIPELINE_LABELS = ['Queued', 'Awaiting Payment', 'Processing', 'In Delivery', 'Completed'];

function StatusTimeline({ currentStatus }) {
  const currentIndex = PIPELINE.indexOf(currentStatus);
  if (currentStatus === 'cancelled') {
    return (
      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-rust)', marginTop: 'var(--space-3)' }}>
        ✕ Order was cancelled
      </div>
    );
  }
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0, marginTop: 'var(--space-3)', overflowX: 'auto' }}>
      {PIPELINE_LABELS.map((label, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', flex: i < PIPELINE_LABELS.length - 1 ? 1 : 'unset' }}>
          <div style={{ textAlign: 'center', minWidth: 56 }}>
            <div style={{
              width: 20, height: 20, borderRadius: '50%', margin: '0 auto 4px',
              background: i <= currentIndex ? 'var(--color-leaf)' : 'var(--color-border)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 10, color: '#fff', fontWeight: 700,
            }}>
              {i < currentIndex ? '✓' : i === currentIndex ? '●' : ''}
            </div>
            <div style={{
              fontSize: 9, color: i <= currentIndex ? 'var(--color-leaf)' : 'var(--color-stone)',
              fontWeight: i === currentIndex ? 700 : 400, lineHeight: 1.2,
            }}>
              {label}
            </div>
          </div>
          {i < PIPELINE_LABELS.length - 1 && (
            <div style={{
              flex: 1, height: 2, marginBottom: 14,
              background: i < currentIndex ? 'var(--color-leaf)' : 'var(--color-border)',
            }} />
          )}
        </div>
      ))}
    </div>
  );
}

/* ─── Order row ─── */
function OrderRow({ order, onPay, onCancel }) {
  const [expanded, setExpanded] = useState(false);
  const statusKey = order.status.toUpperCase();
  const cfg = STATUS_CONFIG[statusKey] || { badge: 'badge-gray', label: order.status, icon: '?', description: '' };

  const { data: matchesData } = useQuery({
    queryKey: ['matches', order.id],
    queryFn: () => matchingApi.getResults(order.id).then((r) => r.data),
    enabled: expanded,
  });

  const matches = matchesData?.results;

  const canPay = order.status === 'waiting_for_payment';
  const canCancel = order.status === 'open' || order.status === 'waiting_for_payment';

  return (
    <>
      <tr style={{ cursor: 'pointer' }} onClick={() => setExpanded((x) => !x)}>
        <td className="font-medium">#{order.id}</td>
        <td>{order.crop_name || `Crop #${order.crop_type}`}</td>
        <td>{order.quantity_kg} kg</td>
        <td>{formatNGN(order.max_price_per_kg)}/kg max</td>
        <td>
          <span className={`badge ${cfg.badge}`}>{cfg.icon} {cfg.label}</span>
        </td>
        <td className="text-sm text-muted">{formatDateTime(order.created_at)}</td>
        <td onClick={(e) => e.stopPropagation()}>
          <div style={{ display: 'flex', gap: 'var(--space-2)', justifyContent: 'flex-end' }}>
            {canPay && (
              <button
                className="btn btn-primary btn-sm"
                onClick={() => onPay(order)}
                title="Pay for this order"
              >
                💳 Pay
              </button>
            )}
            {canCancel && (
              <button
                className="btn btn-secondary btn-sm"
                style={{ color: 'var(--color-rust)', borderColor: 'var(--color-rust)' }}
                onClick={() => onCancel(order)}
                title="Cancel this order"
              >
                ✕ Remove
              </button>
            )}
            <span style={{ color: 'var(--color-stone)' }}>{expanded ? '▲' : '▼'}</span>
          </div>
        </td>
      </tr>

      {expanded && (
        <tr>
          <td colSpan={7} style={{ background: 'var(--color-field)', padding: 'var(--space-4)' }}>
            {/* Status description */}
            <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-stone)', marginBottom: 'var(--space-3)' }}>
              {cfg.icon} <strong>{cfg.label}</strong> — {cfg.description}
            </div>

            {/* Progress timeline */}
            <StatusTimeline currentStatus={order.status} />

            {/* Matched listings */}
            {order.status !== 'open' && order.status !== 'cancelled' && (
              <div style={{ marginTop: 'var(--space-4)' }}>
                <strong style={{ fontSize: 'var(--text-sm)' }}>Matched Listing:</strong>
                {!matches ? (
                  <span className="text-muted text-sm" style={{ marginLeft: 8 }}>Loading…</span>
                ) : matches.length === 0 ? (
                  <span className="text-muted text-sm" style={{ marginLeft: 8 }}>
                    No match details available.
                  </span>
                ) : (
                  <div style={{ marginTop: 'var(--space-3)', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                    {matches.map((m) => (
                      <div key={m.id} style={{ fontSize: 'var(--text-sm)', display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
                        <span>🌾 Farmer: {m.farmer_name}</span>
                        <span>{formatNGN(m.price_per_kg)}/kg</span>
                        <span>Grade {m.quality_grade}</span>
                        <span className={`badge ${m.status === 'delivered' ? 'badge-green' : 'badge-amber'}`}>{m.status}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  );
}

/* ─── Main page ─── */
export default function OrdersPage() {
  const [page, setPage] = useState(1);
  const [payingOrder, setPayingOrder] = useState(null);
  const [notification, setNotification] = useState('');
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['orders', page],
    queryFn: () => ordersApi.getOrders({ page }).then((r) => r.data),
    keepPreviousData: true,
  });

  const cancelMutation = useMutation({
    mutationFn: (id) => ordersApi.cancelOrder(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      showNotification('Order cancelled.');
    },
  });

  function showNotification(msg) {
    setNotification(msg);
    setTimeout(() => setNotification(''), 4000);
  }

  const orders = data?.results ?? [];
  const totalPages = data?.count ? Math.ceil(data.count / 20) : 1;

  return (
    <div style={{ position: 'relative' }}>
      {/* Toast notification */}
      {notification && (
        <div style={{
          position: 'fixed', top: 80, right: 24, zIndex: 400,
          background: 'var(--color-leaf)', color: '#fff',
          padding: 'var(--space-3) var(--space-5)',
          borderRadius: 'var(--radius-md)', boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
          fontSize: 'var(--text-sm)', fontWeight: 500,
          animation: 'slideInRight 0.3s ease',
        }}>
          ✅ {notification}
        </div>
      )}

      {/* Payment modal */}
      {payingOrder && (
        <PaymentModal
          order={payingOrder}
          onClose={() => setPayingOrder(null)}
          onSuccess={(msg) => showNotification(msg)}
        />
      )}

      <div className="page-header">
        <h1 className="page-title">My Orders</h1>
        <p className="page-subtitle">Click any row to expand and track your order through the pipeline</p>
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
                {orders.map((o) => (
                  <OrderRow
                    key={o.id}
                    order={o}
                    onPay={setPayingOrder}
                    onCancel={(order) => {
                      if (window.confirm(`Cancel order #${order.id}?`)) {
                        cancelMutation.mutate(order.id);
                      }
                    }}
                  />
                ))}
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
