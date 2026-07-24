import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { produceApi } from '../../api';
import { getErrorMessage } from '../../utils/helpers';

export default function NewListingPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    crop_type: '',
    collection_point: '',
    quantity_kg: '',
    price_per_kg: '',
    harvest_date: '',
    notes: '',
  });

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

  const crops = cropsData?.results ?? [];
  const hubs = hubsData?.results ?? [];

  const mutation = useMutation({
    mutationFn: (data) => produceApi.createListing(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries(['listings']);
      navigate(`/listings/${res.data.id}`);
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  function handleChange(e) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setError('');
    const payload = { ...form };
    if (!payload.collection_point) delete payload.collection_point;
    mutation.mutate(payload);
  }

  return (
    <div style={{ maxWidth: 600 }}>
      <div className="page-header">
        <h1 className="page-title">New Produce Listing</h1>
        <p className="page-subtitle">List your harvest for buyers to find</p>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--space-5)' }}>{error}</div>}

      <form className="card" onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="crop_type">Crop Type *</label>
          <select id="crop_type" name="crop_type" className="form-select" value={form.crop_type} onChange={handleChange} required>
            <option value="">Select crop…</option>
            {crops.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="collection_point">Collection Point</label>
          <select id="collection_point" name="collection_point" className="form-select" value={form.collection_point} onChange={handleChange}>
            <option value="">None (I'll bring it myself)</option>
            {hubs.map((h) => (
              <option key={h.id} value={h.id}>
                {h.name} — {h.state} {h.has_cold_storage ? '❄️' : ''}
              </option>
            ))}
          </select>
        </div>

        <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
          <div className="form-group">
            <label className="form-label" htmlFor="quantity_kg">Quantity (kg) *</label>
            <input id="quantity_kg" name="quantity_kg" type="number" min="0" step="0.01" className="form-input" placeholder="e.g. 150" value={form.quantity_kg} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="price_per_kg">Price per kg (₦) *</label>
            <input id="price_per_kg" name="price_per_kg" type="number" min="0" step="0.01" className="form-input" placeholder="e.g. 450" value={form.price_per_kg} onChange={handleChange} required />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="harvest_date">Harvest Date *</label>
          <input id="harvest_date" name="harvest_date" type="date" className="form-input" value={form.harvest_date} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="notes">Notes (optional)</label>
          <textarea id="notes" name="notes" className="form-textarea" rows={3} placeholder="e.g. Freshly harvested, no chemical spray…" value={form.notes} onChange={handleChange} />
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <button type="submit" className="btn btn-primary" disabled={mutation.isPending}>
            {mutation.isPending ? <span className="spinner" /> : '✔ Create Listing'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/listings')}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
