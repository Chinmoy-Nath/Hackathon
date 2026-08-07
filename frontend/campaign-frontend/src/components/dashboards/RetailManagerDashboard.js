import React, { useState, useEffect } from 'react';
import { IndianRupee, TrendingUp, Car, Store } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { analyticsAPI } from '../../services/api';
import StatCard from '../common/StatCard';
import LoadingSpinner from '../common/LoadingSpinner';

const defaultData = {
  revenue: 125000000,
  roi: 285,
  conversions: 142,
  active_dealers: 85,
  revenue_trend: [
    { month: 'Feb', revenue: 15000000 },
    { month: 'Mar', revenue: 18000000 },
    { month: 'Apr', revenue: 22000000 },
    { month: 'May', revenue: 19000000 },
    { month: 'Jun', revenue: 25000000 },
    { month: 'Jul', revenue: 28000000 },
  ],
  vehicle_segment_performance: [
    { segment: 'Mid Range', campaigns: 8, conversions: 65, revenue: 35000000 },
    { segment: 'Premium', campaigns: 5, conversions: 52, revenue: 55000000 },
    { segment: 'Luxury', campaigns: 2, conversions: 25, revenue: 35000000 },
  ],
  dealer_performance: [
    { state: 'Maharashtra', revenue: 28000000 },
    { state: 'Karnataka', revenue: 22000000 },
    { state: 'Tamil Nadu', revenue: 18000000 },
    { state: 'Delhi NCR', revenue: 16000000 },
    { state: 'Gujarat', revenue: 14000000 },
    { state: 'Telangana', revenue: 12000000 },
    { state: 'West Bengal', revenue: 8000000 },
    { state: 'Rajasthan', revenue: 7000000 },
  ],
  campaign_effectiveness: [
    { name: 'Diwali Nexon EV', reach: 500, conversions: 42, revenue: 38000000, roi: 380, effectiveness: 92 },
    { name: 'Curvv Summer', reach: 350, conversions: 35, revenue: 32000000, roi: 320, effectiveness: 88 },
    { name: 'Safari Premium', reach: 200, conversions: 28, revenue: 28000000, roi: 280, effectiveness: 85 },
    { name: 'Punch City Drive', reach: 400, conversions: 37, revenue: 18000000, roi: 180, effectiveness: 78 },
  ],
  recommendation_distribution: [
    { name: 'Accepted', value: 68 },
    { name: 'Pending', value: 20 },
    { name: 'Ignored', value: 12 },
  ],
};

const formatINR = (value) => {
  if (value >= 10000000) return `\u20B9${(value / 10000000).toFixed(1)} Cr`;
  if (value >= 100000) return `\u20B9${(value / 100000).toFixed(1)} L`;
  return `\u20B9${value.toLocaleString('en-IN')}`;
};

const PIE_COLORS = { Accepted: '#1a237e', Pending: '#0288d1', Ignored: '#9e9e9e' };

const SEGMENT_COLORS = { campaigns: '#1a237e', conversions: '#0288d1', revenue: '#26a69a' };

function RetailManagerDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    analyticsAPI.getRetailManagerDashboard()
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

  const revSummary = raw.revenue_summary || {};
  const kpis = raw.executive_kpis || {};
  const dashboard = {
    revenue: raw.revenue || revSummary.total_revenue || kpis.total_revenue || defaultData.revenue,
    roi: raw.roi || revSummary.overall_roi || kpis.overall_roi || defaultData.roi,
    conversions: raw.conversions || revSummary.total_purchases || defaultData.conversions,
    active_dealers: raw.active_dealers || (Array.isArray(raw.dealer_performance) ? raw.dealer_performance.reduce((a, d) => a + (d.dealer_count || 0), 0) : defaultData.active_dealers),
    revenue_trend: raw.revenue_trend || defaultData.revenue_trend,
    vehicle_segment_performance: raw.vehicle_segment_performance || defaultData.vehicle_segment_performance,
    dealer_performance: raw.dealer_performance || defaultData.dealer_performance,
    campaign_effectiveness: raw.campaign_effectiveness || defaultData.campaign_effectiveness,
    recommendation_distribution: raw.recommendation_distribution || defaultData.recommendation_distribution,
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

  const vsp = dashboard.vehicle_segment_performance;
  const maxRevenue = Math.max(...vsp.map((x) => x.revenue || 1), 1);
  const maxConversions = Math.max(...vsp.map((x) => x.conversions || 1), 1);
  const maxCampaigns = Math.max(...vsp.map((x) => x.campaigns || 1), 1);
  const segmentNormalized = vsp.map((s) => ({
    segment: s.segment,
    campaigns: Math.round(((s.campaigns || 0) / maxCampaigns) * 100),
    conversions: Math.round(((s.conversions || 0) / maxConversions) * 100),
    revenue: Math.round(((s.revenue || 0) / maxRevenue) * 100),
  }));

  const sortedCampaigns = [...(dashboard.campaign_effectiveness || [])].sort(
    (a, b) => (b.effectiveness || 0) - (a.effectiveness || 0),
  );

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, color: '#1a237e', marginBottom: 24 }}>
        Retail Manager Dashboard
      </h1>

      {error && (
        <div style={{ backgroundColor: '#fff3e0', color: '#e65100', padding: '10px 16px', borderRadius: 8, marginBottom: 20, fontSize: 14 }}>
          {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20, marginBottom: 32 }}>
        <StatCard
          title="Total Revenue"
          value={formatINR(dashboard.revenue)}
          icon={IndianRupee}
          color="#1a237e"
          trend={{ direction: 'up', value: '+18.3%' }}
        />
        <StatCard
          title="Campaign ROI"
          value={`${dashboard.roi}%`}
          icon={TrendingUp}
          color="#0288d1"
          trend={{ direction: 'up', value: '+24%' }}
        />
        <StatCard
          title="Vehicle Conversions"
          value={dashboard.conversions}
          icon={Car}
          color="#2e7d32"
          trend={{ direction: 'up', value: '+32%' }}
        />
        <StatCard
          title="Active Dealers"
          value={dashboard.active_dealers}
          icon={Store}
          color="#f57f17"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 32 }}>
        <div style={card}>
          <h2 style={sectionHeading}>Revenue Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={dashboard.revenue_trend}>
              <defs>
                <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#1a237e" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#1a237e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis tickFormatter={(v) => formatINR(v)} />
              <Tooltip formatter={(v) => formatINR(v)} />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#1a237e"
                strokeWidth={2}
                fill="url(#revenueGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div style={card}>
          <h2 style={sectionHeading}>Vehicle Segment Performance</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={segmentNormalized}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="segment" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="campaigns" fill={SEGMENT_COLORS.campaigns} />
              <Bar dataKey="conversions" fill={SEGMENT_COLORS.conversions} />
              <Bar dataKey="revenue" fill={SEGMENT_COLORS.revenue} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 32 }}>
        <div style={card}>
          <h2 style={sectionHeading}>Dealer Performance by State</h2>
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={dashboard.dealer_performance} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={(v) => formatINR(v)} />
              <YAxis type="category" dataKey="state" width={100} />
              <Tooltip formatter={(v) => formatINR(v)} />
              <Bar dataKey="revenue" fill="#0288d1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={card}>
          <h2 style={sectionHeading}>Recommendation Effectiveness</h2>
          <ResponsiveContainer width="100%" height={360}>
            <PieChart>
              <Pie
                data={dashboard.recommendation_distribution}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={120}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {dashboard.recommendation_distribution.map((entry) => (
                  <Cell key={entry.name} fill={PIE_COLORS[entry.name] || '#ccc'} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ ...card, marginBottom: 32 }}>
        <h2 style={sectionHeading}>Campaign Effectiveness</h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e0e0e0', textAlign: 'left' }}>
                {['Campaign', 'Reach', 'Conversions', 'Revenue', 'ROI', 'Effectiveness'].map((h) => (
                  <th key={h} style={{ padding: '12px 16px', fontWeight: 600, color: '#1a237e', whiteSpace: 'nowrap' }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sortedCampaigns.map((c, idx) => (
                <tr
                  key={c.name}
                  style={{
                    backgroundColor: idx % 2 === 0 ? '#fafafa' : '#ffffff',
                    borderBottom: '1px solid #eee',
                  }}
                >
                  <td style={{ padding: '12px 16px', fontWeight: 500 }}>{c.name}</td>
                  <td style={{ padding: '12px 16px' }}>{(c.reach || 0).toLocaleString()}</td>
                  <td style={{ padding: '12px 16px' }}>{c.conversions || 0}</td>
                  <td style={{ padding: '12px 16px' }}>{formatINR(c.revenue || 0)}</td>
                  <td style={{ padding: '12px 16px' }}>{c.roi || 0}%</td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ flex: 1, height: 8, backgroundColor: '#e0e0e0', borderRadius: 4, overflow: 'hidden' }}>
                        <div style={{ width: `${c.effectiveness || 0}%`, height: '100%', backgroundColor: (c.effectiveness || 0) >= 85 ? '#1a237e' : '#0288d1', borderRadius: 4 }} />
                      </div>
                      <span style={{ fontWeight: 600, color: '#1a237e', minWidth: 32 }}>{c.effectiveness || 0}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default RetailManagerDashboard;
