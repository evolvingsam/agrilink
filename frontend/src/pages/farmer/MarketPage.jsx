import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { marketApi, produceApi } from '../../api';
import { formatNGN, formatDate, getTrendIcon, getTrendClass } from '../../utils/helpers';

export default function MarketPage() {
  const [cropId, setCropId] = useState('');
  const [hubId, setHubId] = useState('');
  const [page, setPage] = useState(1);

  const { data: cropsData } = useQuery({
    queryKey: ['crops'],
    queryFn: () => produceApi.getCrops().then((r) => r.data),
    staleTime: Infinity,
  });
  const { data: hubsData } = useQuery({
    queryKey: ['collection-points'],
    queryFn: () => produceApi.getCollectionPoints().then((r) => r.data),
    staleTime: Infinity,
  });
  const { data: pricesData, isLoading: pricesLoading } = useQuery({
    queryKey: ['market-prices', cropId, hubId, page],
    queryFn: () => marketApi.getPrices({ crop_id: cropId || undefined, hub_id: hubId || undefined, page }).then((r) => r.data),
    keepPreviousData: true,
  });
  const { data: trendsData, isLoading: trendsLoading } = useQuery({
    queryKey: ['market-trends'],
    queryFn: () => marketApi.getTrends().then((r) => r.data),
    staleTime: 5 * 60 * 1000,
  });

  const crops = cropsData?.results ?? [];
  const hubs = hubsData?.results ?? [];
  const prices = pricesData?.data ?? [];
  const totalPages = pricesData?.pagination?.total_pages ?? 1;
  const trendList = trendsData?.data?.trends ?? [];
  const summaryAlert = trendsData?.data?.summary_alert;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Market Prices</h1>
        <p className="page-subtitle">Daily commodity prices across all collection hubs</p>
      </div>

      {/* Trends Section */}
      <div style={{ marginBottom: 'var(--space-10)' }}>
        <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 600, marginBottom: 'var(--space-4)' }}>
          📈 Weekly Trends
        </h2>

        {summaryAlert && (
          <div className="alert alert-warning" style={{ marginBottom: 'var(--space-4)' }}>
            {summaryAlert}
          </div>
        )}

        {trendsLoading ? (
          <div className="loading-center"><span className="spinner" /></div>
        ) : trendList.length === 0 ? (
          <p className="text-muted text-sm">No trend data available.</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 'var(--space-4)' }}>
            {trendList.map((t) => (
              <div key={t.crop_name} className="card">
                <div style={{ fontWeight: 600, marginBottom: 'var(--space-1)' }}>{t.crop_name}</div>
                <div style={{ fontSize: 'var(--text-xl)', fontWeight: 700, marginBottom: 'var(--space-2)' }}>
                  {formatNGN(t.current_avg_price_per_kg)}<span style={{ fontSize: 'var(--text-xs)', fontWeight: 400, color: 'var(--color-stone)' }}>/kg</span>
                </div>
                <span className={getTrendClass(t.trend_direction)} style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>
                  {getTrendIcon(t.trend_direction)} {t.trend_percentage}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Prices Table */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-4)' }}>
          <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 600 }}>📋 All Prices</h2>
          <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
            <select className="form-select" value={cropId} onChange={(e) => { setCropId(e.target.value); setPage(1); }} style={{ width: 'auto' }}>
              <option value="">All Crops</option>
              {crops.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <select className="form-select" value={hubId} onChange={(e) => { setHubId(e.target.value); setPage(1); }} style={{ width: 'auto' }}>
              <option value="">All Hubs</option>
              {hubs.map((h) => <option key={h.id} value={h.id}>{h.name}</option>)}
            </select>
          </div>
        </div>

        {pricesLoading ? (
          <div className="loading-center"><span className="spinner" /> Loading prices…</div>
        ) : prices.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📊</div>
            <div className="empty-state-title">No price data</div>
            <p>No market prices have been recorded yet.</p>
          </div>
        ) : (
          <>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Crop</th>
                    <th>Hub</th>
                    <th>Price / kg</th>
                    <th>Last Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {prices.map((p) => (
                    <tr key={p.id}>
                      <td className="font-medium">{p.crop_name}</td>
                      <td>{p.hub_name}</td>
                      <td style={{ fontWeight: 600, color: 'var(--color-leaf)' }}>{formatNGN(p.price_per_kg)}</td>
                      <td className="text-sm text-muted">{formatDate(p.last_updated)}</td>
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
    </div>
  );
}
