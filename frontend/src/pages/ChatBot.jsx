import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { MessageSquare, Send, Plus, AlertCircle, FileText, ChevronDown, ChevronUp, AlertTriangle, RefreshCw, GraduationCap, Briefcase, UserCheck, Search } from 'lucide-react';

const suggestionSections = [
  {
    title: "Examination Support",
    icon: GraduationCap,
    description: "Students can ask:",
    color: "var(--color-primary)",
    items: [
      { label: "Exam timetable", query: "Where can I find the exam timetable and schedule?" },
      { label: "Hall ticket download", query: "How do I download my exam hall ticket?" },
      { label: "Internal marks", query: "How can I check my internal marks and assessment weightage?" },
      { label: "Revaluation process", query: "What is the revaluation process and script photocopy policy?" }
    ]
  },
  {
    title: "Placement Cell Assistant",
    icon: Briefcase,
    description: "Students can ask:",
    color: "var(--color-success)",
    items: [
      { label: "Placement eligibility", query: "What are the eligibility criteria and training requirements for placements?" },
      { label: "Company requirements", query: "What are the company requirements and domains for recruitment?" },
      { label: "Interview schedule", query: "Where can I see the campus placement interview schedule?" },
      { label: "Resume guidelines", query: "What are the placement resume guidelines and templates?" },
      { label: "Internship opportunities", query: "What internship opportunities are available for students?" }
    ]
  },
  {
    title: "Faculty Support",
    icon: UserCheck,
    description: "Faculty members can ask about:",
    color: "var(--color-warning)",
    items: [
      { label: "Leave policies", query: "What are the casual, duty, and medical leave policies for faculty?" },
      { label: "Academic calendar", query: "Where is the academic calendar and key semester dates?" },
      { label: "Examination duties", query: "What are the examination invigilation duties and guidelines for faculty?" }
    ]
  }
];

export default function ChatBot() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  
  // Escalation Modal States
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [escalateTitle, setEscalateTitle] = useState("");
  const [escalateDesc, setEscalateDesc] = useState("");
  const [escalating, setEscalating] = useState(false);

  // Source snippet expansions mapping (messageId -> boolean)
  const [expandedSources, setExpandedSources] = useState({});

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const initChat = async () => {
    try {
      // Fetch all existing sessions from database
      const fetchedSessions = await api.getSessions();
      if (fetchedSessions && fetchedSessions.length > 0) {
        setSessions(fetchedSessions);
        // Load active session from localStorage if it exists, otherwise use the first (newest) one
        const savedSessionId = localStorage.getItem("activeSessionId");
        if (savedSessionId && fetchedSessions.some(s => s.id === savedSessionId)) {
          setActiveSessionId(savedSessionId);
        } else {
          setActiveSessionId(fetchedSessions[0].id);
        }
      } else {
        // Create a default session to start with if none exist
        const session = await api.createSession();
        setActiveSessionId(session.id);
        setSessions([session]);
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to initialize session:", err);
    }
  };

  useEffect(() => {
    initChat();
  }, []);

  // Fetch session history when activeSessionId changes
  useEffect(() => {
    if (!activeSessionId) return;

    localStorage.setItem("activeSessionId", activeSessionId);

    const fetchHistory = async () => {
      try {
        const history = await api.getSessionMessages(activeSessionId);
        setMessages(history);
      } catch (err) {
        console.error("Failed to load message history:", err);
      }
    };
    
    fetchHistory();
  }, [activeSessionId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const handleCreateNewSession = async () => {
    try {
      const session = await api.createSession();
      setSessions(prev => [session, ...prev]);
      setActiveSessionId(session.id);
      setMessages([]);
    } catch (err) {
      console.error("New session error:", err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !activeSessionId || sending) return;

    const userQuery = input;
    setInput("");
    setSending(true);

    // Optimistically insert user message in state
    const tempUserMsg = {
      id: "temp-user-" + Date.now(),
      sender: "user",
      content: userQuery,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const aiReply = await api.sendMessage(activeSessionId, userQuery);
      setMessages(prev => {
        // filter out optimistic message to avoid duplicate mapping keys
        const filtered = prev.filter(m => !m.id.toString().startsWith("temp-user-"));
        return [...filtered, tempUserMsg, aiReply];
      });

      // Update session title in sidebar if it's the first message or currently untitled
      const currentSession = sessions.find(s => s.id === activeSessionId);
      if (!currentSession || !currentSession.title) {
        try {
          const updatedSessions = await api.getSessions();
          if (updatedSessions) {
            setSessions(updatedSessions);
          }
        } catch (titleErr) {
          console.error("Failed to update session list/title:", titleErr);
        }
      }
    } catch (err) {
      console.error("Send message error:", err);
      const tempErrorMsg = {
        id: "temp-error-" + Date.now(),
        sender: "assistant",
        content: "Error: Failed to fetch reply from API server. Please check FastAPI backend connection.",
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, tempErrorMsg]);
    } finally {
      setSending(false);
    }
  };

  const handleEscalationSubmit = async (e) => {
    e.preventDefault();
    if (!escalateTitle.trim() || !escalateDesc.trim() || escalating || !activeSessionId) return;

    setEscalating(true);
    try {
      const ticket = await api.escalateSession(activeSessionId, escalateTitle, escalateDesc);
      alert(`Ticket created successfully! Category: ${ticket.category.toUpperCase()}, Priority: ${ticket.priority.toUpperCase()}`);
      setShowEscalateModal(false);
      setEscalateTitle("");
      setEscalateDesc("");
      
      // Update session status in state
      setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, status: "escalated" } : s));
    } catch (err) {
      console.error("Escalation error:", err);
      alert("Failed to escalate chat to support ticket: " + err.message);
    } finally {
      setEscalating(false);
    }
  };

  const toggleSourceExpansion = (msgId, sourceIdx) => {
    const key = `${msgId}-${sourceIdx}`;
    setExpandedSources(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const openEscalateDialog = () => {
    // Populate description with last user messages if any
    const userMsgs = messages.filter(m => m.sender === 'user');
    const lastUserQuery = userMsgs.length > 0 ? userMsgs[userMsgs.length - 1].content : "";
    setEscalateDesc(lastUserQuery);
    setEscalateTitle(lastUserQuery ? `Query: ${lastUserQuery.substring(0, 30)}...` : "Support Request");
    setShowEscalateModal(true);
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', height: 'calc(100vh - var(--header-height))', background: 'var(--bg-primary)' }}>
      
      {/* Sessions Sidebar */}
      <div style={{
        width: '260px',
        borderRight: '1px solid var(--border-color)',
        background: 'var(--bg-secondary)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0
      }}>
        <div style={{ padding: '16px', borderBottom: '1px solid var(--border-color)' }}>
          <button className="btn btn-secondary" onClick={handleCreateNewSession} style={{ width: '100%', gap: '8px' }}>
            <Plus size={16} /> New Session
          </button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
          {sessions.map((s) => (
            <div
              key={s.id}
              onClick={() => setActiveSessionId(s.id)}
              style={{
                padding: '12px 14px',
                borderRadius: '8px',
                marginBottom: '8px',
                cursor: 'pointer',
                background: s.id === activeSessionId ? 'rgba(99, 102, 241, 0.08)' : 'transparent',
                border: `1px solid ${s.id === activeSessionId ? 'var(--color-primary)' : 'transparent'}`,
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}
            >
              <MessageSquare size={16} style={{ color: s.id === activeSessionId ? 'var(--color-primary)' : 'var(--text-muted)' }} />
              <div style={{ overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis', fontSize: '0.85rem', flex: 1 }}>
                {s.title || `Chat Session ${s.id.substring(0, 5)}`}
              </div>
              {s.status === 'escalated' && (
                <span className="badge badge-warning" style={{ fontSize: '0.65rem', padding: '2px 5px' }}>TKT</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Main chat window */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'rgba(9, 13, 22, 0.3)' }}>
        
        {/* Active Chat Header */}
        <div style={{ height: '60px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px', background: 'var(--bg-secondary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '8px', height: '8px', background: 'var(--color-success)', borderRadius: '50%' }} />
            <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>Student Query Assistant</span>
          </div>

          <button className="btn btn-secondary btn-icon" onClick={openEscalateDialog} style={{ fontSize: '0.8rem', padding: '6px 12px', gap: '6px', color: 'var(--color-warning)', borderColor: 'rgba(245,158,11,0.2)' }}>
            <AlertTriangle size={14} /> Escalate to Ticket
          </button>
        </div>

        {/* Messages Stream */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {messages.length === 0 && !sending ? (
            <div className="animate-fade-in" style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '100%',
              padding: '40px 20px',
              maxWidth: '960px',
              margin: '0 auto',
              gap: '24px'
            }}>
              <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '60px',
                  height: '60px',
                  borderRadius: '16px',
                  background: 'rgba(99, 102, 241, 0.1)',
                  color: 'var(--color-primary)',
                  marginBottom: '16px',
                  border: '1px solid rgba(99, 102, 241, 0.2)',
                  boxShadow: '0 8px 24px rgba(99, 102, 241, 0.15)'
                }}>
                  <MessageSquare size={30} />
                </div>
                <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px', fontFamily: 'var(--font-display)', letterSpacing: '-0.02em' }}>
                  AI Support Assistant
                </h2>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto', lineHeight: '1.5' }}>
                  Welcome! Access instant RAG-powered answers regarding exams, placements, and faculty administrative guidelines. Select a quick query below or type your own question.
                </p>
              </div>

              {/* Suggestions Grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '20px',
                width: '100%',
                marginTop: '10px'
              }}>
                {suggestionSections.map((section, idx) => (
                  <div key={idx} className="card glass-panel" style={{
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '20px',
                    borderRadius: '16px',
                    border: '1px solid var(--border-color)',
                    background: 'var(--bg-secondary)',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    position: 'relative',
                    overflow: 'hidden'
                  }}>
                    {/* Header with icon and title */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '36px',
                        height: '36px',
                        borderRadius: '10px',
                        background: `${section.color}15`,
                        color: section.color,
                        border: `1px solid ${section.color}30`
                      }}>
                        <section.icon size={18} />
                      </div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 650, color: 'var(--text-primary)', margin: 0 }}>
                        {section.title}
                      </h4>
                    </div>

                    <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      {section.description}
                    </p>

                    {/* Question items */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
                      {section.items.map((item, itemIdx) => (
                        <button
                          key={itemIdx}
                          type="button"
                          onClick={() => {
                            setInput(item.query);
                            inputRef.current?.focus();
                          }}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '10px 12px',
                            background: 'rgba(255, 255, 255, 0.02)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '8px',
                            color: 'var(--text-secondary)',
                            fontSize: '0.825rem',
                            textAlign: 'left',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                            width: '100%',
                            gap: '8px'
                          }}
                        >
                          <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.label}</span>
                          <Search size={12} style={{ opacity: 0.6 }} />
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => {
              const isUser = msg.sender === 'user';
              return (
                <div key={msg.id} style={{
                  alignSelf: isUser ? 'flex-end' : 'flex-start',
                  maxWidth: '75%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: isUser ? 'flex-end' : 'flex-start',
                  animation: 'fadeIn 0.2s ease-out'
                }}>
                  {/* Text bubble */}
                  <div style={{
                    padding: '14px 18px',
                    borderRadius: '16px',
                    background: isUser ? 'var(--bg-tertiary)' : 'var(--glass-bg)',
                    border: isUser ? '1px solid var(--border-color)' : '1px solid rgba(99, 102, 241, 0.15)',
                    boxShadow: isUser ? 'var(--shadow-sm)' : '0 4px 12px rgba(99,102,241,0.03)',
                    color: 'var(--text-primary)',
                    fontSize: '0.9rem',
                    lineHeight: '1.45',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {msg.content}
                  </div>


                </div>
              );
            })
          )}
          
          {sending && (
            <div style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 16px', borderRadius: '16px', background: 'var(--glass-bg)', border: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              <RefreshCw size={14} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
              <span>AI is thinking...</span>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSendMessage} style={{ padding: '16px 24px', borderTop: '1px solid var(--border-color)', background: 'var(--bg-secondary)', display: 'flex', gap: '12px' }}>
          <input
            type="text"
            className="form-input"
            value={input}
            ref={inputRef}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a student query (e.g., Syllabus for AI, attendance requirements)..."
            disabled={sending || !activeSessionId}
          />
          <button type="submit" className="btn btn-primary" disabled={sending || !input.trim() || !activeSessionId} style={{ padding: '0 20px', gap: '6px' }}>
            <Send size={15} /> Send
          </button>
        </form>

      </div>

      {/* Escalation Modal Dialog */}
      {showEscalateModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          background: 'rgba(0,0,0,0.6)',
          backdropFilter: 'blur(4px)',
          zIndex: 2000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div className="card glass-panel animate-fade-in" style={{ width: '480px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <h3 style={{ fontSize: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-warning)' }}>
              <AlertTriangle size={18} /> Escalate support ticket
            </h3>
            
            <form onSubmit={handleEscalationSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 550 }}>TICKET TITLE</label>
                <input
                  type="text"
                  className="form-input"
                  value={escalateTitle}
                  onChange={(e) => setEscalateTitle(e.target.value)}
                  placeholder="Summarize the core problem..."
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 550 }}>ISSUE DESCRIPTION</label>
                <textarea
                  className="form-input"
                  style={{ minHeight: '120px', resize: 'vertical' }}
                  value={escalateDesc}
                  onChange={(e) => setEscalateDesc(e.target.value)}
                  placeholder="Provide all context so the classifier can predict priority..."
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '10px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowEscalateModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: 'var(--color-warning)' }} disabled={escalating}>
                  {escalating ? "Submitting..." : "Submit Ticket"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
