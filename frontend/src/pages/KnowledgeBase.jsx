import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Upload, FileText, Trash2, AlertCircle, RefreshCw, Layers } from 'lucide-react';

export default function KnowledgeBase() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);

  const fetchDocuments = async () => {
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to load documents:", err);
      showAlert("danger", "Failed to fetch document registry list from API.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // Poll every 8 seconds to update document index processing states dynamically
    const interval = setInterval(fetchDocuments, 8000);
    return () => clearInterval(interval);
  }, []);

  const showAlert = (type, text) => {
    setAlert({ type, text });
    setTimeout(() => setAlert(null), 5000);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowedExtensions = [".pdf", ".xlsx", ".xls", ".csv"];
    const fileExtension = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
      showAlert("danger", "Only PDF, Excel (.xlsx, .xls), and CSV files are supported for RAG indexing.");
      return;
    }

    setUploading(true);
    showAlert("info", `Uploading '${file.name}' and initiating RAG splitting...`);

    try {
      await api.uploadDocument(file);
      showAlert("success", `'${file.name}' uploaded successfully. Ingestion in progress.`);
      fetchDocuments();
    } catch (err) {
      console.error("Upload error:", err);
      showAlert("danger", err.message || "Failed to upload document.");
    } finally {
      setUploading(false);
      e.target.value = ""; // clear file input
    }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Are you sure you want to delete '${name}'? This will permanently remove its SQLite chunks and vector embeddings.`)) {
      return;
    }

    try {
      await api.deleteDocument(id);
      showAlert("success", `'${name}' and associated vectors deleted successfully.`);
      fetchDocuments();
    } catch (err) {
      console.error("Delete error:", err);
      showAlert("danger", "Failed to delete document and vectors.");
    }
  };

  const formatSize = (bytes) => {
    if (!bytes) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="animate-fade-in" style={{ padding: '30px', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Alerts system */}
      {alert && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          zIndex: 1000,
          background: alert.type === 'success' ? 'var(--color-success-glow)' : alert.type === 'danger' ? 'var(--color-danger-glow)' : 'rgba(99, 102, 241, 0.2)',
          border: `1px solid ${alert.type === 'success' ? 'var(--color-success)' : alert.type === 'danger' ? 'var(--color-danger)' : 'var(--color-primary)'}`,
          color: alert.type === 'success' ? 'var(--color-success)' : alert.type === 'danger' ? 'var(--color-danger)' : 'var(--color-primary)',
          padding: '14px 20px',
          borderRadius: '12px',
          backdropFilter: 'blur(8px)',
          boxShadow: 'var(--shadow-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          animation: 'fadeIn 0.25s ease-out'
        }}>
          <AlertCircle size={18} />
          <span style={{ fontSize: '0.9rem', fontWeight: 550 }}>{alert.text}</span>
        </div>
      )}

      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Knowledge Library</h1>
          <p className="page-subtitle">Upload organizational manuals and seed the RAG pipeline</p>
        </div>
        <button className="btn btn-secondary btn-icon" onClick={fetchDocuments} title="Refresh document list">
          <RefreshCw size={16} />
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px', alignItems: 'start' }}>
        
        {/* Upload Card */}
        <div className="card glass-panel" style={{ textAlign: 'center', padding: '40px 30px' }}>
          <div style={{ 
            width: '64px', 
            height: '64px', 
            background: 'var(--color-primary-glow)', 
            color: 'var(--color-primary)', 
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px auto'
          }}>
            <Upload size={28} />
          </div>
          
          <h3 style={{ fontSize: '1.25rem', marginBottom: '8px' }}>Upload Document</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '24px' }}>
            Supported formats: **PDF, Excel, CSV**. Upload manuals or spreadsheets to parse, index, and query.
          </p>
          
          <label className="btn btn-primary" style={{ cursor: 'pointer', display: 'inline-flex', opacity: uploading ? 0.7 : 1, pointerEvents: uploading ? 'none' : 'auto' }}>
            <Upload size={16} />
            {uploading ? "Indexing Pipeline Active..." : "Choose Knowledge File"}
            <input type="file" accept=".pdf,.xlsx,.xls,.csv" onChange={handleFileUpload} style={{ display: 'none' }} />
          </label>
        </div>

        {/* Documents Registry Table */}
        <div className="card glass-panel" style={{ gridColumn: 'span 2', minHeight: '300px' }}>
          <h3 style={{ fontSize: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={18} style={{ color: 'var(--color-primary)' }} />
            Indexed Knowledge Registry
          </h3>

          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', alignItems: 'center', justifyContent: 'center', height: '180px', color: 'var(--text-secondary)' }}>
              <RefreshCw size={24} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
              <p style={{ fontSize: '0.85rem' }}>Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '180px', color: 'var(--text-muted)' }}>
              <FileText size={40} style={{ marginBottom: '12px', opacity: 0.4 }} />
              <p style={{ fontSize: '0.9rem' }}>No documents indexed yet.</p>
              <p style={{ fontSize: '0.75rem' }}>Upload your first support manual on the left panel.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px 8px', fontWeight: 500 }}>Filename</th>
                    <th style={{ padding: '12px 8px', fontWeight: 500 }}>Upload Date</th>
                    <th style={{ padding: '12px 8px', fontWeight: 500 }}>Chunks</th>
                    <th style={{ padding: '12px 8px', fontWeight: 500 }}>Status</th>
                    <th style={{ padding: '12px 8px', fontWeight: 500, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', transition: 'background 0.2s' }} className="table-row-hover">
                      <td style={{ padding: '14px 8px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <FileText size={16} style={{ color: 'var(--color-primary)', flexShrink: 0 }} />
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '280px' }} title={doc.filename}>
                          {doc.filename}
                        </span>
                      </td>
                      <td style={{ padding: '14px 8px', color: 'var(--text-secondary)' }}>{formatDate(doc.created_at)}</td>
                      <td style={{ padding: '14px 8px', fontWeight: 600 }}>{doc.chunk_count}</td>
                      <td style={{ padding: '14px 8px' }}>
                        {doc.status === 'indexed' ? (
                          <span className="badge badge-success">indexed</span>
                        ) : doc.status === 'processing' ? (
                          <span className="badge badge-warning" style={{ gap: '4px' }}>
                            <RefreshCw size={10} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                            indexing...
                          </span>
                        ) : (
                          <span className="badge badge-danger">failed</span>
                        )}
                      </td>
                      <td style={{ padding: '14px 8px', textAlign: 'right' }}>
                        <button className="btn btn-danger btn-icon" onClick={() => handleDelete(doc.id, doc.filename)} title="Delete Document & Chunks" style={{ padding: '6px' }}>
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
