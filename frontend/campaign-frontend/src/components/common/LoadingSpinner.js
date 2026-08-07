import React from 'react';

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 60,
  },
  spinner: {
    width: 36,
    height: 36,
    border: '4px solid #e0e0e0',
    borderTop: '4px solid #1a237e',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
    marginBottom: 12,
  },
  text: {
    fontSize: 14,
    color: '#666',
    fontWeight: 500,
  },
};

function LoadingSpinner() {
  return (
    <div style={styles.container}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={styles.spinner} />
      <span style={styles.text}>Loading...</span>
    </div>
  );
}

export default LoadingSpinner;
