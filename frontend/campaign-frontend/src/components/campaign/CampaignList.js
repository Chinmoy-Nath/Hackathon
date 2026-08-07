import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlusCircle, Search, Megaphone } from 'lucide-react';
import { campaignAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../common/LoadingSpinner';

const defaultCampaigns = [
  { campaign_id: 'c1', name: 'Diwali Nexon EV Launch', objective: 'Product Launch', status: 'active', vehicle_name: 'Nexon EV', channels: '["email","whatsapp"]', budget: 500000, created_at: '2026-07-15' },
  { campaign_id: 'c2', name: 'Curvv Summer Drive', objective: 'Awareness', status: 'completed', vehicle_name: 'Curvv EV', channels: '["email","sms","instagram"]', budget: 350000, created_at: '2026-07-10' },
  { campaign_id: 'c3', name: 'Safari Premium Experience', objective: 'Conversion', status: 'active', vehicle_name: 'Safari', channels: '["email","instagram"]', budget: 750000, created_at: '2026-07-05' },
  { campaign_id: 'c4', name: 'Punch City Drive Festival', objective: 'Engagement', status: 'draft', vehicle_name: 'Punch', channels: '["whatsapp","sms"]', budget: 200000, created_at: '2026-07-20' },
  { campaign_id: 'c5', name: 'Tiago EV Green Initiative', objective: 'Retention', status: 'paused', vehicle_name: 'Tiago EV', channels: '["email","push"]', budget: 150000, created_at: '2026-06-30' },
];

const STATUS_COLORS = {
  draft: { backgroundColor: '#f5f5f5', color: '#9e9e9e' },
  active: { backgroundColor: '#e3f2fd', color: '#0288d1' },
  completed: { backgroundColor: '#e8f5e9', color: '#2e7d32' },
  paused: { backgroundColor: '#fff8e1', color: '#f57f17' },
  scheduled: { backgroundColor: '#f3e5f5', color: '#7b1fa2' },
};

function parseChannels(channels) {
  if (Array.isArray(channels)) return channels;
  if (typeof channels === 'string') {
    try {
      const parsed = JSON.parse(channels);
      return Array.isArray(parsed) ? parsed : [channels];
    } catch {
      return [channels];
    }
  }
  return [];
}

function CampaignList() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { isCampaignManager } = useAuth();

  useEffect(() => {
    campaignAPI.list()
      .then((res) => {
        const d = res.data;
        setCampaigns(Array.isArray(d) ? d : d?.campaigns || defaultCampaigns);
      })
      .catch(() => {
        setCampaigns(defaultCampaigns);
        setError('Could not load live data. Showing demo data.');
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  const filtered = campaigns.filter((c) => {
    const matchSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.objective?.toLowerCase().includes(search.toLowerCase()) ||
      c.vehicle_name?.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'all' || c.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const card = {
    backgroundColor: '#ffffff',
    borderRadius: 10,
    padding: 24,
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  };

  const sectionHeading = {
    fontSize: 18,
    fontWeight: 600,
    color: '#1a237e',
  };

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Megaphone size={28} color="#1a237e" />
          <h1 style={{ fontSize: 26, fontWeight: 700, color: '#1a237e', margin: 0 }}>Campaigns</h1>
        </div>
        {isCampaignManager && (
          <button
            onClick={() => navigate('/campaigns/create')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 20px',
              backgroundColor: '#1a237e',
              color: '#ffffff',
              border: 'none',
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <PlusCircle size={18} />
            Create New Campaign
          </button>
        )}
      </div>

      {error && (
        <div style={{ backgroundColor: '#fff3e0', color: '#e65100', padding: '10px 16px', borderRadius: 8, marginBottom: 20, fontSize: 14 }}>
          {error}
        </div>
      )}

      <div style={{ ...card, marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: 240 }}>
            <Search size={16} color="#999" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search campaigns by name, objective, or vehicle..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px 10px 36px',
                border: '1px solid #ddd',
                borderRadius: 8,
                fontSize: 14,
                outline: 'none',
                boxSizing: 'border-box',
              }}
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: '10px 16px',
              border: '1px solid #ddd',
              borderRadius: 8,
              fontSize: 14,
              outline: 'none',
              backgroundColor: '#fff',
              cursor: 'pointer',
            }}
          >
            <option value="all">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="paused">Paused</option>
            <option value="scheduled">Scheduled</option>
          </select>
        </div>
      </div>

      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <h2 style={sectionHeading}>{filtered.length} Campaign{filtered.length !== 1 ? 's' : ''}</h2>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e0e0e0', textAlign: 'left' }}>
                {['Name', 'Objective', 'Status', 'Vehicle', 'Channels', 'Budget', 'Created'].map((h) => (
                  <th key={h} style={{ padding: '12px 16px', fontWeight: 600, color: '#1a237e', whiteSpace: 'nowrap' }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ padding: 40, textAlign: 'center', color: '#999' }}>
                    No campaigns found matching your criteria.
                  </td>
                </tr>
              ) : (
                filtered.map((c, idx) => {
                  const channels = parseChannels(c.channels);
                  const badge = STATUS_COLORS[c.status] || STATUS_COLORS.draft;
                  return (
                    <tr
                      key={c.campaign_id}
                      onClick={() => navigate(`/campaigns/${c.campaign_id}`)}
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
                      <td style={{ padding: '12px 16px' }}>{c.objective}</td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{
                          ...badge,
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
                      <td style={{ padding: '12px 16px' }}>{c.vehicle_name}</td>
                      <td style={{ padding: '12px 16px' }}>
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                          {channels.map((ch) => (
                            <span key={ch} style={{
                              padding: '2px 8px',
                              borderRadius: 12,
                              fontSize: 11,
                              fontWeight: 500,
                              backgroundColor: '#e8eaf6',
                              color: '#1a237e',
                              textTransform: 'capitalize',
                            }}>
                              {ch}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td style={{ padding: '12px 16px', whiteSpace: 'nowrap' }}>
                        {'\u20B9'}{(c.budget || 0).toLocaleString('en-IN')}
                      </td>
                      <td style={{ padding: '12px 16px', color: '#666' }}>{c.created_at}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default CampaignList;
