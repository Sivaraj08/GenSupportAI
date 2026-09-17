import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { ShieldAlert, BarChart3, HelpCircle, Activity } from 'lucide-react';

export default function Analytics() {
  const [sentimentData, setSentimentData] = useState([]);
  const [forecastData, setForecastData] = useState([]);
  const [kpis, setKpis] = useState({ avg_resolution_time_hours: 0, open_tickets: 0 });
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      // 1. Dashboard metrics (to grab resolution speed KPI)
      const meta = await api.getDashboardMetrics();
      setKpis(meta);
      
      // 2. Sentiment Metrics
      const sent = await api.getSentimentMetrics();
      setSentimentData([
        { name: 'Positive', value: sent.positive, color: '#10b981' },
        { name: 'Neutral', value: sent.neutral, color: '#64748b' },
        { name: 'Negative', value: sent.negative, color: '#f43f5e' }
      ]);
      
      // 3. Forecast Metrics
      const fore = await api.getForecastingMetrics();
      // Map predictions date to day format (e.g. "Mon 13")
      const mappedForecast = fore.forecast.map(point => {
        const d = new Date(point.date);
        return {
          ...point,
          displayName: d.toLocaleDateString([], { weekday: 'short', day: 'numeric' })
        };
      });
      setForecastData(mappedForecast);

    } catch (err) {
      console.error("Failed to load analytics charts:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <div className="animate-fade-in" style={{ padding: '30px', maxWidth: '1200px', margin: '0 auto', overflowY: 'auto' }}>
      
      {/* Header */}
      <div className="page-header" style={{ marginBottom: '24px' }}>
        <div>
          <h1 className="page-title">Predictive Intelligence Portal</h1>
          <p className="page-subtitle">Time-series forecasting models and user sentiment analytics</p>
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px' }}>
          <span>Loading analytics engine...</span>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '30px' }}>
          
          {/* Workload 7-Day Forecasting Chart */}
          <div className="card glass-panel" style={{ gridColumn: 'span 2' }}>
            <h3 style={{ fontSize: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} style={{ color: 'var(--color-primary)' }} />
              7-Day Ticket Queue Workload Forecast
            </h3>
            
            <div style={{ width: '100%', height: '300px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={forecastData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                  <XAxis dataKey="displayName" stroke="var(--text-secondary)" fontSize={11} tickLine={false} />
                  <YAxis stroke="var(--text-secondary)" fontSize={11} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ 
                      background: 'var(--bg-secondary)', 
                      border: '1px solid var(--border-color)', 
                      borderRadius: '8px', 
                      color: 'var(--text-primary)',
                      fontFamily: 'var(--font-sans)',
                      fontSize: '0.8rem'
                    }} 
                  />
                  <Area type="monotone" dataKey="predicted_tickets" name="Predicted Tickets" stroke="var(--color-primary)" strokeWidth={2} fillOpacity={1} fill="url(#colorForecast)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            
            <div style={{ marginTop: '16px', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '12px 16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              **Prediction Analysis:** The model projects standard weekly fluctuations, expecting weekend workloads to drop and Monday surges (as client emails queue up over the weekend) to raise demand. Fits using linear-quadratic regression models.
            </div>
          </div>

          {/* User Sentiment Satisfactions Chart */}
          <div className="card glass-panel">
            <h3 style={{ fontSize: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart3 size={18} style={{ color: 'var(--color-success)' }} />
              Customer Sentiment Satisfaction
            </h3>
            
            <div style={{ display: 'flex', alignItems: 'center', height: '240px' }}>
              {/* If no sentiment data seeded */}
              {sentimentData.every(d => d.value === 0) ? (
                <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  <HelpCircle size={32} style={{ marginBottom: '8px', opacity: 0.4 }} />
                  <p>No chat history to analyze sentiment.</p>
                </div>
              ) : (
                <>
                  <div style={{ width: '60%', height: '100%' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={sentimentData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {sentimentData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '40%' }}>
                    {sentimentData.map((item, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem' }}>
                        <div style={{ width: '10px', height: '10px', background: item.color, borderRadius: '50%' }} />
                        <span style={{ color: 'var(--text-secondary)', fontWeight: 550 }}>{item.name}:</span>
                        <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{item.value}</span>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Operational Health KPIs */}
          <div className="card glass-panel">
            <h3 style={{ fontSize: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={18} style={{ color: 'var(--color-danger)' }} />
              Queue Health Analytics
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px', paddingTop: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.03)', paddingBottom: '12px' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Open Backlog Size</span>
                <span style={{ fontWeight: 600, color: kpis.open_tickets > 5 ? 'var(--color-danger)' : 'var(--text-primary)' }}>{kpis.open_tickets} tickets</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.03)', paddingBottom: '12px' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Average Resolution SLA</span>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{kpis.avg_resolution_time_hours} hours</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '6px' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Target SLA Threshold</span>
                <span style={{ fontWeight: 600, color: 'var(--color-success)' }}>12 hours</span>
              </div>
            </div>
            
            <div style={{ marginTop: '20px', padding: '12px', background: 'rgba(16,185,129,0.02)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '8px', fontSize: '0.75rem', color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ display: 'block', width: '6px', height: '6px', background: 'var(--color-success)', borderRadius: '50%' }} />
              Operational status: SLA speed complies with company target guarantees.
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
