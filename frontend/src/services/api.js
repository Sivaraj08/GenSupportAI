const API_BASE = "http://localhost:8000/api";

async function request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    // Set headers
    const headers = options.headers || {};
    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }
    
    const config = {
        ...options,
        headers
    };
    
    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            const errBody = await response.json().catch(() => ({}));
            throw new Error(errBody.detail || `HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API Request failed on ${endpoint}:`, error);
        throw error;
    }
}

export const api = {
    // Documents (RAG Ingestion)
    uploadDocument: async (file) => {
        const formData = new FormData();
        formData.append("file", file);
        return request("/documents/upload", {
            method: "POST",
            body: formData
        });
    },
    getDocuments: async () => request("/documents"),
    deleteDocument: async (id) => request(`/documents/${id}`, { method: "DELETE" }),
    
    // Chat sessions
    getSessions: async () => request("/chat/sessions"),
    createSession: async (userId = null) => request("/chat/session", {
        method: "POST",
        body: JSON.stringify({ user_id: userId })
    }),
    getSessionMessages: async (sessionId) => request(`/chat/session/${sessionId}/messages`),
    sendMessage: async (sessionId, content) => request("/chat/message", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, content })
    }),
    
    // Tickets
    escalateSession: async (sessionId, title, description) => request("/tickets/escalate", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, title, description })
    }),
    getTickets: async (filters = {}) => {
        const params = new URLSearchParams();
        if (filters.status) params.append("status", filters.status);
        if (filters.category) params.append("category", filters.category);
        if (filters.assigned_agent_id) params.append("assigned_agent_id", filters.assigned_agent_id);
        
        const queryString = params.toString() ? `?${params.toString()}` : "";
        return request(`/tickets${queryString}`);
    },
    updateTicketStatus: async (ticketId, status) => request(`/tickets/${ticketId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status })
    }),
    assignTicket: async (ticketId, agentId) => request(`/tickets/${ticketId}/assign`, {
        method: "PATCH",
        body: JSON.stringify({ assigned_agent_id: agentId })
    }),
    
    // Analytics
    getDashboardMetrics: async () => request("/analytics/dashboard"),
    getSentimentMetrics: async () => request("/analytics/sentiment"),
    getForecastingMetrics: async () => request("/analytics/forecasting")
};
