import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

/** Redirects to /login if not authenticated */
export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

/** Redirects to role-specific home if already authenticated */
export function PublicOnlyRoute() {
  const { isAuthenticated, user } = useAuthStore();
  if (!isAuthenticated) return <Outlet />;
  return <Navigate to="/" replace />;
}

/** Guard that only allows a specific role */
export function RoleRoute({ roles }) {
  const user = useAuthStore((s) => s.user);
  if (!user) return null;
  if (!roles.includes(user.role)) return <Navigate to="/" replace />;
  return <Outlet />;
}
