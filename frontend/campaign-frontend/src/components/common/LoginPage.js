import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f7fa',
  },
  card: {
    width: 400,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
    padding: 40,
  },
  heading: {
    fontSize: 22,
    fontWeight: 700,
    color: '#1a237e',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 13,
    color: '#666',
    textAlign: 'center',
    marginBottom: 32,
  },
  label: {
    display: 'block',
    fontSize: 13,
    fontWeight: 600,
    color: '#333',
    marginBottom: 6,
  },
  input: {
    width: '100%',
    padding: '10px 12px',
    border: '1px solid #ccc',
    borderRadius: 6,
    fontSize: 14,
    marginBottom: 16,
    boxSizing: 'border-box',
    outline: 'none',
  },
  loginBtn: {
    width: '100%',
    padding: '12px 0',
    border: 'none',
    borderRadius: 6,
    backgroundColor: '#1a237e',
    color: '#ffffff',
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
    marginBottom: 24,
  },
  divider: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    marginBottom: 16,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#e0e0e0',
  },
  dividerText: {
    fontSize: 12,
    color: '#999',
  },
  demoBtn: {
    width: '100%',
    padding: '10px 0',
    border: '1px solid #0288d1',
    borderRadius: 6,
    backgroundColor: 'transparent',
    color: '#0288d1',
    fontSize: 13,
    fontWeight: 500,
    cursor: 'pointer',
    marginBottom: 8,
  },
  error: {
    backgroundColor: '#fce4ec',
    color: '#c62828',
    padding: '10px 14px',
    borderRadius: 6,
    fontSize: 13,
    marginBottom: 16,
  },
};

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError('');
    setIsLoading(true);
    try {
      await login(demoEmail, demoPassword);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.heading}>TATA Campaign Intelligence Platform</h1>
        <p style={styles.subtitle}>Sign in to manage your campaigns</p>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <label style={styles.label}>Email</label>
          <input
            style={styles.input}
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <label style={styles.label}>Password</label>
          <input
            style={styles.input}
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button style={styles.loginBtn} type="submit" disabled={isLoading}>
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={styles.divider}>
          <div style={styles.dividerLine} />
          <span style={styles.dividerText}>Quick Demo Access</span>
          <div style={styles.dividerLine} />
        </div>

        <button
          style={styles.demoBtn}
          onClick={() => handleDemoLogin('campaign_manager@tata.com', 'admin123')}
          disabled={isLoading}
        >
          Login as Campaign Manager
        </button>
        <button
          style={styles.demoBtn}
          onClick={() => handleDemoLogin('retail_manager@tata.com', 'admin123')}
          disabled={isLoading}
        >
          Login as Retail Manager
        </button>
      </div>
    </div>
  );
}

export default LoginPage;
