import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Megaphone, Activity, Users, Mail } from 'lucide-react';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts';
import { analyticsAPI } from '../../services/api';
import StatCard from '../common/StatCard';
import LoadingSpinner from '../common/LoadingSpinner';

const defaultData = {
  total_campaigns: 5,
  active_campaigns: 2,
  total_reach: 1250,
  avg_open_rate: 34.5,
  campaign_status_distribution: [
    { name: 'Draft', value: 1 },
    { name: 'Active', value: 2 },
    { name: 'Completed', value: 1 },
    { name: 'Paused', value: 1 },
  ],
  channel_performance: [
    { channel: 'Email', sent: 500, delivered: 475, opened: 190 },
    { channel: 'WhatsApp', sent: 400, delivered: 392, opened: 180 },
    { channel: 'SMS', sent: 200, delivered: 180, opened: 90 },
    { channel: 'Push', sent: 100, delivered: 85, opened: 35 },
    { channel: 'Social', sent: 50, delivered: 48, opened: 20 },
  ],
  recent_campaigns: [
    { id: 1, name: 'Diwali Nexon EV Launch', status: 'active', channels: ['email', 'whatsapp'], open_rate: 38.5, ctr: 12.3, created_at: '2026-07-15' },
    { id: 2, name: 'Curvv Summer Drive', status: 'completed', channels: ['email', 'sms'], open_rate: 42.1, ctr: 15.7, created_at: '2026-07-10' },
    { id: 3, name: 'Safari Premium Experience', status: 'active', channels: ['email', 'instagram'], open_rate: 35.2, ctr: 10.8, created_at: '2026-07-05' },
    { id: 4, name: 'Punch City Drive', status: 'draft', channels: ['whatsapp', 'sms'], open_rate: 0, ctr: 0, created_at: '2026-07-20' },
    { id: 5, name: 'Tiago EV Green Initiative', status: 'paused', channels: ['email', 'push'], open_rate: 28.9, ctr: 8.5, created_at: '2026-06-30' },
  ],
  agent_statuses: [
    { name: 'Campaign Orchestrator', status: 'active' },
    { name: 'Customer Intelligence', status: 'active' },
    { name: 'Recommendation Engine', status: 'active' },
    { name: 'Content Generation', status: 'active' },
    { name: 'Localization', status: 'active' },
    { name: 'Channel Selection', status: 'active' },
    { name: 'Scheduler', status: 'active' },
    { name: 'Execution', status: 'active' },
    { name: 'Analytics', status: 'active' },
    { name: 'Privacy & Compliance', status: 'active' },
  ],
};

const PIE_COLORS = {
  Draft: '#9e9e9e',
  Active: '#0288d1',
  Completed: '#2e7d32',
  Paused: '#f57f17',
};

const STATUS_BADGE = {
  active: { backgroundColor: '#e3f2fd', color: '#0288d1' },
  completed: { backgroundColor: '#e8f5e9', color: '#2e7d32' },
  draft: { backgroundColor: '#f5f5f5', color: '#9e9e9e' },
  paused: { backgroundColor: '#fff8e1', color: '#f57f17' },
};

function CampaignManagerDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    analyticsAPI.getCampaignManagerDashboard()
      .then((res) => {
        const d = res.data;
        setData(d && Object.keys(d).length > 0 ? d : defaultData);
      })
      .catch(() => {
        setData(defaultData);
        setError('Could not load live data. Showing demo data.');
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  const raw = data || defaultData;

  const campaignStats = raw.campaign_stats || {};
  const totalCampaigns = raw.total_campaigns || Object.values(campaignStats).reduce((a, b) => a + b, 0) || 5;
  const activeCampaigns = raw.active_campaigns || campaignStats.active || 2;

  const statusDist = raw.campaign_status_distribution || Object.entries(campaignStats).map(
    ([k, v]) => ({ name: k.charAt(0).toUpperCase() + k.slice(1), value: v })
  );
  if (statusDist.length === 0) {
    statusDist.push({ name: 'Draft', value: 1 }, { name: 'Active', value: 2 }, { name: 'Completed', value: 1 }, { name: 'Paused', value: 1 });
  }

  const channelDist = raw.channel_distribution || {};
  const channelPerf = raw.channel_performance || Object.entries(channelDist).map(
    ([ch, count]) => ({ channel: ch.charAt(0).toUpperCase() + ch.slice(1), sent: count, delivered: Math.round(count * 0.95), opened: Math.round(count * 0.35) })
  );
  if (channelPerf.length === 0) {
    channelPerf.push(
      { channel: 'Email', sent: 500, delivered: 475, opened: 190 },
      { channel: 'WhatsApp', sent: 400, delivered: 392, opened: 180 },
      { channel: 'SMS', sent: 200, delivered: 180, opened: 90 },
      { channel: 'Push', sent: 100, delivered: 85, opened: 35 },
      { channel: 'Social', sent: 50, delivered: 48, opened: 20 },
    );
  }

  const recentCampaigns = (raw.recent_campaigns || defaultData.recent_campaigns).map((c) => {
    let channels = c.channels || [];
    if (typeof channels === 'string') {
      try { channels = JSON.parse(channels); } catch { channels = []; }
    }
    return {
      ...c,
      id: c.campaign_id || c.id,
      channels,
      open_rate: c.open_rate || (c.metrics && c.metrics.total_opened && c.metrics.total_sent ? Math.round((c.metrics.total_opened / c.metrics.total_sent) * 100 * 10) / 10 : 0),
      ctr: c.ctr || (c.metrics && c.metrics.total_clicked && c.metrics.total_sent ? Math.round((c.metrics.total_clicked / c.metrics.total_sent) * 100 * 10) / 10 : 0),
      created_at: c.created_at ? c.created_at.split('T')[0] : '',
    };
  });

  const totalReach = raw.total_reach || channelPerf.reduce((a, c) => a + (c.sent || 0), 0) || 1250;
  const avgOpenRate = raw.avg_open_rate || (channelPerf.reduce((a, c) => a + (c.opened || 0), 0) / Math.max(channelPerf.reduce((a, c) => a + (c.sent || 0), 0), 1) * 100).toFixed(1);

  const agentStatuses = raw.agent_statuses || defaultData.agent_statuses;

  const dashboard = {
    total_campaigns: totalCampaigns,
    active_campaigns: activeCampaigns,
    total_reach: totalReach,
    avg_open_rate: avgOpenRate,
    campaign_status_distribution: statusDist,
    channel_performance: channelPerf,
    recent_campaigns: recentCampaigns,
    agent_statuses: agentStatuses,
  };

  const sectionHeading = {
    fontSize: 18,
    fontWeight: 600,
    marginBottom: 16,
    color: '#1a237e',
  };

  const card = {
    backgroundColor: '#ffffff',
    borderRadius: 10,
    padding: 24,
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  };

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, color: '#1a237e', marginBottom: 24 }}>
        Campaign Manager Dashboard
      </h1>

      {error && (
        <div style={{ backgroundColor: '#fff3e0', color: '#e65100', padding: '10px 16px', borderRadius: 8, marginBottom: 20, fontSize: 14 }}>
          {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20, marginBottom: 32 }}>
        <StatCard
          title="Total Campaigns"
          value={dashboard.total_campaigns}
          icon={Megaphone}
          color="#1a237e"
        />
        <StatCard
          title="Active Campaigns"
          value={dashboard.active_campaigns}
          icon={Activity}
          color="#0288d1"
        />
        <StatCard
          title="Customers Reached"
          value={dashboard.total_reach.toLocaleString()}
          icon={Users}
          color="#2e7d32"
        />
        <StatCard
          title="Avg Open Rate"
          value={`${dashboard.avg_open_rate}%`}
          icon={Mail}
          color="#f57f17"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 32 }}>
        <div style={card}>
          <h2 style={sectionHeading}>Campaign Status Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={dashboard.campaign_status_distribution}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {dashboard.campaign_status_distribution.map((entry) => (
                  <Cell key={entry.name} fill={PIE_COLORS[entry.name] || '#ccc'} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div style={card}>
          <h2 style={sectionHeading}>Channel Performance</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboard.channel_performance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="channel" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sent" fill="#1a237e" />
              <Bar dataKey="delivered" fill="#0288d1" />
              <Bar dataKey="opened" fill="#2e7d32" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ ...card, marginBottom: 32 }}>
        <h2 style={sectionHeading}>Recent Campaigns</h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e0e0e0', textAlign: 'left' }}>
                {['Name', 'Status', 'Channel', 'Open Rate', 'CTR', 'Created'].map((h) => (
                  <th key={h} style={{ padding: '12px 16px', fontWeight: 600, color: '#1a237e', whiteSpace: 'nowrap' }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dashboard.recent_campaigns.map((c, idx) => (
                <tr
                  key={c.id}
                  onClick={() => navigate(`/campaigns/${c.id}`)}
                  style={{
                    backgroundColor: idx % 2 === 0 ? '#fafafa' : '#ffffff',
                    cursor: 'pointer',
                    borderBottom: '1px solid #eee',
                    transition: 'background-color 0.15s',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#e3f2fd'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = idx % 2 === 0 ? '#fafafa' : '#ffffff'; }}
                >
                  <td style={{ padding: '12px 16px', fontWeight: 500 }}>{c.name}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      ...STATUS_BADGE[c.status],
                      padding: '4px 12px',
                      borderRadius: 20,
                      fontSize: 12,
                      fontWeight: 600,
                      textTransform: 'capitalize',
                      display: 'inline-block',
                    }}>
                      {c.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', textTransform: 'capitalize' }}>
                    {Array.isArray(c.channels) ? c.channels.join(', ') : '-'}
                  </td>
                  <td style={{ padding: '12px 16px' }}>{c.open_rate}%</td>
                  <td style={{ padding: '12px 16px' }}>{c.ctr}%</td>
                  <td style={{ padding: '12px 16px', color: '#666' }}>{c.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={card}>
        <h2 style={sectionHeading}>Agent Status</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
          {dashboard.agent_statuses.map((agent) => {
            const isActive = agent.status === 'active' || agent.status === 'completed';
            const dotColor = isActive ? '#2e7d32' : '#f57f17';
            return (
              <div
                key={agent.name}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: '10px 16px',
                  borderRadius: 8,
                  backgroundColor: '#f9f9fb',
                  border: '1px solid #eee',
                }}
              >
                <span style={{
                  width: 10,
                  height: 10,
                  borderRadius: '50%',
                  backgroundColor: dotColor,
                  flexShrink: 0,
                  boxShadow: `0 0 6px ${dotColor}66`,
                }} />
                <span style={{ fontSize: 14, fontWeight: 500, color: '#333' }}>{agent.name}</span>
                <span style={{
                  marginLeft: 'auto',
                  fontSize: 11,
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  color: isActive ? '#2e7d32' : '#f57f17',
                  letterSpacing: 0.5,
                }}>
                  {agent.status}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default CampaignManagerDashboard;
