import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi } from '../../api';
import { useAuthStore } from '../../store/authStore';
import { getErrorMessage } from '../../utils/helpers';
import './Auth.css';

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'ha', label: 'Hausa' },
  { value: 'yo', label: 'Yoruba' },
  { value: 'ig', label: 'Igbo' },
  { value: 'pcm', label: 'Nigerian Pidgin' },
];

const ROLES = [
  { value: 'farmer', label: 'Farmer', icon: '🌾' },
  { value: 'buyer', label: 'Buyer', icon: '🛒' },
  { value: 'dispatcher', label: 'Dispatcher', icon: '🚛' },
];

export default function RegisterPage() {
  const [form, setForm] = useState({
    username: '', email: '', first_name: '', last_name: '',
    password: '', password2: '', role: 'farmer', phone: '',
    state: '', lga: '', preferred_language: 'en',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setTokens, setUser } = useAuthStore();
  const navigate = useNavigate();

  function handleChange(e) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    if (form.password !== form.password2) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    try {
      await authApi.register(form);
      const { data } = await authApi.login({ username: form.username, password: form.password });
      setTokens(data.access, data.refresh);
      const { data: me } = await authApi.me();
      setUser(me);
      navigate('/');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card auth-card-wide">
        <div className="auth-header">
          <span className="auth-logo">🌱</span>
          <h1 className="auth-title">Join AgriLink</h1>
          <p className="auth-subtitle">Create your account</p>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: 'var(--space-4)' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          {/* Role Selector */}
          <div className="form-group">
            <label className="form-label">I am a</label>
            <div className="role-picker">
              {ROLES.map((r) => (
                <label key={r.value} className={`role-option${form.role === r.value ? ' selected' : ''}`}>
                  <input type="radio" name="role" value={r.value} onChange={handleChange} />
                  <span className="role-icon">{r.icon}</span>
                  <span>{r.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="first_name">First Name</label>
              <input id="first_name" name="first_name" className="form-input" placeholder="Aminu" value={form.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="last_name">Last Name</label>
              <input id="last_name" name="last_name" className="form-input" placeholder="Musa" value={form.last_name} onChange={handleChange} required />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-username">Username</label>
            <input id="reg-username" name="username" className="form-input" placeholder="aminu_kano" value={form.username} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">Email</label>
            <input id="reg-email" name="email" type="email" className="form-input" placeholder="aminu@example.com" value={form.email} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="phone">Phone Number</label>
            <input id="phone" name="phone" className="form-input" placeholder="08012345678" value={form.phone} onChange={handleChange} />
          </div>

          {form.role === 'farmer' && (
            <>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label" htmlFor="state">State</label>
                  <input id="state" name="state" className="form-input" placeholder="Kano" value={form.state} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="lga">LGA</label>
                  <input id="lga" name="lga" className="form-input" placeholder="Kano Municipal" value={form.lga} onChange={handleChange} />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="preferred_language">Preferred Language</label>
                <select id="preferred_language" name="preferred_language" className="form-select" value={form.preferred_language} onChange={handleChange}>
                  {LANGUAGES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
                </select>
              </div>
            </>
          )}

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="reg-password">Password</label>
              <input id="reg-password" name="password" type="password" className="form-input" placeholder="At least 8 characters" value={form.password} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="password2">Confirm Password</label>
              <input id="password2" name="password2" type="password" className="form-input" placeholder="Repeat password" value={form.password2} onChange={handleChange} required />
            </div>
          </div>

          <button type="submit" className="btn btn-primary w-full btn-lg" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Create Account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
