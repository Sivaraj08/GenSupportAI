import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Ticket, ArrowRight, CheckCircle, RefreshCw } from 'lucide-react';

export default function TicketCenter() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  
  // Mock agents list
  const agents = [
    { id: "852601a1-bc2d-408c-a80c-5091ee952dbe", name: "Bob Agent" },
    { id: "c3d13dca-dc0e-4d21-96c9-481fdbffd3e9", name: "Alice Admin" }
  ];

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const data = await api.getTickets({
        status: statusFilter || null,
        category: categoryFilter || null
      });
      setTickets(data);
    } catch (err) {
      console.error("Failed to load tickets:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [statusFilter, categoryFilter]);

  const handleUpdateStatus = async (ticketId, nextStatus) => {
    try {
      await api.updateTicketStatus(ticketId, nextStatus);
      fetchTickets();
    } catch (err) {
      alert("Failed to update status: " + err.message);
    }
  };

  const handleAssignAgent = async (ticketId, agentId) => {
    try {
      await api.assignTicket(ticketId, agentId);
      fetchTickets();
    } catch (err) {
      alert("Failed to assign agent: " + err.message);
    }
  };

  const getPriorityBadge = (priority) => {
    const p = priority.toLowerCase();
    if (p === 'critical') return <span className="badge badge-danger">critical</span>;
    if (p === 'high') return <span className="badge badge-warning">high</span>;
    if (p === 'medium') return <span className="badge badge-info">medium</span>;
    return <span className="badge badge-neutral">low</span>;
  };

  const getCategoryBadge = (category) => {
    const c = category.toLowerCase();
    if (c === 'technical') return <span className="badge badge-neutral" style={{ color: 'var(--color-primary)', border: '1px solid var(--color-primary-glow)' }}>tech</span>;
    if (c === 'billing') return <span className="badge badge-neutral" style={{ color: 'var(--color-danger)', border: '1px solid var(--color-danger-glow)' }}>billing</span>;
    if (c === 'sales') return <span className="badge badge-neutral" style={{ color: 'var(--color-success)', border: '1px solid var(--color-success-glow)' }}>sales</span>;
    return <span className="badge badge-neutral">general</span>;
  };

  const getAgentName = (agentId) => {
    const agent = agents.find(a => a.id === agentId);
    return agent ? agent.name : "Unassigned";
  };

  // Group tickets by status for Kanban Board representation
  const columns = [
    { id: "open", title: "Open Queue", glow: "var(--color-danger-glow)", color: "var(--color-danger)" },
    { id: "in_progress", title: "In Progress", glow: "var(--color-warning-glow)", color: "var(--color-warning)" },
    { id: "resolved", title: "Resolved", glow: "var(--color-success-glow)", color: "var(--color-success)" }
  ];

  return (
    <div className="animate-fade-in" style={{ padding: '30px', maxWidth: '1200px', margin: '0 auto', height: 'calc(100vh - var(--header-height))', display: 'flex', flexDirection: 'column' }}>
      
      {/* Header */}
      <div className="page-header" style={{ marginBottom: '16px', flexShrink: 0 }}>
        <div>
          <h1 className="page-title">Support Ticket Desk</h1>
          <p className="page-subtitle">Track, route, and resolve AI-escalated customer tickets</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <select 
            className="form-input" 
            style={{ width: '140px', padding: '8px 12px', fontSize: '0.8rem' }}
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="technical">Technical</option>
            <option value="billing">Billing</option>
            <option value="sales">Sales</option>
            <option value="general">General</option>
          </select>
          
          <button className="btn btn-secondary btn-icon" onClick={fetchTickets}>
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Kanban Board Grid */}
      {loading && tickets.length === 0 ? (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <RefreshCw size={24} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '24px',
          flex: 1,
          overflow: 'hidden',
          minHeight: '400px'
        }}>
          {columns.map((col) => {
            const colTickets = tickets.filter(t => t.status === col.id);
            return (
              <div key={col.id} style={{
                background: 'rgba(15,21,36,0.3)',
                border: '1px solid var(--border-color)',
                borderRadius: '16px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                overflow: 'hidden'
              }}>
                {/* Column Title Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border-color)', marginBottom: '16px', flexShrink: 0 }}>
                  <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.95rem' }}>
                    <div style={{ width: '8px', height: '8px', background: col.color, borderRadius: '50%' }} />
                    {col.title}
                  </span>
                  <span style={{ padding: '2px 8px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>
                    {colTickets.length}
                  </span>
                </div>

                {/* Column Cards scroll list */}
                <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px', paddingRight: '4px' }}>
                  {colTickets.length === 0 ? (
                    <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem', padding: '40px 0' }}>
                      No tickets in column
                    </div>
                  ) : (
                    colTickets.map((t) => (
                      <div key={t.id} className="card animate-fade-in" style={{ padding: '16px', border: '1px solid var(--border-color)', background: 'var(--bg-secondary)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                            {getCategoryBadge(t.category)}
                            {getPriorityBadge(t.priority)}
                          </div>
                          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>{t.title}</h4>
                          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '6px', wordBreak: 'break-word', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }} title={t.description}>
                            {t.description}
                          </p>
                        </div>

                        {/* Assign Agent select bar */}
                        <div style={{ display: 'flex', alignItems: 'center', justifyStyle: 'space-between', gap: '8px', borderTop: '1px solid var(--border-color)', paddingTop: '12px', fontSize: '0.8rem' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Assign:</span>
                          <select 
                            style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', outline: 'none', cursor: 'pointer', fontWeight: 550 }}
                            value={t.assigned_agent_id || ""}
                            onChange={(e) => handleAssignAgent(t.id, e.target.value)}
                          >
                            <option value="" disabled>Select Agent</option>
                            {agents.map(ag => (
                              <option key={ag.id} value={ag.id} style={{ background: 'var(--bg-secondary)' }}>{ag.name}</option>
                            ))}
                          </select>
                        </div>

                        {/* Action buttons */}
                        <div style={{ display: 'flex', justifyStyle: 'flex-end', gap: '8px', marginTop: '4px' }}>
                          {col.id === 'open' && (
                            <button className="btn btn-secondary btn-icon" style={{ flex: 1, fontSize: '0.75rem', gap: '4px' }} onClick={() => handleUpdateStatus(t.id, "in_progress")}>
                              Start <ArrowRight size={12} />
                            </button>
                          )}
                          {col.id === 'in_progress' && (
                            <button className="btn btn-primary" style={{ flex: 1, fontSize: '0.75rem', gap: '4px', background: 'var(--color-success)' }} onClick={() => handleUpdateStatus(t.id, "resolved")}>
                              Resolve <CheckCircle size={12} />
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
