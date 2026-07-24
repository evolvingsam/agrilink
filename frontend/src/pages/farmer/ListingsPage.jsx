import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { produceApi } from '../../api';
import { getStatusBadgeClass, getGradeBadgeClass, formatNGN, formatDate } from '../../utils/helpers';

export default function ListingsPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery({
    queryKey: ['listings', page],
    queryFn: () => produceApi.getListings({ page }).then((r) => r.data),
    keepPreviousData: true,
  });

  const listings = data?.results ?? [];
  const totalPages = data?.count ? Math.ceil(data.count / 20) : 1;

  return (
    <div>
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">My Listings</h1>
          <p className="page-subtitle">All your produce available in the market</p>
        </div>
        <Link to="/listings/new" className="btn btn-primary">
          ➕ New Listing
        </Link>
      </div>

      {isLoading && (
        <div className="loading-center">
          <span className="spinner" /> Loading your listings…
        </div>
      )}

      {error && <div className="alert alert-error">Failed to load listings.</div>}

      {!isLoading && listings.length === 0 && (
        <div className="empty-state">
          <div className="empty-state-icon">📦</div>
          <div className="empty-state-title">No listings yet</div>
          <p>Create your first listing to start selling your produce.</p>
          <Link to="/listings/new" className="btn btn-primary" style={{ marginTop: 'var(--space-4)' }}>
            Create First Listing
          </Link>
        </div>
      )}

      {listings.length > 0 && (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Crop</th>
                  <th>Qty (kg)</th>
                  <th>Price / kg</th>
                  <th>Grade</th>
                  <th>Status</th>
                  <th>Harvest Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {listings.map((l) => (
                  <tr key={l.id}>
                    <td className="font-medium">{l.crop_name}</td>
                    <td>{l.quantity_kg}</td>
                    <td>{formatNGN(l.price_per_kg)}</td>
                    <td>
                      <span className={`badge ${getGradeBadgeClass(l.quality_grade)}`}>
                        {l.quality_grade}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getStatusBadgeClass(l.status)}`}>
                        {l.status}
                      </span>
                    </td>
                    <td className="text-sm text-muted">{formatDate(l.harvest_date)}</td>
                    <td>
                      <Link to={`/listings/${l.id}`} className="btn btn-secondary btn-sm">
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="pagination-btn"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                ← Prev
              </button>
              <span className="text-sm text-muted">Page {page} of {totalPages}</span>
              <button
                className="pagination-btn"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
