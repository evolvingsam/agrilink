import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { produceApi, ordersApi, matchingApi } from '../../api';
import { formatNGN, formatDate, getStatusBadgeClass, getGradeBadgeClass, getErrorMessage } from '../../utils/helpers';

export default function BuyerHomePage() {
  const queryClient = useQueryClient();
  const [crop, setCrop] = useState('');
  const [region, setRegion] = useState('');
  const [grade, setGrade] = useState('');
  const [page, setPage] = useState(1);

  const [orderForm, setOrderForm] = useState({ crop_type: '', quantity_kg: '', max_price_per_kg: '', required_grade: 'A' });
  const [orderSuccess, setOrderSuccess] = useState('');
  const [orderError, setOrderError] = useState('');

  const { data: cropsData } = useQuery({
    queryKey: ['crops'],
    queryFn: () => produceApi.getCrops().then((r) => r.data),
    staleTime: Infinity,
  });

  const { data: listingsData, isLoading } = useQuery({
    queryKey: ['marketplace', crop, region, grade, page],
    queryFn: () => produceApi.getListings({ crop, region, grade, page }).then((r) => r.data),
    keepPreviousData: true,
  });

  const orderMutation = useMutation({
    mutationFn: (data) => ordersApi.createOrder(data),
    onSuccess: () => {
      setOrderSuccess('Order placed successfully!');
      setOrderForm({ crop_type: '', quantity_kg: '', max_price_per_kg: '', required_grade: 'A' });
      queryClient.invalidateQueries(['orders']);
    },
    onError: (err) => setOrderError(getErrorMessage(err)),
  });

  const crops = cropsData?.results ?? [];
  const listings = listingsData?.results ?? [];
  const totalPages = listingsData?.count ? Math.ceil(listingsData.count / 20) : 1;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 'var(--space-8)', alignItems: 'start' }}>
      {/* Marketplace */}
      <div>
        <div className="page-header">
          <h1 className="page-title">Marketplace</h1>
          <p className="page-subtitle">Browse graded produce available from farmers</p>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap', marginBottom: 'var(--space-5)' }}>
          <select className="form-select" style={{ width: 'auto' }} value={crop} onChange={(e) => { setCrop(e.target.value); setPage(1); }}>
            <option value="">All Crops</option>
            {crops.map((c) => <option key={c.id} value={c.name}>{c.name}</option>)}
          </select>
          <select className="form-select" style={{ width: 'auto' }} value={grade} onChange={(e) => { setGrade(e.target.value); setPage(1); }}>
            <option value="">All Grades</option>
            <option value="A">Grade A</option>
            <option value="B">Grade B</option>
            <option value="C">Grade C</option>
          </select>
          <input className="form-input" style={{ width: 'auto' }} placeholder="Filter by region…" value={region} onChange={(e) => { setRegion(e.target.value); setPage(1); }} />
        </div>

        {isLoading ? (
          <div className="loading-center"><span className="spinner" /> Loading…</div>
        ) : listings.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🌾</div>
            <div className="empty-state-title">No listings found</div>
          </div>
        ) : (
          <>
            <div className="grid-2">
              {listings.map((l) => (
                <div key={l.id} className="card">
                  {l.photo && (
                    <img
                      src={l.photo}
                      alt={l.crop_name}
                      style={{ width: '100%', height: 140, objectFit: 'cover', borderRadius: 'var(--radius-sm)', marginBottom: 'var(--space-3)', border: 'var(--border-1)' }}
                    />
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-2)' }}>
                    <div className="font-semibold" style={{ fontSize: 'var(--text-lg)' }}>{l.crop_name}</div>
                    <span className={`badge ${getGradeBadgeClass(l.quality_grade)}`}>Grade {l.quality_grade}</span>
                  </div>
                  <div style={{ color: 'var(--color-leaf)', fontWeight: 700, fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
                    {formatNGN(l.price_per_kg)}<span style={{ fontSize: 'var(--text-sm)', fontWeight: 400, color: 'var(--color-stone)' }}>/kg</span>
                  </div>
                  <div className="text-sm text-muted">{l.quantity_kg} kg available</div>
                  <div className="text-sm text-muted">📍 {l.collection_point_name || 'Pickup arranged'}</div>
                  <div className="text-sm text-muted">🌾 Farmer: {l.farmer_name}</div>
                  <div className="text-sm text-muted">Harvested: {formatDate(l.harvest_date)}</div>
                </div>
              ))}
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

      {/* Place Order Sidebar */}
      <div className="card" style={{ position: 'sticky', top: 80 }}>
        <h2 className="card-title">🛒 Place an Order</h2>
        <p className="text-sm text-muted" style={{ marginBottom: 'var(--space-4)' }}>
          Specify what you need and let the system find matching produce.
        </p>

        {orderSuccess && <div className="alert alert-success" style={{ marginBottom: 'var(--space-4)' }}>{orderSuccess}</div>}
        {orderError && <div className="alert alert-error" style={{ marginBottom: 'var(--space-4)' }}>{orderError}</div>}

        <form onSubmit={(e) => { e.preventDefault(); setOrderSuccess(''); setOrderError(''); orderMutation.mutate(orderForm); }}>
          <div className="form-group">
            <label className="form-label" htmlFor="order-crop">Crop *</label>
            <select id="order-crop" className="form-select" value={orderForm.crop_type} onChange={(e) => setOrderForm((f) => ({ ...f, crop_type: e.target.value }))} required>
              <option value="">Select…</option>
              {crops.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="order-qty">Quantity (kg) *</label>
            <input id="order-qty" type="number" min="1" className="form-input" value={orderForm.quantity_kg} onChange={(e) => setOrderForm((f) => ({ ...f, quantity_kg: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="order-price">Max Price / kg (₦) *</label>
            <input id="order-price" type="number" min="1" className="form-input" value={orderForm.max_price_per_kg} onChange={(e) => setOrderForm((f) => ({ ...f, max_price_per_kg: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="order-grade">Minimum Grade</label>
            <select id="order-grade" className="form-select" value={orderForm.required_grade} onChange={(e) => setOrderForm((f) => ({ ...f, required_grade: e.target.value }))}>
              <option value="A">Grade A (Premium)</option>
              <option value="B">Grade B (Standard)</option>
              <option value="C">Grade C (Processing)</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary w-full" disabled={orderMutation.isPending}>
            {orderMutation.isPending ? <span className="spinner" /> : 'Submit Order'}
          </button>
        </form>
      </div>
    </div>
  );
}
