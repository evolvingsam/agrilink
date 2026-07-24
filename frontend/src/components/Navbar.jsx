import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import './Navbar.css';

const farmerLinks = [
  { to: '/', label: 'Home', icon: '🌾' },
  { to: '/listings', label: 'My Listings', icon: '📦' },
  { to: '/chat', label: 'AI Assistant', icon: '🤖' },
  { to: '/market', label: 'Market', icon: '📈' },
  { to: '/payments', label: 'Payments', icon: '💳' },
];

const buyerLinks = [
  { to: '/', label: 'Marketplace', icon: '🛒' },
  { to: '/orders', label: 'My Orders', icon: '📋' },
];

const dispatcherLinks = [
  { to: '/', label: 'Routes', icon: '🚛' },
];

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const links =
    user?.role === 'farmer' ? farmerLinks
    : user?.role === 'buyer' ? buyerLinks
    : dispatcherLinks;

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="navbar-logo">🌱</span>
        <span className="navbar-name">AgriLink</span>
        {user?.role && <span className="navbar-role">{user.role}</span>}
      </div>

      <div className="navbar-links">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/'}
            className={({ isActive }) => `navbar-link${isActive ? ' active' : ''}`}
          >
            <span className="navbar-link-icon">{link.icon}</span>
            <span className="navbar-link-label">{link.label}</span>
          </NavLink>
        ))}
      </div>

      <div className="navbar-user">
        {user?.role === 'buyer' && user?.wallet_balance != null && (
          <span className="navbar-wallet" title="Demo Wallet Balance">
            💰 ₦{Number(user.wallet_balance).toLocaleString('en-NG', { minimumFractionDigits: 0 })}
          </span>
        )}
        <span className="navbar-username">{user?.username}</span>
        <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </nav>
  );
}
