import { useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { produceApi } from '../../api';
import { getStatusBadgeClass, getGradeBadgeClass, formatNGN, formatDate, formatDateTime, getErrorMessage } from '../../utils/helpers';

export default function ListingDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const fileRef = useRef();
  const [uploadError, setUploadError] = useState('');
  const [gradingResult, setGradingResult] = useState(null);

  const { data, isLoading } = useQuery({
    queryKey: ['listing', id],
    queryFn: () => produceApi.getListing(id).then((r) => r.data),
  });

  const uploadMutation = useMutation({
    mutationFn: (file) => {
      const fd = new FormData();
      fd.append('photo', file);
      return produceApi.uploadPhoto(id, fd);
    },
    onSuccess: (res) => {
      setGradingResult(res.data.grading);
      queryClient.invalidateQueries(['listing', id]);
      queryClient.invalidateQueries(['listings']);
    },
    onError: (err) => setUploadError(getErrorMessage(err)),
  });

  const deleteMutation = useMutation({
    mutationFn: () => produceApi.deleteListing(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['listings']);
      navigate('/listings');
    },
  });

  if (isLoading) return <div className="loading-center"><span className="spinner" /> Loading…</div>;
  if (!data) return <div className="alert alert-error">Listing not found.</div>;

  const gradeMap = { A: 'Grade A — Premium 🟢', B: 'Grade B — Standard 🟡', C: 'Grade C — Processing 🟠', rejected: 'Rejected 🔴', ungraded: 'Not Yet Graded' };

  return (
    <div style={{ maxWidth: 700 }}>
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">{data.crop_name}</h1>
          <p className="page-subtitle">Listing #{data.id} · Created {formatDate(data.created_at)}</p>
        </div>
        <div className="flex gap-2">
          <span className={`badge ${getStatusBadgeClass(data.status)}`}>{data.status}</span>
          <span className={`badge ${getGradeBadgeClass(data.quality_grade)}`}>{data.quality_grade}</span>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <h2 className="card-title">Details</h2>
        <table style={{ width: '100%' }}>
          <tbody>
            <tr><td className="text-muted text-sm" style={{ padding: 'var(--space-2) 0', width: 160 }}>Crop</td><td className="font-medium">{data.crop_name}</td></tr>
            <tr><td className="text-muted text-sm" style={{ padding: 'var(--space-2) 0' }}>Quantity</td><td>{data.quantity_kg} kg</td></tr>
            <tr><td className="text-muted text-sm" style={{ padding: 'var(--space-2) 0' }}>Price</td><td>{formatNGN(data.price_per_kg)} / kg</td></tr>
            <tr><td className="text-muted text-sm" style={{ padding: 'var(--space-2) 0' }}>Grade</td><td>{gradeMap[data.quality_grade] || data.quality_grade}</td></tr>
            <tr><td className="text-muted text-sm" style={{ padding: 'var(--space-2) 0' }}>Harvest Date</td><td>{formatDate(data.harvest_date)}</td></tr>
            <tr><td className="text-muted text-sm" style={{ padding: 'var(--space-2) 0' }}>Collection Point</td><td>{data.collection_point_name || '—'}</td></tr>
            {data.notes && <tr><td className="text-muted text-sm" style={{ padding: 'var(--space-2) 0' }}>Notes</td><td>{data.notes}</td></tr>}
            <tr><td className="text-muted text-sm" style={{ padding: 'var(--space-2) 0' }}>Last Updated</td><td className="text-sm">{formatDateTime(data.updated_at)}</td></tr>
          </tbody>
        </table>
      </div>

      {/* Photo + Grading */}
      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <h2 className="card-title">Photo & AI Grading</h2>
        {data.photo && (
          <img
            src={data.photo}
            alt="Produce photo"
            style={{ width: '100%', maxHeight: 300, objectFit: 'cover', borderRadius: 'var(--radius-sm)', marginBottom: 'var(--space-4)', border: 'var(--border-1)' }}
          />
        )}

        {uploadError && <div className="alert alert-error" style={{ marginBottom: 'var(--space-4)' }}>{uploadError}</div>}

        {gradingResult && (
          <div className="alert alert-success" style={{ marginBottom: 'var(--space-4)' }}>
            <strong>AI Grading Complete!</strong> Grade: <strong>{gradingResult.grade}</strong> ·
            Shelf life: {gradingResult.estimated_shelf_days} days ·
            Confidence: {Math.round(gradingResult.confidence * 100)}%
            {gradingResult.issues?.length > 0 && (
              <div style={{ marginTop: 'var(--space-2)' }}>Issues: {gradingResult.issues.join(', ')}</div>
            )}
          </div>
        )}

        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={(e) => {
            if (e.target.files[0]) {
              setUploadError('');
              setGradingResult(null);
              uploadMutation.mutate(e.target.files[0]);
            }
          }}
        />
        <button
          className="btn btn-secondary"
          onClick={() => fileRef.current.click()}
          disabled={uploadMutation.isPending}
        >
          {uploadMutation.isPending ? (
            <><span className="spinner" /> Scanning…</>
          ) : (
            data.photo ? '📷 Replace Photo & Re-grade' : '📷 Upload Photo for AI Grading'
          )}
        </button>
      </div>

      {/* Actions */}
      <div className="flex gap-4">
        <button
          className="btn btn-danger"
          onClick={() => { if (window.confirm('Delete this listing?')) deleteMutation.mutate(); }}
          disabled={deleteMutation.isPending}
        >
          {deleteMutation.isPending ? <span className="spinner" /> : '🗑 Delete Listing'}
        </button>
        <button className="btn btn-secondary" onClick={() => navigate('/listings')}>
          ← Back to Listings
        </button>
      </div>
    </div>
  );
}
