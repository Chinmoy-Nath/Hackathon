import React, { useState, useEffect } from 'react';
import { Car, Search, Fuel, Zap, Leaf } from 'lucide-react';
import { vehicleAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const defaultVehicles = [
  { vehicle_id: 'v1', name: 'Tata Punch', category: 'Petrol', segment: 'Mid Range', price_min: 600000, price_max: 1000000, features: ['Advanced Safety', 'Touchscreen Infotainment', 'AMT Transmission', 'Cruise Control'], target_audience: 'Young urban professionals and first-time buyers' },
  { vehicle_id: 'v2', name: 'Tata Tiago', category: 'Petrol', segment: 'Mid Range', price_min: 550000, price_max: 850000, features: ['Harman Audio', 'Digital Instrument Cluster', 'Dual Airbags', 'ABS with EBD'], target_audience: 'Budget-conscious families and daily commuters' },
  { vehicle_id: 'v3', name: 'Tata Altroz', category: 'Petrol', segment: 'Mid Range', price_min: 670000, price_max: 1100000, features: ['5-Star Safety Rating', 'iRA Connected Tech', 'Ventilated Seats', 'Turbo Engine Option'], target_audience: 'Safety-conscious buyers seeking premium hatchback' },
  { vehicle_id: 'v4', name: 'Tata Nexon', category: 'Petrol', segment: 'Premium', price_min: 850000, price_max: 1500000, features: ['Panoramic Sunroof', 'Ventilated Seats', '5-Star NCAP', 'Electric Sunblind'], target_audience: 'Tech-savvy professionals seeking feature-rich compact SUV' },
  { vehicle_id: 'v5', name: 'Tata Harrier', category: 'Petrol', segment: 'Premium', price_min: 1500000, price_max: 2500000, features: ['ADAS Suite', 'Panoramic Sunroof', 'JBL Audio', '170 PS Engine'], target_audience: 'Premium SUV enthusiasts wanting muscular design' },
  { vehicle_id: 'v6', name: 'Tata Safari', category: 'Petrol', segment: 'Luxury', price_min: 1600000, price_max: 2700000, features: ['Captain Seats', 'ADAS', 'Air Purifier', '7-Seater Configuration'], target_audience: 'Large families and those seeking commanding road presence' },
  { vehicle_id: 'v7', name: 'Tata Tiago EV', category: 'EV', segment: 'Mid Range', price_min: 800000, price_max: 1200000, features: ['315 km Range', 'Fast Charging', 'Ziptron Technology', 'Regenerative Braking'], target_audience: 'Eco-conscious urban commuters on a budget' },
  { vehicle_id: 'v8', name: 'Tata Nexon EV', category: 'EV', segment: 'Premium', price_min: 1500000, price_max: 2000000, features: ['465 km Range', 'Fast Charging', 'Connected Car Tech', 'Multi-mode Regen'], target_audience: 'Premium EV adopters seeking SUV form factor' },
  { vehicle_id: 'v9', name: 'Tata Curvv EV', category: 'EV', segment: 'Premium', price_min: 1750000, price_max: 2200000, features: ['Coupe SUV Design', '500 km Range', 'Level 2 ADAS', 'Arcade.ev Platform'], target_audience: 'Style-conscious professionals wanting futuristic EV' },
  { vehicle_id: 'v10', name: 'Tata Punch EV', category: 'EV', segment: 'Mid Range', price_min: 1000000, price_max: 1400000, features: ['421 km Range', 'Fast Charging', 'Connected Car', 'Multi-drive Modes'], target_audience: 'First-time EV buyers wanting compact crossover' },
  { vehicle_id: 'v11', name: 'Tata Curvv', category: 'Petrol', segment: 'Premium', price_min: 1000000, price_max: 1900000, features: ['Coupe SUV Design', 'Panoramic Sunroof', 'ADAS', 'Turbo Engine'], target_audience: 'Trend-setting buyers wanting unique design language' },
  { vehicle_id: 'v12', name: 'Tata Nexon iCNG', category: 'Hybrid', segment: 'Mid Range', price_min: 900000, price_max: 1300000, features: ['Twin-cylinder CNG', 'iCNG Technology', 'Seamless Switching', 'Boot Space Retained'], target_audience: 'Cost-conscious buyers seeking dual-fuel flexibility' },
];

const CATEGORY_COLORS = {
  Petrol: '#f57f17',
  EV: '#2e7d32',
  Hybrid: '#7b1fa2',
};

const CATEGORY_ICONS = {
  Petrol: Fuel,
  EV: Zap,
  Hybrid: Leaf,
};

const SEGMENT_COLORS = {
  'Mid Range': { backgroundColor: '#e3f2fd', color: '#0288d1' },
  'Premium': { backgroundColor: '#f3e5f5', color: '#7b1fa2' },
  'Luxury': { backgroundColor: '#fff8e1', color: '#b8860b' },
};

function formatPrice(value) {
  if (!value) return '';
  const lakhs = value / 100000;
  return lakhs.toFixed(1).replace(/\.0$/, '');
}

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
  grid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 },
  vehicleCard: { backgroundColor: '#ffffff', borderRadius: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.06)', overflow: 'hidden', display: 'flex', flexDirection: 'column', transition: 'transform 0.2s, box-shadow 0.2s' },
  cardHeader: { padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' },
  cardBody: { padding: '0 20px 20px', flex: 1, display: 'flex', flexDirection: 'column' },
  vehicleName: { fontSize: 18, fontWeight: 700, color: '#1a237e', marginBottom: 8 },
  badgeRow: { display: 'flex', gap: 8, marginBottom: 12 },
  badge: { padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, display: 'inline-block' },
  priceRange: { fontSize: 16, fontWeight: 700, color: '#333', marginBottom: 12 },
  featureList: { listStyle: 'none', padding: 0, margin: '0 0 12px 0' },
  featureItem: { fontSize: 13, color: '#555', padding: '3px 0', display: 'flex', alignItems: 'center', gap: 8 },
  featureDot: { width: 5, height: 5, borderRadius: '50%', backgroundColor: '#0288d1', flexShrink: 0 },
  targetAudience: { fontSize: 12, color: '#888', marginTop: 'auto', paddingTop: 12, borderTop: '1px solid #eee', lineHeight: 1.5 },
  targetLabel: { fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, color: '#aaa', marginBottom: 4 },
  emptyState: { textAlign: 'center', padding: 60, color: '#999', fontSize: 16 },
};

function VehiclesPage() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [segmentFilter, setSegmentFilter] = useState('all');

  useEffect(() => {
    vehicleAPI.list()
      .then((res) => {
        const d = res.data;
        setVehicles(Array.isArray(d) ? d : d?.vehicles || defaultVehicles);
      })
      .catch(() => {
        setVehicles(defaultVehicles);
        setError('Could not load live data. Showing demo data.');
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  const filtered = vehicles.filter((v) => {
    const matchSearch = (v.name || '').toLowerCase().includes(search.toLowerCase());
    const matchCategory = categoryFilter === 'all' || v.category === categoryFilter;
    const matchSegment = segmentFilter === 'all' || v.segment === segmentFilter;
    return matchSearch && matchCategory && matchSegment;
  });

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <Car size={28} color="#1a237e" />
          <h1 style={styles.title}>Vehicle Catalog</h1>
        </div>
        <div style={{ fontSize: 14, color: '#666' }}>{filtered.length} vehicle{filtered.length !== 1 ? 's' : ''}</div>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      <div style={{ ...styles.card, marginBottom: 24 }}>
        <div style={styles.filterRow}>
          <div style={styles.searchWrap}>
            <Search size={16} color="#999" style={styles.searchIcon} />
            <input
              type="text"
              placeholder="Search vehicles..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={styles.searchInput}
            />
          </div>
          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} style={styles.select}>
            <option value="all">All Categories</option>
            <option value="Petrol">Petrol</option>
            <option value="EV">EV</option>
            <option value="Hybrid">Hybrid</option>
          </select>
          <select value={segmentFilter} onChange={(e) => setSegmentFilter(e.target.value)} style={styles.select}>
            <option value="all">All Segments</option>
            <option value="Mid Range">Mid Range</option>
            <option value="Premium">Premium</option>
            <option value="Luxury">Luxury</option>
          </select>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div style={styles.emptyState}>No vehicles found matching your criteria.</div>
      ) : (
        <div style={styles.grid}>
          {filtered.map((v) => {
            const catColor = CATEGORY_COLORS[v.category] || '#666';
            const CatIcon = CATEGORY_ICONS[v.category] || Fuel;
            const segBadge = SEGMENT_COLORS[v.segment] || SEGMENT_COLORS['Mid Range'];
            return (
              <div
                key={v.vehicle_id || v.name}
                style={styles.vehicleCard}
                onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)'; }}
              >
                <div style={{ ...styles.cardHeader, borderBottom: `3px solid ${catColor}` }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <CatIcon size={20} color={catColor} />
                    <span style={{ fontSize: 13, fontWeight: 600, color: catColor, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                      {v.category}
                    </span>
                  </div>
                </div>
                <div style={styles.cardBody}>
                  <div style={styles.vehicleName}>{v.name}</div>
                  <div style={styles.badgeRow}>
                    <span style={{ ...styles.badge, backgroundColor: `${catColor}20`, color: catColor }}>
                      {v.category}
                    </span>
                    <span style={{ ...styles.badge, ...segBadge }}>
                      {v.segment}
                    </span>
                  </div>
                  <div style={styles.priceRange}>
                    {'\u20B9'}{formatPrice(v.price_min)} - {formatPrice(v.price_max)} Lakhs
                  </div>
                  <ul style={styles.featureList}>
                    {(v.features || []).map((f, i) => (
                      <li key={i} style={styles.featureItem}>
                        <span style={styles.featureDot} />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <div style={styles.targetAudience}>
                    <div style={styles.targetLabel}>Target Audience</div>
                    {v.target_audience}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default VehiclesPage;
