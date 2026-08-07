import React from 'react';
import { NavLink, useNavigate, Outlet } from 'react-router-dom';
import { LayoutDashboard, Megaphone, PlusCircle, Users, Car, BarChart3, Store, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const campaignManagerLinks = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/campaigns', label: 'Campaigns', icon: Megaphone },
  { to: '/campaigns/create', label: 'Create Campaign', icon: PlusCircle },
  { to: '/customers', label: 'Customers', icon: Users },
  { to: '/vehicles', label: 'Vehicles', icon: Car },
];

const retailManagerLinks = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/campaigns', label: 'Campaigns', icon: Megaphone },
  { to: '/customers', label: 'Customers', icon: Users },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/dealer-performance', label: 'Dealer Performance', icon: Store },
];

const styles = {
  container: {
    display: 'flex',
    minHeight: '100vh',
    backgroundColor: '#f5f7fa',
  },
  sidebar: {
    width: 240,
    minWidth: 240,
    backgroundColor: '#1a237e',
    color: '#ffffff',
    display: 'flex',
    flexDirection: 'column',
    position: 'fixed',
    top: 0,
    left: 0,
    bottom: 0,
    zIndex: 100,
  },
  brand: {
    padding: '24px 20px',
    fontSize: 18,
    fontWeight: 700,
    letterSpacing: 0.5,
    borderBottom: '1px solid rgba(255,255,255,0.1)',
    color: '#ffffff',
  },
  nav: {
    flex: 1,
    padding: '16px 0',
    overflowY: 'auto',
  },
  navLink: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '12px 20px',
    color: 'rgba(255,255,255,0.7)',
    textDecoration: 'none',
    fontSize: 14,
    fontWeight: 500,
    borderLeft: '3px solid transparent',
    transition: 'all 0.2s ease',
  },
  navLinkActive: {
    color: '#ffffff',
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderLeft: '3px solid #0288d1',
  },
  userSection: {
    padding: '16px 20px',
    borderTop: '1px solid rgba(255,255,255,0.1)',
  },
  userName: {
    fontSize: 14,
    fontWeight: 600,
    color: '#ffffff',
    marginBottom: 4,
  },
  roleBadge: {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: 12,
    fontSize: 11,
    fontWeight: 600,
    backgroundColor: 'rgba(2,136,209,0.3)',
    color: '#80d8ff',
  },
  mainWrapper: {
    flex: 1,
    marginLeft: 240,
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
  },
  topbar: {
    height: 56,
    backgroundColor: '#ffffff',
    borderBottom: '1px solid #e0e0e0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 24px',
    position: 'sticky',
    top: 0,
    zIndex: 50,
  },
  topbarUser: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  },
  topbarName: {
    fontSize: 14,
    fontWeight: 500,
    color: '#333',
  },
  logoutBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '6px 14px',
    border: 'none',
    borderRadius: 6,
    backgroundColor: '#c62828',
    color: '#ffffff',
    fontSize: 13,
    fontWeight: 500,
    cursor: 'pointer',
  },
  content: {
    flex: 1,
    padding: 24,
    maxWidth: 1280,
    width: '100%',
    boxSizing: 'border-box',
  },
};

function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const links = user?.role === 'retail_manager' ? retailManagerLinks : campaignManagerLinks;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const formatRole = (role) => {
    if (!role) return '';
    return role.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  return (
    <div style={styles.container}>
      <aside style={styles.sidebar}>
        <div style={styles.brand}>TATA Campaign AI</div>
        <nav style={styles.nav}>
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/dashboard'}
              style={({ isActive }) => ({
                ...styles.navLink,
                ...(isActive ? styles.navLinkActive : {}),
              })}
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div style={styles.userSection}>
          <div style={styles.userName}>{user?.name || 'User'}</div>
          <span style={styles.roleBadge}>{formatRole(user?.role)}</span>
        </div>
      </aside>
      <div style={styles.mainWrapper}>
        <header style={styles.topbar}>
          <div style={styles.topbarUser}>
            <span style={styles.topbarName}>{user?.name || 'User'}</span>
            <button style={styles.logoutBtn} onClick={handleLogout}>
              <LogOut size={14} />
              Logout
            </button>
          </div>
        </header>
        <main style={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default Layout;
