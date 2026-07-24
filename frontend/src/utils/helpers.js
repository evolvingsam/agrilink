/** Map listing status to badge class */
export function getStatusBadgeClass(status) {
  const map = {
    pending: 'badge-gray',
    graded: 'badge-blue',
    matched: 'badge-amber',
    sold: 'badge-green',
    expired: 'badge-red',
  };
  return map[status] || 'badge-gray';
}

/** Map grade to badge class */
export function getGradeBadgeClass(grade) {
  const map = {
    A: 'badge-green',
    B: 'badge-amber',
    C: 'badge-brown',
    rejected: 'badge-red',
    ungraded: 'badge-gray',
  };
  return map[grade] || 'badge-gray';
}

/** Format NGN currency */
export function formatNGN(amount) {
  if (amount == null) return '—';
  return new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: 'NGN',
    maximumFractionDigits: 2,
  }).format(amount);
}

/** Format a date string */
export function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-NG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/** Format datetime string */
export function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-NG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/** Get trend icon */
export function getTrendIcon(direction) {
  if (direction === 'up') return '↑';
  if (direction === 'down') return '↓';
  return '→';
}

/** Get trend class */
export function getTrendClass(direction) {
  if (direction === 'up') return 'trend-up';
  if (direction === 'down') return 'trend-down';
  return 'trend-flat';
}

/** Extract error message from API error */
export function getErrorMessage(error) {
  if (!error?.response?.data) return 'An unexpected error occurred.';
  const data = error.response.data;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  const msgs = Object.entries(data)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
    .join(' | ');
  return msgs || 'An unexpected error occurred.';
}
