import React from 'react';

function StatCard({ title, value, subtitle, icon: Icon, color = '#1a237e', trend }) {
  const styles = {
    card: {
      backgroundColor: '#ffffff',
      borderRadius: 10,
      padding: '20px 24px',
      borderLeft: `4px solid ${color}`,
      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
      display: 'flex',
      alignItems: 'flex-start',
      gap: 16,
    },
    iconWrap: {
      width: 44,
      height: 44,
      borderRadius: 10,
      backgroundColor: `${color}15`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
    },
    body: {
      flex: 1,
      minWidth: 0,
    },
    title: {
      fontSize: 12,
      fontWeight: 600,
      color: '#888',
      textTransform: 'uppercase',
      letterSpacing: 0.5,
      marginBottom: 4,
    },
    value: {
      fontSize: 28,
      fontWeight: 700,
      color: '#1a237e',
      lineHeight: 1.2,
      marginBottom: 4,
    },
    subtitle: {
      fontSize: 12,
      color: '#999',
    },
    trendUp: {
      fontSize: 12,
      fontWeight: 600,
      color: '#2e7d32',
    },
    trendDown: {
      fontSize: 12,
      fontWeight: 600,
      color: '#c62828',
    },
  };

  return (
    <div style={styles.card}>
      {Icon && (
        <div style={styles.iconWrap}>
          <Icon size={22} color={color} />
        </div>
      )}
      <div style={styles.body}>
        <div style={styles.title}>{title}</div>
        <div style={styles.value}>{value}</div>
        {subtitle && <div style={styles.subtitle}>{subtitle}</div>}
        {trend && (
          <span style={trend.direction === 'up' ? styles.trendUp : styles.trendDown}>
            {trend.direction === 'up' ? '\u25B2' : '\u25BC'} {trend.value}
          </span>
        )}
      </div>
    </div>
  );
}

export default StatCard;
