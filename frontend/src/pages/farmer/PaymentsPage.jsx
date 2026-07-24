import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { paymentsApi } from '../../api';
import { formatNGN, formatDateTime } from '../../utils/helpers';

export default function PaymentsPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['payments', page],
    queryFn: () => paymentsApi.getPayments({ page }).then((r) => r.data),
    keepPreviousData: true,
  });

  const payments = data?.results ?? [];
  const totalPages = data?.count ? Math.ceil(data.count / 20) : 1;

  const totalReceived = payments
    .filter((p) => p.status === 'completed')
    .reduce((sum, p) => sum + parseFloat(p.amount || 0), 0);

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Payments</h1>
        <p className="page-subtitle">Your payment history and payouts</p>
      </div>

      <div className="stats-row" style={{ marginBottom: 'var(--space-8)' }}>
        <div className="stat-card">
          <div className="stat-label">Total Received</div>
          <div className="stat-value">{formatNGN(totalReceived)}</div>
          <div className="stat-note">From completed transactions</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Transactions</div>
          <div className="stat-value">{data?.count ?? 0}</div>
          <div className="stat-note">All time</div>
        </div>
      </div>

      {isLoading ? (
        <div className="loading-center"><span className="spinner" /> Loading payments…</div>
      ) : payments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">💳</div>
          <div className="empty-state-title">No payments yet</div>
          <p>Payments will appear here once your listings are sold and matched.</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Transaction Ref</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((p) => (
                  <tr key={p.id}>
                    <td className="font-medium text-sm" style={{ fontFamily: 'monospace' }}>
                      {p.transaction_ref || `TXN-${p.id}`}
                    </td>
                    <td style={{ fontWeight: 600 }}>{formatNGN(p.amount)}</td>
                    <td>
                      <span className={`badge ${p.status === 'completed' ? 'badge-green' : p.status === 'pending' ? 'badge-amber' : 'badge-gray'}`}>
                        {p.status}
                      </span>
                    </td>
                    <td className="text-sm text-muted">{formatDateTime(p.created_at)}</td>
                  </tr>
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
