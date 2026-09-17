# GenSupportAI: Enterprise AI Customer Support Knowledge Assistant
## System Architecture & Technical Specifications

This is the functional design document for GenSupportAI. It contains database schemas (SQL DDL), directory architectures, API routes, configurations, and core workflows.

---

## 1. System Overview & Technology Stack

GenSupportAI integrates RAG-based search, dynamic LLM chatting, predictive ticket routing, and analytics.

| Layer | Technology | Version / Configuration | Purpose |
|---|---|---|---|
| **Frontend** | React + Vite + Vanilla CSS | React 18+, ES6 | Responsive agent & admin dashboard with custom interactive UI elements |
| **Backend** | FastAPI | Python 3.10+ | High-performance, asynchronous REST and WebSocket API gateway |
| **Database** | PostgreSQL | Version 15+ | Relational data persistence for users, chat sessions, logs, and tickets |
| **Vector Store** | ChromaDB / FAISS | Local Instance | High-dimensional embedding storage and cosine similarity indexing |
| **Embeddings** | SentenceTransformers | `all-MiniLM-L6-v2` (384 dimensions) | Converts document text chunks into numeric vectors |
| **LLM Engine** | Ollama (Local) | Llama 3 (8B) or Gemma 2 (9B) | Local, privacy-preserving conversational inference and synthesis |
| **Analytics/ML** | Scikit-Learn & Statsmodels | XGBoost, ARIMA/Prophet | Classification of ticket priority/categories and time-series volume forecasting |

---

## 2. Directory Structure Blueprint

To initialize the project, establish the following folder layout:

```text
gensupportai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Application bootstrapper
│   │   ├── config.py               # Application configurations
│   │   ├── database.py             # Database engine & session maker
│   │   ├── models/                 # SQLAlchemy Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   ├── chat.py
│   │   │   └── ticket.py
│   │   ├── schemas/                # Pydantic schema declarations
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   ├── chat.py
│   │   │   └── ticket.py
│   │   ├── routers/                # API router blueprints
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── chat.py
│   │   │   ├── ticket.py
│   │   │   └── analytics.py
│   │   └── services/               # Core algorithms & ML pipelines
│   │       ├── __init__.py
│   │       ├── rag_service.py       # Document extraction, splitting, and upsert
│   │       ├── llm_service.py       # Inference connector
│   │       ├── ticket_service.py    # Auto-classifier and router
│   │       └── analytics_service.py # Time-series forecaster and sentiment extractor
│   ├── requirements.txt            # System dependencies list
│   └── Dockerfile
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/             # Dynamic and shared UI components
    │   ├── layouts/                # Main sidebar & nav layout
    │   ├── pages/                  # Application views
    │   │   ├── Dashboard.jsx        # Landing interface
    │   │   ├── KnowledgeBase.jsx    # File manager and uploader
    │   │   ├── ChatBot.jsx          # AI assistant conversational window
    │   │   ├── TicketCenter.jsx     # Kanban Board for agent dispatching
    │   │   └── Analytics.jsx        # Trend models and forecast grids
    │   ├── services/               # Axios API client handlers
    │   │   └── api.js
    │   ├── App.jsx                 # Routes coordinator
    │   ├── index.css               # Core styling tokens
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

---

## 3. Relational Database Schema (SQL DDL)

Copy and execute these SQL commands to initialize your relational database tables:

```sql
-- Enable UUID extension if using PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'agent', 'customer')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Knowledge Documents Table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('uploading', 'processing', 'indexed', 'failed')),
    chunk_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Document Chunks (Local references)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    vector_ref VARCHAR(255) NOT NULL -- Links directly to vector store ID
);

-- 4. Chat Sessions Table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'resolved', 'escalated')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Chat Messages Table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender VARCHAR(50) NOT NULL CHECK (sender IN ('user', 'assistant')),
    content TEXT NOT NULL,
    retrieved_chunks JSONB DEFAULT '[]'::jsonb, -- Store list of source chunk metadata
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tickets Table (Support Escalate)
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID UNIQUE REFERENCES chat_sessions(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(50) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    category VARCHAR(50) NOT NULL CHECK (category IN ('billing', 'technical', 'sales', 'general')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved')),
    assigned_agent_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);
```

---

## 4. RAG & Core Algorithms Design Configurations

### RAG Chunking Configuration
*   **Chunk Size:** `800` characters.
*   **Chunk Overlap:** `150` characters.
*   **Chunking Strategy:** Recursive character splitting using separator sequence: `["\n\n", "\n", " ", ""]`.
*   **Similarity Search Metrics:** L2 Euclidean Distance / Cosine Similarity (Chroma default).
*   **Context Limit ($K$ value):** Pass the top `3` similarity results as context.

### LLM System Prompt Template
```text
System Prompt:
You are GenSupportAI, a helpful, polite enterprise customer support virtual assistant.
Answer the User's question using ONLY the facts provided in the Context sections below.
If the Context does not contain the answer, reply exactly with:
"I am sorry, but I cannot locate that information in the official documentation. Would you like me to open a support ticket for our human agents?"

Context:
---------------------
{context_chunks}
---------------------

Conversation History:
{history_context}

User Question: {user_query}
AI Response:
```

### Ticket Auto-Classifier
*   **Feature Extraction:** TF-IDF representation of conversation logs or summary vectors.
*   **Category Predictor:** Linear Support Vector Classification (LinearSVC) or XGBoost trained on annotated text fields.
*   **Priority Predictor:** Heuristic logic combined with sentiment output:
    *   If sentiment is `negative` and contains keywords like `broken`, `crashed`, `security`, `urgent` -> Priority: `critical` or `high`.
    *   If sentiment is `neutral` -> Priority: `medium` or `low`.

---

## 5. Primary API Routes & Contract Definitions

### Authentication & Users
*   `POST /api/users` - Register standard users, agents, and administrators.
*   `GET /api/users/{id}` - Fetch user profiles and system permissions.

### Knowledge Base (RAG)
*   `POST /api/documents/upload` - Upload PDF files. Initiates parsing, splitting, embedding, and vector insertion.
*   `GET /api/documents` - Fetches status list of indexing processes.
*   `DELETE /api/documents/{id}` - Deletes a document, its local chunks, and its vector space embeddings from ChromaDB.

### Agent Conversational Bot
*   `POST /api/chat/session` - Initializes a conversational session.
*   `POST /api/chat/message` - Accepts user query, triggers RAG pipelines, compiles logs, and generates a response.
*   `GET /api/chat/session/{id}/messages` - Loads chronological scroll history.

### Ticket Support Desk
*   `POST /api/tickets/escalate` - Submits historical chat summaries to the classifier and creates a support ticket.
*   `GET /api/tickets` - List filters (status, category, assigned agent).
*   `PATCH /api/tickets/{id}/assign` - Re-assigns tickets to different department agents.
*   `PATCH /api/tickets/{id}/status` - Sets ticket states (`open`, `in_progress`, `resolved`).

### Management Analytics
*   `GET /api/analytics/dashboard` - Outputs high-level KPI cards (Total chats, pending tickets, average resolution speed).
*   `GET /api/analytics/sentiment` - Aggregated chat sentiment ratios (Positive / Neutral / Negative).
*   `GET /api/analytics/forecasting` - Serves 7-day projected ticket volumes generated by time-series prediction runs.

---

## 6. Execution & Setup Instructions

Follow these setup steps to run the stack:

### Step 1: Backend Initialization
```bash
# Navigate to the backend directory
cd backend

# Create Python virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server locally
uvicorn app.main:app --reload --port 8000
```

### Step 2: Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install package dependencies
npm install

# Run hot-reloading development server
npm run dev
```
