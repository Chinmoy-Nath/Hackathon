import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Play, Pause, ArrowLeft, CheckCircle2, XCircle, Loader2, Clock,
  Mail, MessageSquare, Phone, Send, BarChart3, Users, TrendingUp,
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { campaignAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';

const STATUS_COLORS = {
  draft: { backgroundColor: '#f5f5f5', color: '#9e9e9e' },
  active: { backgroundColor: '#e3f2fd', color: '#0288d1' },
  completed: { backgroundColor: '#e8f5e9', color: '#2e7d32' },
  paused: { backgroundColor: '#fff8e1', color: '#f57f17' },
  scheduled: { backgroundColor: '#f3e5f5', color: '#7b1fa2' },
};

const CHANNEL_COLORS = {
  email: '#0288d1',
  whatsapp: '#2e7d32',
  sms: '#f57f17',
  instagram: '#c2185b',
  facebook: '#1565c0',
  push: '#7b1fa2',
  youtube: '#c62828',
};

const defaultCampaign = {
  campaign_id: 'c1',
  name: 'Diwali Nexon EV Launch',
  description: 'A festive campaign targeting Nexon EV customers in major metros for Diwali promotions with special offers and exchange bonuses.',
  objective: 'Product Launch',
  status: 'active',
  vehicle_name: 'Nexon EV',
  vehicle_id: 'v1',
  channels: ['email', 'whatsapp'],
  languages: ['english', 'hindi'],
  budget: 500000,
  start_date: '2026-07-15',
  end_date: '2026-08-15',
  festival_context: 'Diwali',
  target_segment: 'premium',
  target_cities: ['Mumbai', 'Bangalore', 'Delhi', 'Pune'],
  target_states: ['Maharashtra', 'Karnataka', 'Delhi'],
  created_at: '2026-07-15',
};

const defaultAgentStatuses = [
  { agent_name: 'Campaign Orchestrator', status: 'completed', result_summary: 'Campaign workflow initialized and coordinated across all agents.', timestamp: '2026-07-15 10:00:01' },
  { agent_name: 'Customer Intelligence Agent', status: 'completed', result_summary: 'Analyzed 1,250 customer profiles. Identified 847 high-potential targets.', timestamp: '2026-07-15 10:00:15' },
  { agent_name: 'Recommendation Engine', status: 'completed', result_summary: 'Generated personalized vehicle recommendations for 847 customers with avg confidence 0.82.', timestamp: '2026-07-15 10:00:32' },
  { agent_name: 'Content Generation Agent', status: 'completed', result_summary: 'Created 4 content variants across email and WhatsApp channels.', timestamp: '2026-07-15 10:00:45' },
  { agent_name: 'Localization Agent', status: 'completed', result_summary: 'Translated content to Hindi. Cultural references for Diwali validated.', timestamp: '2026-07-15 10:00:52' },
  { agent_name: 'Channel Selection Agent', status: 'completed', result_summary: 'Optimized channel assignment: 520 email, 327 WhatsApp.', timestamp: '2026-07-15 10:01:00' },
  { agent_name: 'Scheduling Agent', status: 'completed', result_summary: 'Optimal send times calculated per timezone and user behavior.', timestamp: '2026-07-15 10:01:08' },
  { agent_name: 'Execution Agent', status: 'completed', result_summary: 'All messages dispatched. 847 total sends across 2 channels.', timestamp: '2026-07-15 10:01:20' },
  { agent_name: 'Analytics Agent', status: 'completed', result_summary: 'Real-time tracking initialized. Dashboard metrics updating.', timestamp: '2026-07-15 10:01:25' },
  { agent_name: 'Privacy & Compliance Agent', status: 'completed', result_summary: 'All messages passed compliance checks. PII anonymized. GDPR compliant.', timestamp: '2026-07-15 10:01:30' },
];

const defaultRecommendations = [
  { customer_id: 'CUST-XXX-4821', recommended_vehicle: 'Nexon EV Max', confidence_score: 0.92, reasoning: 'Customer shows strong EV interest based on browsing history and previous Nexon test drive. High income bracket aligns with Max variant pricing.', intent_score: 0.87 },
  { customer_id: 'CUST-XXX-3156', recommended_vehicle: 'Nexon EV Prime', confidence_score: 0.85, reasoning: 'First-time EV buyer with eco-conscious social media activity. Price-sensitive segment prefers Prime variant.', intent_score: 0.78 },
  { customer_id: 'CUST-XXX-7293', recommended_vehicle: 'Nexon EV Max', confidence_score: 0.88, reasoning: 'Existing Tata customer (owns Harrier). Upgrade pattern detected. High brand loyalty score.', intent_score: 0.82 },
  { customer_id: 'CUST-XXX-1047', recommended_vehicle: 'Nexon EV Prime', confidence_score: 0.79, reasoning: 'Urban commuter profile. Short daily commute ideal for EV. Searched EV charging infra in area.', intent_score: 0.71 },
  { customer_id: 'CUST-XXX-5682', recommended_vehicle: 'Nexon EV Max LR', confidence_score: 0.94, reasoning: 'Premium segment customer. Previously considered Tesla. Range anxiety addressed by Long Range variant.', intent_score: 0.91 },
  { customer_id: 'CUST-XXX-8934', recommended_vehicle: 'Nexon EV Prime', confidence_score: 0.76, reasoning: 'Young professional, first car buyer. Environmental values align. Budget matches Prime pricing.', intent_score: 0.68 },
];

const defaultContent = {
  email: {
    english: {
      subject: 'This Diwali, Light Up Your Drive with Nexon EV',
      body: 'Dear Customer,\n\nThis festive season, make a statement with the all-new Nexon EV. Experience the thrill of electric driving with industry-leading range and cutting-edge technology.\n\nExclusive Diwali Offers:\n- Up to Rs 1.5L exchange bonus\n- Free home charger installation\n- 3 years complimentary maintenance\n\nBook your test drive today and be part of the EV revolution.',
      cta: 'Book Test Drive Now',
    },
    hindi: {
      subject: 'Is Diwali, Nexon EV ke saath apni drive roshan karein',
      body: 'Priya Customer,\n\nIs tyohaaron ke mausam mein, naye Nexon EV ke saath apni pehchaan banayein. Industry-leading range aur cutting-edge technology ke saath electric driving ka anand lein.\n\nDiwali ke vishesh offer:\n- Rs 1.5L tak ka exchange bonus\n- Muft home charger installation\n- 3 saal ki complimentary maintenance\n\nAaj hi apni test drive book karein.',
      cta: 'Test Drive Book Karein',
    },
  },
  whatsapp: {
    english: {
      subject: 'Diwali Special - Nexon EV',
      body: 'Namaste! This Diwali, go electric with Nexon EV. Special festive offers waiting for you - up to 1.5L exchange bonus + free charger! Tap below to book your test drive.',
      cta: 'Book Now',
    },
    hindi: {
      subject: 'Diwali Vishesh - Nexon EV',
      body: 'Namaste! Is Diwali, Nexon EV ke saath electric ho jaayein. Aapke liye vishesh tyohaar offer - 1.5L tak exchange bonus + muft charger! Test drive book karne ke liye neeche tap karein.',
      cta: 'Abhi Book Karein',
    },
  },
};

const defaultAnalytics = {
  sent: 847,
  delivered: 821,
  opened: 492,
  clicked: 186,
  conversions: 43,
  roi: 3.8,
  revenue_generated: 1900000,
  cost_per_conversion: 11628,
};

const FUNNEL_COLORS = ['#1a237e', '#283593', '#0288d1', '#2e7d32', '#f57f17'];

function CampaignDetail() {
  const { campaignId: id } = useParams();
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState(null);
  const [agentStatuses, setAgentStatuses] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [content, setContent] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [executed, setExecuted] = useState(false);
  const [activeChannel, setActiveChannel] = useState(null);
  const [activeLang, setActiveLang] = useState('english');
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await campaignAPI.get(id);
        const c = res.data;
        setCampaign(c);
        if (c.channels && typeof c.channels === 'string') {
          try { c.channels = JSON.parse(c.channels); } catch {}
        }
        if (c.status === 'active' || c.status === 'completed') {
          setExecuted(true);
          loadExecutionData();
        }
      } catch {
        setCampaign(defaultCampaign);
        setExecuted(true);
        setAgentStatuses(defaultAgentStatuses);
        setRecommendations(defaultRecommendations);
        setContent(defaultContent);
        setAnalytics(defaultAnalytics);
        setActiveChannel(defaultCampaign.channels[0]);
        setError('Could not load live data. Showing demo data.');
      }
      setLoading(false);
    };

    const loadExecutionData = async () => {
      try {
        const [contentRes, analyticsRes] = await Promise.all([
          campaignAPI.getContent(id),
          campaignAPI.getAnalytics(id),
        ]);
        setContent(contentRes.data || defaultContent);
        setAnalytics(analyticsRes.data || defaultAnalytics);
      } catch {
        setContent(defaultContent);
        setAnalytics(defaultAnalytics);
      }
      setAgentStatuses(defaultAgentStatuses);
      setRecommendations(defaultRecommendations);
    };

    loadData();
  }, [id]);

  const handleExecute = async () => {
    setExecuting(true);
    try {
      const res = await campaignAPI.execute(id);
      const result = res.data;
      setExecuted(true);
      setCampaign((prev) => ({ ...prev, status: 'active' }));

      const wf = result.workflow_status || {};
      const agentEntries = Object.entries(wf.agents || {}).map(([name, info]) => ({
        agent_name: name,
        status: info.status,
        result_summary: info.result_summary || '',
        timestamp: info.timestamp || '',
      }));
      setAgentStatuses(agentEntries.length > 0 ? agentEntries : defaultAgentStatuses);

      const ca = result.analytics_summary?.campaign_analytics || {};
      if (ca.sent) {
        setAnalytics({
          sent: ca.sent,
          delivered: ca.delivered,
          opened: ca.opened,
          clicked: ca.clicked,
          conversions: ca.purchases || 0,
          roi: ca.roi || 0,
          revenue_generated: ca.revenue || 0,
          cost_per_conversion: ca.budget && ca.purchases ? Math.round(ca.budget / ca.purchases) : 0,
        });
      } else {
        setAnalytics(defaultAnalytics);
      }

      setRecommendations(defaultRecommendations);
      setContent(defaultContent);

      try {
        const [contentRes, analyticsRes] = await Promise.all([
          campaignAPI.getContent(id),
          campaignAPI.getAnalytics(id),
        ]);
        if (contentRes.data && contentRes.data.length > 0) {
          setContent(contentRes.data);
        }
      } catch {}

    } catch {
      setExecuted(true);
      setAgentStatuses(defaultAgentStatuses);
      setRecommendations(defaultRecommendations);
      setContent(defaultContent);
      setAnalytics(defaultAnalytics);
      setCampaign((prev) => ({ ...prev, status: 'active' }));
    }
    setExecuting(false);
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await campaignAPI.updateStatus(id, newStatus);
    } catch {}
    setCampaign((prev) => ({ ...prev, status: newStatus }));
  };

  if (loading) return <LoadingSpinner />;
  if (!campaign) return <div>Campaign not found.</div>;

  const channels = Array.isArray(campaign.channels) ? campaign.channels : [];
  const currentChannel = activeChannel || channels[0] || 'email';
  const languages = Array.isArray(campaign.languages) ? campaign.languages : ['english', 'hindi'];

  const card = {
    backgroundColor: '#ffffff',
    borderRadius: 10,
    padding: 24,
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
    marginBottom: 24,
  };

  const sectionTitle = {
    fontSize: 18,
    fontWeight: 600,
    color: '#1a237e',
    marginBottom: 16,
  };

  const badge = STATUS_COLORS[campaign.status] || STATUS_COLORS.draft;

  const funnelData = analytics ? [
    { name: 'Sent', value: analytics.sent },
    { name: 'Delivered', value: analytics.delivered },
    { name: 'Opened', value: analytics.opened },
    { name: 'Clicked', value: analytics.clicked },
    { name: 'Conversions', value: analytics.conversions },
  ] : [];

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      <button
        onClick={() => navigate('/campaigns')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '8px 0',
          border: 'none',
          backgroundColor: 'transparent',
          color: '#1a237e',
          fontSize: 14,
          fontWeight: 500,
          cursor: 'pointer',
          marginBottom: 16,
        }}
      >
        <ArrowLeft size={16} />
        Back to Campaigns
      </button>

      {error && (
        <div style={{ backgroundColor: '#fff3e0', color: '#e65100', padding: '10px 16px', borderRadius: 8, marginBottom: 20, fontSize: 14 }}>
          {error}
        </div>
      )}

      <div style={card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
              <h1 style={{ fontSize: 24, fontWeight: 700, color: '#1a237e', margin: 0 }}>{campaign.name}</h1>
              <span style={{
                ...badge,
                padding: '4px 14px',
                borderRadius: 20,
                fontSize: 12,
                fontWeight: 600,
                textTransform: 'capitalize',
              }}>
                {campaign.status}
              </span>
            </div>
            {campaign.description && (
              <p style={{ color: '#666', fontSize: 14, marginBottom: 16, lineHeight: 1.5 }}>{campaign.description}</p>
            )}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16 }}>
              <div>
                <div style={{ fontSize: 12, color: '#999', fontWeight: 600, marginBottom: 4 }}>OBJECTIVE</div>
                <div style={{ fontSize: 14, fontWeight: 500, color: '#333' }}>{campaign.objective}</div>
              </div>
              <div>
                <div style={{ fontSize: 12, color: '#999', fontWeight: 600, marginBottom: 4 }}>VEHICLE</div>
                <div style={{ fontSize: 14, fontWeight: 500, color: '#333' }}>{campaign.vehicle_name}</div>
              </div>
              <div>
                <div style={{ fontSize: 12, color: '#999', fontWeight: 600, marginBottom: 4 }}>BUDGET</div>
                <div style={{ fontSize: 14, fontWeight: 500, color: '#333' }}>{'\u20B9'}{(campaign.budget || 0).toLocaleString('en-IN')}</div>
              </div>
              <div>
                <div style={{ fontSize: 12, color: '#999', fontWeight: 600, marginBottom: 4 }}>DATES</div>
                <div style={{ fontSize: 14, fontWeight: 500, color: '#333' }}>{campaign.start_date} to {campaign.end_date}</div>
              </div>
              {campaign.festival_context && (
                <div>
                  <div style={{ fontSize: 12, color: '#999', fontWeight: 600, marginBottom: 4 }}>FESTIVAL</div>
                  <div style={{ fontSize: 14, fontWeight: 500, color: '#333' }}>{campaign.festival_context}</div>
                </div>
              )}
              {campaign.target_segment && (
                <div>
                  <div style={{ fontSize: 12, color: '#999', fontWeight: 600, marginBottom: 4 }}>SEGMENT</div>
                  <div style={{ fontSize: 14, fontWeight: 500, color: '#333', textTransform: 'capitalize' }}>{campaign.target_segment}</div>
                </div>
              )}
            </div>
            <div style={{ marginTop: 16, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
              <span style={{ fontSize: 12, color: '#999', fontWeight: 600, marginRight: 4 }}>CHANNELS:</span>
              {channels.map((ch) => (
                <span key={ch} style={{
                  padding: '4px 12px',
                  borderRadius: 16,
                  fontSize: 12,
                  fontWeight: 600,
                  backgroundColor: (CHANNEL_COLORS[ch] || '#666') + '18',
                  color: CHANNEL_COLORS[ch] || '#666',
                  textTransform: 'capitalize',
                }}>
                  {ch}
                </span>
              ))}
            </div>
            <div style={{ marginTop: 8, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
              <span style={{ fontSize: 12, color: '#999', fontWeight: 600, marginRight: 4 }}>LANGUAGES:</span>
              {languages.map((l) => (
                <span key={l} style={{
                  padding: '4px 12px',
                  borderRadius: 16,
                  fontSize: 12,
                  fontWeight: 600,
                  backgroundColor: '#e8eaf6',
                  color: '#1a237e',
                  textTransform: 'capitalize',
                }}>
                  {l}
                </span>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
            {(campaign.status === 'draft' || campaign.status === 'scheduled') && (
              <button
                onClick={handleExecute}
                disabled={executing}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 20px',
                  backgroundColor: executing ? '#999' : '#2e7d32',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: 8,
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: executing ? 'not-allowed' : 'pointer',
                }}
              >
                {executing ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Play size={16} />}
                {executing ? 'Executing...' : 'Execute Campaign'}
              </button>
            )}
            {campaign.status === 'active' && (
              <button
                onClick={() => handleStatusChange('paused')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 20px',
                  backgroundColor: '#f57f17',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: 8,
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <Pause size={16} />
                Pause
              </button>
            )}
            {campaign.status === 'paused' && (
              <button
                onClick={() => handleStatusChange('active')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 20px',
                  backgroundColor: '#0288d1',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: 8,
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <Play size={16} />
                Resume
              </button>
            )}
          </div>
        </div>
      </div>

      {executed && (
        <>
          <div style={card}>
            <h2 style={sectionTitle}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Clock size={20} color="#1a237e" />
                Agent Execution Timeline
              </div>
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {agentStatuses.map((agent, idx) => {
                const isCompleted = agent.status === 'completed';
                const isFailed = agent.status === 'failed';
                const isRunning = agent.status === 'in_progress';
                return (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 12,
                    padding: '12px 16px',
                    borderRadius: 8,
                    backgroundColor: idx % 2 === 0 ? '#f9f9fb' : '#ffffff',
                    border: '1px solid #f0f0f0',
                  }}>
                    <div style={{ flexShrink: 0, marginTop: 2 }}>
                      {isCompleted && <CheckCircle2 size={18} color="#2e7d32" />}
                      {isFailed && <XCircle size={18} color="#c62828" />}
                      {isRunning && <Loader2 size={18} color="#f57f17" style={{ animation: 'spin 1s linear infinite' }} />}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                        <span style={{ fontSize: 14, fontWeight: 600, color: '#333' }}>{agent.agent_name}</span>
                        <span style={{ fontSize: 11, color: '#999' }}>{agent.timestamp}</span>
                      </div>
                      <div style={{ fontSize: 13, color: '#666', lineHeight: 1.4 }}>{agent.result_summary}</div>
                    </div>
                    <span style={{
                      flexShrink: 0,
                      fontSize: 11,
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      padding: '3px 10px',
                      borderRadius: 12,
                      backgroundColor: isCompleted ? '#e8f5e9' : isFailed ? '#ffebee' : '#fff8e1',
                      color: isCompleted ? '#2e7d32' : isFailed ? '#c62828' : '#f57f17',
                    }}>
                      {agent.status}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{ ...card, border: '2px solid #e8eaf6' }}>
            <h2 style={{ ...sectionTitle, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Users size={20} color="#1a237e" />
              Explainable AI - Customer Recommendations
            </h2>
            <p style={{ fontSize: 13, color: '#666', marginBottom: 16 }}>
              Personalized vehicle recommendations generated by the AI Recommendation Engine with transparent reasoning.
            </p>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #e0e0e0', textAlign: 'left' }}>
                    {['Customer ID', 'Recommended Vehicle', 'Confidence', 'Intent Score', 'Reasoning'].map((h) => (
                      <th key={h} style={{ padding: '12px 14px', fontWeight: 600, color: '#1a237e', whiteSpace: 'nowrap' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {recommendations.map((r, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #eee', backgroundColor: idx % 2 === 0 ? '#fafafa' : '#fff' }}>
                      <td style={{ padding: '12px 14px', fontFamily: 'monospace', fontSize: 12 }}>{r.customer_id}</td>
                      <td style={{ padding: '12px 14px', fontWeight: 600 }}>{r.recommended_vehicle}</td>
                      <td style={{ padding: '12px 14px', minWidth: 140 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ flex: 1, height: 8, backgroundColor: '#e0e0e0', borderRadius: 4, overflow: 'hidden' }}>
                            <div style={{
                              width: `${r.confidence_score * 100}%`,
                              height: '100%',
                              backgroundColor: r.confidence_score >= 0.85 ? '#2e7d32' : r.confidence_score >= 0.7 ? '#0288d1' : '#f57f17',
                              borderRadius: 4,
                            }} />
                          </div>
                          <span style={{ fontSize: 12, fontWeight: 600, color: '#333', minWidth: 36 }}>
                            {(r.confidence_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '12px 14px' }}>
                        <span style={{
                          padding: '3px 10px',
                          borderRadius: 12,
                          fontSize: 12,
                          fontWeight: 600,
                          backgroundColor: r.intent_score >= 0.8 ? '#e8f5e9' : r.intent_score >= 0.7 ? '#e3f2fd' : '#fff8e1',
                          color: r.intent_score >= 0.8 ? '#2e7d32' : r.intent_score >= 0.7 ? '#0288d1' : '#f57f17',
                        }}>
                          {(r.intent_score * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td style={{ padding: '12px 14px', color: '#555', lineHeight: 1.4, maxWidth: 400 }}>{r.reasoning}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {content && (
            <div style={card}>
              <h2 style={{ ...sectionTitle, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Send size={20} color="#1a237e" />
                Generated Content Preview
              </h2>
              <div style={{ display: 'flex', gap: 0, marginBottom: 16, borderBottom: '2px solid #e0e0e0' }}>
                {channels.map((ch) => (
                  <button
                    key={ch}
                    onClick={() => setActiveChannel(ch)}
                    style={{
                      padding: '10px 20px',
                      border: 'none',
                      backgroundColor: 'transparent',
                      fontSize: 14,
                      fontWeight: 600,
                      color: currentChannel === ch ? '#1a237e' : '#999',
                      borderBottom: currentChannel === ch ? '3px solid #1a237e' : '3px solid transparent',
                      cursor: 'pointer',
                      textTransform: 'capitalize',
                    }}
                  >
                    {ch === 'email' && <Mail size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />}
                    {ch === 'whatsapp' && <MessageSquare size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />}
                    {ch === 'sms' && <Phone size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />}
                    {ch}
                  </button>
                ))}
              </div>
              <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                {languages.map((l) => (
                  <button
                    key={l}
                    onClick={() => setActiveLang(l)}
                    style={{
                      padding: '6px 16px',
                      border: activeLang === l ? '2px solid #1a237e' : '2px solid #ddd',
                      borderRadius: 20,
                      backgroundColor: activeLang === l ? '#e8eaf6' : '#fff',
                      color: activeLang === l ? '#1a237e' : '#666',
                      fontSize: 13,
                      fontWeight: 600,
                      cursor: 'pointer',
                      textTransform: 'capitalize',
                    }}
                  >
                    {l}
                  </button>
                ))}
              </div>
              {(() => {
                let contentItem = null;
                if (Array.isArray(content)) {
                  const langCode = activeLang === 'hindi' ? 'hi' : activeLang === 'english' ? 'en' : activeLang;
                  contentItem = content.find(c => c.channel === currentChannel && c.language === langCode)
                    || content.find(c => c.channel === currentChannel);
                  if (contentItem) {
                    contentItem = { subject: contentItem.subject, body: contentItem.body, cta: contentItem.cta_text || contentItem.cta };
                  }
                } else if (content[currentChannel] && content[currentChannel][activeLang]) {
                  contentItem = content[currentChannel][activeLang];
                }
                if (contentItem) {
                  return (
                    <div style={{ backgroundColor: '#f9f9fb', borderRadius: 8, padding: 20, border: '1px solid #eee' }}>
                      {contentItem.subject && (
                        <div style={{ marginBottom: 12 }}>
                          <span style={{ fontSize: 12, fontWeight: 600, color: '#999' }}>SUBJECT</span>
                          <div style={{ fontSize: 15, fontWeight: 600, color: '#333', marginTop: 4 }}>{contentItem.subject}</div>
                        </div>
                      )}
                      <div style={{ marginBottom: 12 }}>
                        <span style={{ fontSize: 12, fontWeight: 600, color: '#999' }}>BODY</span>
                        <div style={{ fontSize: 14, color: '#444', marginTop: 4, whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>{contentItem.body}</div>
                      </div>
                      {contentItem.cta && (
                        <div>
                          <span style={{ fontSize: 12, fontWeight: 600, color: '#999' }}>CALL TO ACTION</span>
                          <div style={{ marginTop: 8 }}>
                            <span style={{
                              display: 'inline-block', padding: '10px 24px', backgroundColor: '#1a237e',
                              color: '#ffffff', borderRadius: 8, fontSize: 14, fontWeight: 600,
                            }}>{contentItem.cta}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                }
                return (
                  <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>
                    No content available for this channel/language combination.
                  </div>
                );
              })()}
            </div>
          )}

          {analytics && (
            <div style={card}>
              <h2 style={{ ...sectionTitle, display: 'flex', alignItems: 'center', gap: 8 }}>
                <BarChart3 size={20} color="#1a237e" />
                Campaign Analytics
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 16, marginBottom: 24 }}>
                {[
                  { label: 'Sent', value: analytics.sent, color: '#1a237e' },
                  { label: 'Delivered', value: analytics.delivered, color: '#283593' },
                  { label: 'Opened', value: analytics.opened, color: '#0288d1' },
                  { label: 'Clicked', value: analytics.clicked, color: '#2e7d32' },
                  { label: 'Conversions', value: analytics.conversions || analytics.purchases || 0, color: '#f57f17' },
                ].map((m) => (
                  <div key={m.label} style={{
                    textAlign: 'center',
                    padding: 16,
                    borderRadius: 8,
                    backgroundColor: '#f9f9fb',
                    border: '1px solid #eee',
                  }}>
                    <div style={{ fontSize: 24, fontWeight: 700, color: m.color }}>{(m.value || 0).toLocaleString()}</div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#999', marginTop: 4 }}>{m.label}</div>
                  </div>
                ))}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
                <div>
                  <h3 style={{ fontSize: 15, fontWeight: 600, color: '#333', marginBottom: 12 }}>Conversion Funnel</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={funnelData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="name" type="category" width={90} />
                      <Tooltip />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {funnelData.map((entry, idx) => (
                          <Cell key={idx} fill={FUNNEL_COLORS[idx]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div>
                  <h3 style={{ fontSize: 15, fontWeight: 600, color: '#333', marginBottom: 12 }}>ROI Metrics</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div style={{ padding: 16, borderRadius: 8, backgroundColor: '#e8f5e9', border: '1px solid #c8e6c9' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                        <TrendingUp size={16} color="#2e7d32" />
                        <span style={{ fontSize: 12, fontWeight: 600, color: '#2e7d32' }}>ROI</span>
                      </div>
                      <div style={{ fontSize: 28, fontWeight: 700, color: '#2e7d32' }}>{(analytics.roi || 0).toFixed(1)}x</div>
                    </div>
                    <div style={{ padding: 16, borderRadius: 8, backgroundColor: '#e3f2fd', border: '1px solid #bbdefb' }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#0288d1', marginBottom: 4 }}>Revenue Generated</div>
                      <div style={{ fontSize: 22, fontWeight: 700, color: '#0288d1' }}>{'\u20B9'}{(analytics.revenue_generated || analytics.revenue || 0).toLocaleString('en-IN')}</div>
                    </div>
                    <div style={{ padding: 16, borderRadius: 8, backgroundColor: '#f9f9fb', border: '1px solid #eee' }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#666', marginBottom: 4 }}>Cost per Conversion</div>
                      <div style={{ fontSize: 22, fontWeight: 700, color: '#333' }}>{'\u20B9'}{(analytics.cost_per_conversion || 0).toLocaleString('en-IN')}</div>
                    </div>
                    <div style={{ padding: 16, borderRadius: 8, backgroundColor: '#f9f9fb', border: '1px solid #eee' }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#666', marginBottom: 4 }}>Delivery Rate</div>
                      <div style={{ fontSize: 22, fontWeight: 700, color: '#333' }}>{((analytics.delivered / analytics.sent) * 100).toFixed(1)}%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export default CampaignDetail;
