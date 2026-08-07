import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Send, Loader2 } from 'lucide-react';
import { campaignAPI, vehicleAPI } from '../../services/api';

const OBJECTIVES = [
  'Product Launch', 'Awareness', 'Engagement', 'Conversion',
  'Retention', 'Upsell', 'Re-engagement', 'Festive Campaign',
];

const SEGMENTS = [
  { value: 'mid_range', label: 'Mid Range' },
  { value: 'premium', label: 'Premium' },
  { value: 'luxury', label: 'Luxury' },
  { value: 'all', label: 'All' },
];

const FESTIVALS = [
  'None', 'Diwali', 'Holi', 'Navratri', 'Dussehra', 'Christmas',
  'Independence Day', 'Onam', 'Ganesh Chaturthi', 'Makar Sankranti', 'Ugadi',
];

const CHANNELS = [
  { value: 'email', label: 'Email' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'sms', label: 'SMS' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'push', label: 'Push Notification' },
  { value: 'youtube', label: 'YouTube' },
];

const LANGUAGES = [
  { value: 'english', label: 'English' },
  { value: 'hindi', label: 'Hindi' },
];

const defaultVehicles = [
  { vehicle_id: 'v1', name: 'Nexon EV', category: 'EV' },
  { vehicle_id: 'v2', name: 'Curvv EV', category: 'EV' },
  { vehicle_id: 'v3', name: 'Safari', category: 'SUV' },
  { vehicle_id: 'v4', name: 'Punch', category: 'SUV' },
  { vehicle_id: 'v5', name: 'Tiago EV', category: 'EV' },
  { vehicle_id: 'v6', name: 'Harrier', category: 'SUV' },
  { vehicle_id: 'v7', name: 'Altroz', category: 'Hatchback' },
  { vehicle_id: 'v8', name: 'Tigor EV', category: 'EV' },
];

function CreateCampaign() {
  const navigate = useNavigate();
  const [vehicles, setVehicles] = useState([]);
  const [nlInput, setNlInput] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parseResult, setParseResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [form, setForm] = useState({
    name: '',
    description: '',
    objective: '',
    vehicle_id: '',
    target_segment: 'all',
    target_cities: '',
    target_states: '',
    budget: '',
    start_date: '',
    end_date: '',
    festival_context: 'None',
    channels: [],
    languages: ['english'],
  });

  useEffect(() => {
    vehicleAPI.list()
      .then((res) => {
        const d = res.data;
        setVehicles(Array.isArray(d) ? d : d?.vehicles || defaultVehicles);
      })
      .catch(() => setVehicles(defaultVehicles));
  }, []);

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const toggleArrayField = (field, value) => {
    setForm((prev) => {
      const arr = prev[field];
      return {
        ...prev,
        [field]: arr.includes(value) ? arr.filter((v) => v !== value) : [...arr, value],
      };
    });
  };

  const handleParse = async () => {
    if (!nlInput.trim()) return;
    setParsing(true);
    setParseResult(null);
    try {
      const res = await campaignAPI.parseRequest(nlInput);
      const parsed = res.data;
      setParseResult(parsed);
      setForm((prev) => ({
        ...prev,
        name: parsed.campaign_name || parsed.name || prev.name,
        description: parsed.description || prev.description,
        objective: parsed.objective || prev.objective,
        vehicle_id: parsed.vehicle_id || prev.vehicle_id,
        target_segment: parsed.target_segment || prev.target_segment,
        target_cities: Array.isArray(parsed.target_cities) ? parsed.target_cities.join(', ') : parsed.target_cities || prev.target_cities,
        target_states: Array.isArray(parsed.target_states) ? parsed.target_states.join(', ') : parsed.target_states || prev.target_states,
        budget: parsed.budget || prev.budget,
        start_date: parsed.start_date || prev.start_date,
        end_date: parsed.end_date || prev.end_date,
        festival_context: parsed.festival_context || prev.festival_context,
        channels: parsed.channels || prev.channels,
        languages: parsed.languages || prev.languages,
      }));
    } catch {
      setError('AI parsing failed. Please fill the form manually.');
    } finally {
      setParsing(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.objective) {
      setError('Campaign name and objective are required.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const payload = {
        ...form,
        budget: form.budget ? Number(form.budget) : 0,
        target_cities: form.target_cities ? form.target_cities.split(',').map((s) => s.trim()).filter(Boolean) : [],
        target_states: form.target_states ? form.target_states.split(',').map((s) => s.trim()).filter(Boolean) : [],
        festival_context: form.festival_context === 'None' ? null : form.festival_context,
      };
      await campaignAPI.create(payload);
      navigate('/campaigns');
    } catch {
      setError('Failed to create campaign. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const card = {
    backgroundColor: '#ffffff',
    borderRadius: 10,
    padding: 24,
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
    marginBottom: 24,
  };

  const sectionTitle = {
    fontSize: 16,
    fontWeight: 600,
    color: '#1a237e',
    marginBottom: 16,
    paddingBottom: 8,
    borderBottom: '1px solid #eee',
  };

  const labelStyle = {
    display: 'block',
    fontSize: 13,
    fontWeight: 600,
    color: '#333',
    marginBottom: 6,
  };

  const inputStyle = {
    width: '100%',
    padding: '10px 12px',
    border: '1px solid #ddd',
    borderRadius: 8,
    fontSize: 14,
    outline: 'none',
    boxSizing: 'border-box',
  };

  const selectStyle = {
    ...inputStyle,
    backgroundColor: '#fff',
    cursor: 'pointer',
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, color: '#1a237e', marginBottom: 24 }}>
        Create New Campaign
      </h1>

      {error && (
        <div style={{ backgroundColor: '#ffebee', color: '#c62828', padding: '10px 16px', borderRadius: 8, marginBottom: 20, fontSize: 14 }}>
          {error}
        </div>
      )}

      <div style={card}>
        <div style={sectionTitle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Sparkles size={18} color="#1a237e" />
            AI-Powered Campaign Builder (Optional)
          </div>
        </div>
        <textarea
          value={nlInput}
          onChange={(e) => setNlInput(e.target.value)}
          placeholder="Launch a Diwali campaign for Nexon EV customers in Bangalore who purchased within the last 3 years"
          rows={4}
          style={{ ...inputStyle, resize: 'vertical', marginBottom: 12 }}
        />
        <button
          onClick={handleParse}
          disabled={parsing || !nlInput.trim()}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '10px 20px',
            backgroundColor: parsing ? '#999' : '#1a237e',
            color: '#ffffff',
            border: 'none',
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 600,
            cursor: parsing ? 'not-allowed' : 'pointer',
          }}
        >
          {parsing ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Sparkles size={16} />}
          {parsing ? 'Parsing...' : 'Parse with AI'}
        </button>
        {parseResult && (
          <div style={{
            marginTop: 16,
            padding: 16,
            backgroundColor: '#e8f5e9',
            borderRadius: 8,
            fontSize: 13,
            color: '#2e7d32',
          }}>
            AI parsed your request successfully. The form below has been auto-filled.
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit}>
        <div style={card}>
          <div style={sectionTitle}>Basic Information</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Campaign Name</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder="Enter campaign name"
                style={inputStyle}
              />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Description</label>
              <textarea
                value={form.description}
                onChange={(e) => updateField('description', e.target.value)}
                placeholder="Campaign description"
                rows={3}
                style={{ ...inputStyle, resize: 'vertical' }}
              />
            </div>
            <div>
              <label style={labelStyle}>Objective</label>
              <select
                value={form.objective}
                onChange={(e) => updateField('objective', e.target.value)}
                style={selectStyle}
              >
                <option value="">Select objective</option>
                {OBJECTIVES.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Vehicle</label>
              <select
                value={form.vehicle_id}
                onChange={(e) => updateField('vehicle_id', e.target.value)}
                style={selectStyle}
              >
                <option value="">Select vehicle</option>
                {vehicles.map((v) => (
                  <option key={v.vehicle_id} value={v.vehicle_id}>
                    {v.name} - {v.category}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div style={card}>
          <div style={sectionTitle}>Targeting</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={labelStyle}>Target Segment</label>
              <select
                value={form.target_segment}
                onChange={(e) => updateField('target_segment', e.target.value)}
                style={selectStyle}
              >
                {SEGMENTS.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Festival Context</label>
              <select
                value={form.festival_context}
                onChange={(e) => updateField('festival_context', e.target.value)}
                style={selectStyle}
              >
                {FESTIVALS.map((f) => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Target Cities (comma separated)</label>
              <input
                type="text"
                value={form.target_cities}
                onChange={(e) => updateField('target_cities', e.target.value)}
                placeholder="Mumbai, Bangalore, Delhi"
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>Target States (comma separated)</label>
              <input
                type="text"
                value={form.target_states}
                onChange={(e) => updateField('target_states', e.target.value)}
                placeholder="Maharashtra, Karnataka, Delhi"
                style={inputStyle}
              />
            </div>
          </div>
        </div>

        <div style={card}>
          <div style={sectionTitle}>Budget & Schedule</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={labelStyle}>Budget</label>
              <div style={{ position: 'relative' }}>
                <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#666', fontSize: 14, fontWeight: 600 }}>
                  {'\u20B9'}
                </span>
                <input
                  type="number"
                  value={form.budget}
                  onChange={(e) => updateField('budget', e.target.value)}
                  placeholder="500000"
                  style={{ ...inputStyle, paddingLeft: 28 }}
                />
              </div>
            </div>
            <div />
            <div>
              <label style={labelStyle}>Start Date</label>
              <input
                type="date"
                value={form.start_date}
                onChange={(e) => updateField('start_date', e.target.value)}
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>End Date</label>
              <input
                type="date"
                value={form.end_date}
                onChange={(e) => updateField('end_date', e.target.value)}
                style={inputStyle}
              />
            </div>
          </div>
        </div>

        <div style={card}>
          <div style={sectionTitle}>Channels</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
            {CHANNELS.map((ch) => {
              const checked = form.channels.includes(ch.value);
              return (
                <label
                  key={ch.value}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    padding: '8px 16px',
                    borderRadius: 8,
                    border: checked ? '2px solid #1a237e' : '2px solid #ddd',
                    backgroundColor: checked ? '#e8eaf6' : '#fff',
                    cursor: 'pointer',
                    fontSize: 14,
                    fontWeight: 500,
                    transition: 'all 0.15s',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleArrayField('channels', ch.value)}
                    style={{ display: 'none' }}
                  />
                  <span style={{
                    width: 18,
                    height: 18,
                    borderRadius: 4,
                    border: checked ? '2px solid #1a237e' : '2px solid #bbb',
                    backgroundColor: checked ? '#1a237e' : '#fff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: 12,
                    fontWeight: 700,
                    flexShrink: 0,
                  }}>
                    {checked ? '\u2713' : ''}
                  </span>
                  {ch.label}
                </label>
              );
            })}
          </div>
        </div>

        <div style={card}>
          <div style={sectionTitle}>Languages</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
            {LANGUAGES.map((lang) => {
              const checked = form.languages.includes(lang.value);
              return (
                <label
                  key={lang.value}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    padding: '8px 16px',
                    borderRadius: 8,
                    border: checked ? '2px solid #1a237e' : '2px solid #ddd',
                    backgroundColor: checked ? '#e8eaf6' : '#fff',
                    cursor: 'pointer',
                    fontSize: 14,
                    fontWeight: 500,
                    transition: 'all 0.15s',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleArrayField('languages', lang.value)}
                    style={{ display: 'none' }}
                  />
                  <span style={{
                    width: 18,
                    height: 18,
                    borderRadius: 4,
                    border: checked ? '2px solid #1a237e' : '2px solid #bbb',
                    backgroundColor: checked ? '#1a237e' : '#fff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: 12,
                    fontWeight: 700,
                    flexShrink: 0,
                  }}>
                    {checked ? '\u2713' : ''}
                  </span>
                  {lang.label}
                </label>
              );
            })}
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={() => navigate('/campaigns')}
            style={{
              padding: '12px 24px',
              backgroundColor: '#fff',
              color: '#333',
              border: '1px solid #ddd',
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '12px 28px',
              backgroundColor: submitting ? '#999' : '#1a237e',
              color: '#ffffff',
              border: 'none',
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 600,
              cursor: submitting ? 'not-allowed' : 'pointer',
            }}
          >
            {submitting ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={16} />}
            {submitting ? 'Creating...' : 'Create Campaign'}
          </button>
        </div>
      </form>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export default CreateCampaign;
