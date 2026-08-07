import React, { useState, useEffect } from 'react';
import { Users, Search, ChevronDown, ChevronUp, User, Car, Brain, Sparkles } from 'lucide-react';
import { customerAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import StatCard from '../components/common/StatCard';

const defaultCustomers = [
  { customer_id: 'cust001abc1234', name: 'Rajesh Sharma', city: 'Mumbai', state: 'Maharashtra', segment: 'premium', intent_level: 'High', preferred_channel: 'email', language: 'Hindi', persona: 'Tech-savvy professional seeking premium EVs with cutting-edge features', buying_intent: { score: 0.87, signals: ['Visited EV showroom twice', 'Downloaded brochure', 'Compared Nexon EV vs competitors'] }, vehicle_ownership: { current: 'Tata Nexon (2022)', history: ['Maruti Swift (2018)'] } },
  { customer_id: 'cust002def5678', name: 'Priya Patel', city: 'Ahmedabad', state: 'Gujarat', segment: 'luxury', intent_level: 'High', preferred_channel: 'whatsapp', language: 'Gujarati', persona: 'Affluent business owner looking for luxury SUV upgrade', buying_intent: { score: 0.92, signals: ['Requested test drive', 'Asked about financing options', 'Visited Safari page 5 times'] }, vehicle_ownership: { current: 'Tata Harrier (2023)', history: ['Honda City (2019)', 'Hyundai Creta (2020)'] } },
  { customer_id: 'cust003ghi9012', name: 'Amit Kumar', city: 'Delhi', state: 'Delhi', segment: 'mid_range', intent_level: 'Medium', preferred_channel: 'sms', language: 'Hindi', persona: 'Budget-conscious family man seeking reliable daily commuter', buying_intent: { score: 0.55, signals: ['Browsed Tiago page', 'Compared fuel efficiency'] }, vehicle_ownership: { current: 'Maruti Alto (2020)', history: [] } },
  { customer_id: 'cust004jkl3456', name: 'Sneha Reddy', city: 'Hyderabad', state: 'Telangana', segment: 'premium', intent_level: 'Medium', preferred_channel: 'email', language: 'Telugu', persona: 'Young IT professional interested in stylish compact SUVs', buying_intent: { score: 0.63, signals: ['Subscribed to newsletter', 'Watched Punch review videos'] }, vehicle_ownership: { current: 'Hyundai i20 (2021)', history: [] } },
  { customer_id: 'cust005mno7890', name: 'Vikram Singh', city: 'Jaipur', state: 'Rajasthan', segment: 'luxury', intent_level: 'Low', preferred_channel: 'instagram', language: 'Hindi', persona: 'Established entrepreneur browsing luxury segment casually', buying_intent: { score: 0.25, signals: ['Liked Safari Instagram post'] }, vehicle_ownership: { current: 'Toyota Fortuner (2023)', history: ['Tata Safari (2019)'] } },
  { customer_id: 'cust006pqr1234', name: 'Deepa Nair', city: 'Kochi', state: 'Kerala', segment: 'mid_range', intent_level: 'High', preferred_channel: 'whatsapp', language: 'Malayalam', persona: 'Environmentally conscious teacher interested in EVs', buying_intent: { score: 0.81, signals: ['Attended EV expo', 'Enquired about Tiago EV price', 'Requested dealer callback'] }, vehicle_ownership: { current: 'None', history: [] } },
  { customer_id: 'cust007stu5678', name: 'Arjun Mehta', city: 'Pune', state: 'Maharashtra', segment: 'premium', intent_level: 'High', preferred_channel: 'email', language: 'Marathi', persona: 'Auto enthusiast looking for performance-oriented SUV', buying_intent: { score: 0.88, signals: ['Booked test drive for Curvv', 'Compared with competitors', 'Visited showroom'] }, vehicle_ownership: { current: 'Tata Altroz (2022)', history: ['Maruti Baleno (2019)'] } },
  { customer_id: 'cust008vwx9012', name: 'Kavitha Iyer', city: 'Chennai', state: 'Tamil Nadu', segment: 'mid_range', intent_level: 'Low', preferred_channel: 'sms', language: 'Tamil', persona: 'Retired professional, occasional car browser', buying_intent: { score: 0.18, signals: ['Opened one email campaign'] }, vehicle_ownership: { current: 'Tata Indica (2017)', history: [] } },
  { customer_id: 'cust009yza3456', name: 'Rohit Banerjee', city: 'Kolkata', state: 'West Bengal', segment: 'mid_range', intent_level: 'Medium', preferred_channel: 'whatsapp', language: 'Bengali', persona: 'Young professional considering first car purchase', buying_intent: { score: 0.52, signals: ['Compared Punch vs Creta', 'Checked EMI calculator'] }, vehicle_ownership: { current: 'None', history: [] } },
  { customer_id: 'cust010bcd7890', name: 'Ananya Gupta', city: 'Bangalore', state: 'Karnataka', segment: 'luxury', intent_level: 'Medium', preferred_channel: 'email', language: 'Kannada', persona: 'Startup founder evaluating premium EVs for sustainability goals', buying_intent: { score: 0.65, signals: ['Downloaded Nexon EV brochure', 'Attended webinar on EVs'] }, vehicle_ownership: { current: 'MG ZS EV (2023)', history: ['Honda Jazz (2020)'] } },
];

const defaultSegmentSummary = [
  { segment: 'mid_range', count: 4, avg_intent_score: 0.42, top_channels: ['whatsapp', 'sms'] },
  { segment: 'premium', count: 3, avg_intent_score: 0.79, top_channels: ['email'] },
  { segment: 'luxury', count: 3, avg_intent_score: 0.61, top_channels: ['email', 'whatsapp'] },
];

const INTENT_COLORS = {
  Low: { backgroundColor: '#fce4ec', color: '#c62828' },
  Medium: { backgroundColor: '#fff8e1', color: '#f57f17' },
  High: { backgroundColor: '#e8f5e9', color: '#2e7d32' },
};

const SEGMENT_COLORS = {
  mid_range: { backgroundColor: '#e3f2fd', color: '#0288d1' },
  premium: { backgroundColor: '#f3e5f5', color: '#7b1fa2' },
  luxury: { backgroundColor: '#fff8e1', color: '#b8860b' },
};

const defaultRecommendation = {
  recommended_vehicle: 'Nexon EV',
  confidence: 85,
  reasoning: 'Based on customer browsing history, EV interest signals, and budget alignment with the premium segment.',
  alternative: 'Tata Curvv EV',
};

const styles = {
  container: { maxWidth: 1400, margin: '0 auto' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 },
  headerLeft: { display: 'flex', alignItems: 'center', gap: 12 },
  title: { fontSize: 26, fontWeight: 700, color: '#1a237e', margin: 0 },
  card: { backgroundColor: '#ffffff', borderRadius: 10, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' },
  filterRow: { display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap', marginBottom: 24 },
  searchWrap: { position: 'relative', flex: 1, minWidth: 240 },
  searchIcon: { position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' },
  searchInput: { width: '100%', padding: '10px 12px 10px 36px', border: '1px solid #ddd', borderRadius: 8, fontSize: 14, outline: 'none', boxSizing: 'border-box' },
  select: { padding: '10px 16px', border: '1px solid #ddd', borderRadius: 8, fontSize: 14, outline: 'none', backgroundColor: '#fff', cursor: 'pointer' },
  error: { backgroundColor: '#fff3e0', color: '#e65100', padding: '10px 16px', borderRadius: 8, marginBottom: 20, fontSize: 14 },
  sectionHeading: { fontSize: 18, fontWeight: 600, color: '#1a237e' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 14 },
  th: { padding: '12px 16px', fontWeight: 600, color: '#1a237e', whiteSpace: 'nowrap', textAlign: 'left' },
  thead: { borderBottom: '2px solid #e0e0e0' },
  badge: { padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, display: 'inline-block', textTransform: 'capitalize' },
  expandedRow: { backgroundColor: '#f9f9fb' },
  expandedCell: { padding: '20px 16px' },
  expandedGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 },
  expandedCard: { backgroundColor: '#ffffff', borderRadius: 8, padding: 16, border: '1px solid #eee' },
  expandedCardTitle: { display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, fontWeight: 600, color: '#1a237e', marginBottom: 12 },
  expandedLabel: { fontSize: 12, fontWeight: 600, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 },
  expandedValue: { fontSize: 14, color: '#333', marginBottom: 12 },
  signalList: { listStyle: 'disc', paddingLeft: 20, margin: 0 },
  signalItem: { fontSize: 13, color: '#555', marginBottom: 4 },
  confidenceBar: { width: '100%', height: 8, backgroundColor: '#e0e0e0', borderRadius: 4, overflow: 'hidden', marginTop: 4, marginBottom: 8 },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, marginBottom: 24 },
  statLabel: { fontSize: 13, color: '#666', marginBottom: 2 },
  statValue: { fontSize: 20, fontWeight: 700, color: '#1a237e' },
};

function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [segmentSummary, setSegmentSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [segmentFilter, setSegmentFilter] = useState('all');
  const [intentFilter, setIntentFilter] = useState('all');
  const [expandedId, setExpandedId] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [recLoading, setRecLoading] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [custRes, segRes] = await Promise.allSettled([
          customerAPI.list(),
          customerAPI.getSegmentSummary(),
        ]);
        const custData = custRes.status === 'fulfilled' ? custRes.value.data : null;
        const custList = Array.isArray(custData) ? custData : custData?.customers || defaultCustomers;
        setCustomers(custList.map((c) => {
          const intentScore = c.purchase_intent_score || 0;
          return {
            ...c,
            name: c.name || ((c.first_name || '') + ' ' + (c.last_name || '')).trim() || 'Unknown',
            segment: c.customer_segment || c.vehicle_segment || c.segment || 'mid_range',
            intent_level: c.intent_level || (intentScore > 65 ? 'High' : intentScore >= 30 ? 'Medium' : 'Low'),
            language: c.language_preference || c.language || 'en',
          };
        }));
        const segData = segRes.status === 'fulfilled' ? segRes.value.data : null;
        if (segData && segData.segments && !Array.isArray(segData)) {
          const mapped = Object.entries(segData.segments).map(([seg, count]) => ({
            segment: seg,
            count,
            avg_intent_score: 0.5,
            top_channels: Object.entries(segData.preferred_channels || {}).sort((a, b) => b[1] - a[1]).slice(0, 2).map(([ch]) => ch),
          }));
          setSegmentSummary(mapped.length > 0 ? mapped : defaultSegmentSummary);
        } else {
          setSegmentSummary(Array.isArray(segData) ? segData : defaultSegmentSummary);
        }
        if (custRes.status === 'rejected') {
          setError('Could not load live data. Showing demo data.');
        }
      } catch {
        setCustomers(defaultCustomers);
        setSegmentSummary(defaultSegmentSummary);
        setError('Could not load live data. Showing demo data.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleRowClick = async (customer) => {
    const id = customer.customer_id;
    if (expandedId === id) {
      setExpandedId(null);
      setRecommendation(null);
      return;
    }
    setExpandedId(id);
    setRecommendation(null);
    setRecLoading(true);
    try {
      const res = await customerAPI.getRecommendation(id);
      setRecommendation(res.data || defaultRecommendation);
    } catch {
      setRecommendation(defaultRecommendation);
    } finally {
      setRecLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  const filtered = customers.filter((c) => {
    const matchSearch = (c.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (c.city || '').toLowerCase().includes(search.toLowerCase()) ||
      (c.state || '').toLowerCase().includes(search.toLowerCase());
    const matchSegment = segmentFilter === 'all' || c.segment === segmentFilter;
    const matchIntent = intentFilter === 'all' || c.intent_level === intentFilter;
    return matchSearch && matchSegment && matchIntent;
  });

  const formatSegment = (seg) => {
    if (!seg) return '';
    return seg.split('_').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <Users size={28} color="#1a237e" />
          <h1 style={styles.title}>Customers</h1>
        </div>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.statsGrid}>
        {segmentSummary.map((seg) => (
          <div key={seg.segment} style={{ ...styles.card, borderLeft: `4px solid ${(SEGMENT_COLORS[seg.segment] || {}).color || '#333'}` }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 }}>
              {formatSegment(seg.segment)} Segment
            </div>
            <div style={styles.statValue}>{seg.count} customers</div>
            <div style={styles.statLabel}>Avg Intent: {(seg.avg_intent_score * 100).toFixed(0)}%</div>
            <div style={styles.statLabel}>Top Channels: {(seg.top_channels || []).join(', ')}</div>
          </div>
        ))}
      </div>

      <div style={{ ...styles.card, marginBottom: 24 }}>
        <div style={styles.filterRow}>
          <div style={styles.searchWrap}>
            <Search size={16} color="#999" style={styles.searchIcon} />
            <input
              type="text"
              placeholder="Search by name, city, or state..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={styles.searchInput}
            />
          </div>
          <select value={segmentFilter} onChange={(e) => setSegmentFilter(e.target.value)} style={styles.select}>
            <option value="all">All Segments</option>
            {[...new Set(customers.map(c => c.segment))].filter(Boolean).map(s => (
              <option key={s} value={s}>{formatSegment(s)}</option>
            ))}
          </select>
          <select value={intentFilter} onChange={(e) => setIntentFilter(e.target.value)} style={styles.select}>
            <option value="all">All Intent Levels</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>
      </div>

      <div style={styles.card}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <h2 style={styles.sectionHeading}>{filtered.length} Customer{filtered.length !== 1 ? 's' : ''}</h2>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={styles.table}>
            <thead>
              <tr style={styles.thead}>
                {['ID', 'Name', 'City', 'State', 'Segment', 'Intent', 'Channel', 'Language', ''].map((h) => (
                  <th key={h} style={styles.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} style={{ padding: 40, textAlign: 'center', color: '#999' }}>
                    No customers found matching your criteria.
                  </td>
                </tr>
              ) : (
                filtered.map((c, idx) => {
                  const isExpanded = expandedId === c.customer_id;
                  const intentBadge = INTENT_COLORS[c.intent_level] || INTENT_COLORS.Medium;
                  const segBadge = SEGMENT_COLORS[c.segment] || SEGMENT_COLORS.mid_range;
                  return (
                    <React.Fragment key={c.customer_id}>
                      <tr
                        onClick={() => handleRowClick(c)}
                        style={{
                          backgroundColor: isExpanded ? '#e3f2fd' : idx % 2 === 0 ? '#fafafa' : '#ffffff',
                          cursor: 'pointer',
                          borderBottom: '1px solid #eee',
                          transition: 'background-color 0.15s',
                        }}
                        onMouseEnter={(e) => { if (!isExpanded) e.currentTarget.style.backgroundColor = '#e3f2fd'; }}
                        onMouseLeave={(e) => { if (!isExpanded) e.currentTarget.style.backgroundColor = idx % 2 === 0 ? '#fafafa' : '#ffffff'; }}
                      >
                        <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontSize: 13 }}>
                          {(c.customer_id || '').substring(0, 8)}
                        </td>
                        <td style={{ padding: '12px 16px', fontWeight: 500 }}>{c.name}</td>
                        <td style={{ padding: '12px 16px' }}>{c.city}</td>
                        <td style={{ padding: '12px 16px' }}>{c.state}</td>
                        <td style={{ padding: '12px 16px' }}>
                          <span style={{ ...styles.badge, ...segBadge }}>{formatSegment(c.segment)}</span>
                        </td>
                        <td style={{ padding: '12px 16px' }}>
                          <span style={{ ...styles.badge, ...intentBadge }}>{c.intent_level}</span>
                        </td>
                        <td style={{ padding: '12px 16px', textTransform: 'capitalize' }}>{c.preferred_channel}</td>
                        <td style={{ padding: '12px 16px' }}>{c.language}</td>
                        <td style={{ padding: '12px 16px' }}>
                          {isExpanded ? <ChevronUp size={16} color="#666" /> : <ChevronDown size={16} color="#666" />}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr style={styles.expandedRow}>
                          <td colSpan={9} style={styles.expandedCell}>
                            <div style={styles.expandedGrid}>
                              <div style={styles.expandedCard}>
                                <div style={styles.expandedCardTitle}>
                                  <User size={16} color="#1a237e" />
                                  Customer Persona
                                </div>
                                <div style={{ fontSize: 14, color: '#333', lineHeight: 1.6 }}>
                                  {c.persona || 'No persona data available.'}
                                </div>
                              </div>

                              <div style={styles.expandedCard}>
                                <div style={styles.expandedCardTitle}>
                                  <Brain size={16} color="#1a237e" />
                                  Buying Intent
                                </div>
                                <div style={styles.expandedLabel}>Intent Score</div>
                                <div style={{ fontSize: 20, fontWeight: 700, color: '#1a237e', marginBottom: 4 }}>
                                  {c.buying_intent ? (c.buying_intent.score * 100).toFixed(0) + '%' : 'N/A'}
                                </div>
                                <div style={styles.confidenceBar}>
                                  <div style={{ height: '100%', width: `${c.buying_intent ? c.buying_intent.score * 100 : 0}%`, backgroundColor: '#0288d1', borderRadius: 4 }} />
                                </div>
                                <div style={styles.expandedLabel}>Signals</div>
                                <ul style={styles.signalList}>
                                  {(c.buying_intent?.signals || []).map((s, i) => (
                                    <li key={i} style={styles.signalItem}>{s}</li>
                                  ))}
                                </ul>
                              </div>

                              <div style={styles.expandedCard}>
                                <div style={styles.expandedCardTitle}>
                                  <Car size={16} color="#1a237e" />
                                  Vehicle Ownership
                                </div>
                                <div style={styles.expandedLabel}>Current Vehicle</div>
                                <div style={styles.expandedValue}>
                                  {c.vehicle_ownership?.current || 'None'}
                                </div>
                                <div style={styles.expandedLabel}>Previous Vehicles</div>
                                <div style={{ fontSize: 14, color: '#333' }}>
                                  {(c.vehicle_ownership?.history || []).length > 0
                                    ? c.vehicle_ownership.history.join(', ')
                                    : 'No history'}
                                </div>
                              </div>

                              <div style={styles.expandedCard}>
                                <div style={styles.expandedCardTitle}>
                                  <Sparkles size={16} color="#1a237e" />
                                  AI Recommendation
                                </div>
                                {recLoading ? (
                                  <div style={{ fontSize: 13, color: '#999' }}>Loading recommendation...</div>
                                ) : recommendation ? (
                                  <div>
                                    <div style={styles.expandedLabel}>Recommended Vehicle</div>
                                    <div style={{ fontSize: 16, fontWeight: 700, color: '#1a237e', marginBottom: 8 }}>
                                      {recommendation.recommended_vehicle}
                                    </div>
                                    <div style={styles.expandedLabel}>Confidence</div>
                                    <div style={{ fontSize: 14, fontWeight: 600, color: '#2e7d32', marginBottom: 4 }}>
                                      {recommendation.confidence}%
                                    </div>
                                    <div style={styles.confidenceBar}>
                                      <div style={{ height: '100%', width: `${recommendation.confidence}%`, backgroundColor: '#2e7d32', borderRadius: 4 }} />
                                    </div>
                                    <div style={styles.expandedLabel}>Reasoning</div>
                                    <div style={{ fontSize: 13, color: '#555', marginBottom: 8, lineHeight: 1.5 }}>
                                      {recommendation.reasoning}
                                    </div>
                                    <div style={styles.expandedLabel}>Alternative</div>
                                    <div style={{ fontSize: 14, color: '#333' }}>
                                      {recommendation.alternative}
                                    </div>
                                  </div>
                                ) : (
                                  <div style={{ fontSize: 13, color: '#999' }}>No recommendation available.</div>
                                )}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
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

export default CustomersPage;
