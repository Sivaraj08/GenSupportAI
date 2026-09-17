import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { MessageSquare, Ticket, Clock, Users, ArrowRight, ShieldCheck, RefreshCw } from 'lucide-react';

export default function Dashboard({ setActiveTab }) {
  const [metrics, setMetrics] = useState({
    total_chats: 0,
    open_tickets: 0,
    avg_resolution_time_hours: 0,
    user_count: 0
  });
  const [docsCount, setDocsCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardMetrics();
      setMetrics(data);
      const docs = await api.getDocuments();
      setDocsCount(docs.length);
    } catch (err) {
      console.error("Error loading dashboard metrics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const cards = [
    {
      title: "Total Chats",
      value: metrics.total_chats,
      desc: "Client sessions logged",
      icon: MessageSquare,
      color: "var(--color-primary)",
      glow: "var(--color-primary-glow)"
    },
    {
      title: "Open Tickets",
      value: metrics.open_tickets,
      desc: "Escalated queue pending",
      icon: Ticket,
      color: "var(--color-warning)",
      glow: "var(--color-warning-glow)"
    },
    {
      title: "Avg Resolution",
      value: `${metrics.avg_resolution_time_hours}h`,
      desc: "Ticket closing speed",
      icon: Clock,
      color: "var(--color-success)",
      glow: "var(--color-success-glow)"
    },
    {
      title: "Registered Users",
      value: metrics.user_count,
      desc: "Agent and client base",
      icon: Users,
      color: "var(--color-danger)",
      glow: "var(--color-danger-glow)"
    }
  ];

  return (
    <div className="animate-fade-in" style={{ padding: '30px', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Operational Workspace</h1>
          <p className="page-subtitle">Enterprise cognitive support control hub</p>
        </div>
        <button className="btn btn-secondary btn-icon" onClick={fetchDashboardData} title="Refresh Statistics">
          <RefreshCw size={18} className={loading ? "animate-spin" : ""} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        {cards.map((card, idx) => (
          <div key={idx} className="card card-hover" style={{ position: 'relative', overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 500 }}>{card.title}</p>
                <h3 style={{ fontSize: '2rem', margin: '8px 0 4px 0', fontFamily: 'var(--font-display)' }}>
                  {loading ? "..." : card.value}
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{card.desc}</p>
              </div>
              <div style={{ 
                background: card.glow, 
                color: card.color, 
                padding: '12px', 
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <card.icon size={22} />
              </div>
            </div>
            <div style={{ 
              position: 'absolute', 
              bottom: 0, 
              left: 0, 
              width: '100%', 
              height: '3px', 
              background: card.color 
            }} />
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '30px' }}>
        
        {/* Core Quick Action shortcuts */}
        <div className="card glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ fontSize: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            Quick Actions
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Access components to build files indexing, chat with RAG vectors, assign helpdesk agent Bob, or load forecasting models.
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <button className="btn btn-secondary" style={{ justifyContent: 'space-between' }} onClick={() => setActiveTab('kb')}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                Index PDF Manuals ({docsCount} Loaded)
              </span>
              <ArrowRight size={16} />
            </button>
            <button className="btn btn-secondary" style={{ justifyContent: 'space-between' }} onClick={() => setActiveTab('chat')}>
              <span>Test AI Chat Assistant</span>
              <ArrowRight size={16} />
            </button>
            <button className="btn btn-secondary" style={{ justifyContent: 'space-between' }} onClick={() => setActiveTab('tickets')}>
              <span>View Open Support Tickets</span>
              <ArrowRight size={16} />
            </button>
            <button className="btn btn-secondary" style={{ justifyContent: 'space-between' }} onClick={() => setActiveTab('analytics')}>
              <span>View Time-Series Analytics & Forecasting</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>

        {/* System Diagnostic Status */}
        <div className="card glass-panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              System Health
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Core API Engine</span>
                <span className="badge badge-success" style={{ gap: '4px' }}>
                  <ShieldCheck size={12} /> online
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>SQL Database (PostgreSQL)</span>
                <span className="badge badge-success" style={{ gap: '4px' }}>
                  <ShieldCheck size={12} /> active
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Vector Store (ChromaDB)</span>
                <span className="badge badge-success" style={{ gap: '4px' }}>
                  <ShieldCheck size={12} /> active
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Local LLM Server (Ollama)</span>
                <span className="badge badge-neutral">Standby</span>
              </div>
            </div>
          </div>
          
          <div style={{ marginTop: '24px', padding: '12px 16px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Hardware execution active: Python 3.14.6 Environment on PostgreSQL & HNSW Vector Indexes.
          </div>
        </div>

      </div>
    </div>
  );
}
