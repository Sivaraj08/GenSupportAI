import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import KnowledgeBase from './pages/KnowledgeBase';
import ChatBot from './pages/ChatBot';
import TicketCenter from './pages/TicketCenter';
import Analytics from './pages/Analytics';
import { LayoutDashboard, Database, MessageSquare, Ticket, BarChart3, ShieldAlert } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'kb', label: 'Knowledge Base', icon: Database },
    { id: 'chat', label: 'AI Support Chat', icon: MessageSquare },
    { id: 'tickets', label: 'Ticket Center', icon: Ticket },
    { id: 'analytics', label: 'Predictive Analytics', icon: BarChart3 }
  ];

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard setActiveTab={setActiveTab} />;
      case 'kb':
        return <KnowledgeBase />;
      case 'chat':
        return <ChatBot />;
      case 'tickets':
        return <TicketCenter />;
      case 'analytics':
        return <Analytics />;
      default:
        return <Dashboard setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="app-container">
      
      {/* Navigation Sidebar */}
      <div style={{
        width: 'var(--sidebar-width)',
        background: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0
      }}>
        {/* Sidebar Brand header */}
        <div style={{
          height: 'var(--header-height)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '0 24px',
          borderBottom: '1px solid var(--border-color)'
        }}>
          <div style={{
            width: '32px',
            height: '32px',
            background: 'linear-gradient(135deg, var(--color-primary), #4f46e5)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 10px rgba(99, 102, 241, 0.3)'
          }}>
            <ShieldAlert size={18} style={{ color: '#fff' }} />
          </div>
          <span style={{ 
            fontFamily: 'var(--font-display)', 
            fontWeight: 700, 
            fontSize: '1.15rem', 
            letterSpacing: '-0.02em',
            background: 'linear-gradient(to right, #fff, var(--text-secondary))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            GenSupportAI
          </span>
        </div>

        {/* Sidebar Navigation Items */}
        <div style={{ flex: 1, padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {navigationItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderRadius: '10px',
                  border: 'none',
                  background: isActive ? 'var(--color-primary)' : 'transparent',
                  color: isActive ? '#fff' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: isActive ? 600 : 500,
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: isActive ? '0 4px 12px rgba(99, 102, 241, 0.25)' : 'none',
                  textAlign: 'left'
                }}
                className={!isActive ? "sidebar-item-hover" : ""}
              >
                <item.icon size={18} />
                {item.label}
              </button>
            );
          })}
        </div>

        {/* Sidebar Footer details */}
        <div style={{ padding: '20px 24px', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          © 2026 GenSupportAI.<br />Enterprise Edition v1.0.0
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        
        {/* Global top bar */}
        <div style={{
          height: 'var(--header-height)',
          borderBottom: '1px solid var(--border-color)',
          background: 'var(--bg-secondary)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 30px',
          justifyContent: 'flex-end',
          flexShrink: 0
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ textAlign: 'right' }}>
              <p style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Bob Agent</p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Support Operator</p>
            </div>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #4f46e5, var(--color-primary))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 600,
              fontSize: '0.85rem',
              color: '#fff',
              border: '2px solid var(--border-color)'
            }}>
              BA
            </div>
          </div>
        </div>

        {/* Tab View Container */}
        <div style={{ flex: 1, overflowY: 'auto', background: 'var(--bg-primary)' }}>
          {renderActiveView()}
        </div>

      </div>
    </div>
  );
}
