# 🧠 TaskRebuild

**TaskRebuild** is an intelligent, context-aware productivity suite consisting of a React-powered Chrome Extension and a massively scalable FastAPI/PostgreSQL backend. It is designed to act as a "Second Brain," automatically tracking your browsing activity, capturing research resources, and mapping your workflow into a vector-searchable AI Knowledge Graph.

---

## ✨ Core Engines

### 🔍 1. Google-Clone RRF Search Engine
TaskRebuild doesn't just do basic text search. It utilizes a custom **Reciprocal Rank Fusion (RRF)** engine built directly into PostgreSQL that simultaneously calculates and merges:
* **Semantic Meaning** (3072-Dimension Vector embeddings powered by Google Gemini AI)
* **Keyword Matches** (`tsvector` Full-Text Search)
* **Personal PageRank** (Logarithmic algorithmic boosts for pages you visit most frequently)
* **Recency Bias** (Decay mathematical boosts for fresher resources)

The frontend features lightning-fast `pg_trgm` Fuzzy Autocomplete and HTML Snippet Highlighting to show you exactly *why* a resource matched your query.

### 🕸️ 2. Automated Knowledge Graph
Every time you switch contexts, open a tab, or save a resource, the backend records it. Using Gemini AI, TaskRebuild analyzes your unstructured activity and automatically builds a mathematical Graph (`nodes` and `edges`) mapping exactly how your research topics connect to each other.

### 🛡️ 3. Strict Context Boundaries
Unlike standard bookmark managers that dump everything into one global bucket, TaskRebuild strictly binds your resources and searches to specific **Tasks**. If you search for a bug while inside your "Cooking Project," the database mathematically walls off the search space so you don't get polluted results from your "Coding Project."

### 📈 4. Zero-Latency System Metrics
The backend features an asynchronous background monitor that continually tracks CPU, RAM, Python Runtime states, and Vector Database capacities, broadcasting them live to the Extension's beautiful UI Dashboard.

---

## 🏗️ Architecture Stack

* **Frontend Chrome Extension:** React 18, TypeScript, Vite, Manifest V3
* **Backend API:** FastAPI (Python), Pydantic, httpx
* **Database:** Supabase (PostgreSQL), `pgvector` (HNSW/IVFFlat), `pg_trgm` (Fuzzy Logic)
* **AI Provider:** Google Gemini API (`embedding-001` & Text Models)
* **API Documentation:** Integrated Scalar UI (`/docs`)

---

## 🚀 Installation & Setup

### 1. The Database (Supabase)
1. Create a new Supabase project.
2. Enable the `pgvector` and `pg_trgm` extensions.
3. Run the provided `supabase_schema.sql` in the SQL Editor to generate the tables, Row Level Security (RLS) policies, and the complex RRF Search RPCs.

### 2. The Python Backend
```bash
cd render-backend
python -m venv venv
source venv/bin/activate  # (or venv\Scripts\activate on Windows)
pip install -r requirements.txt
```

Create a `.env` file in the `render-backend` directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
GEMINI_API_KEY=your_google_gemini_api_key
GRAPH_AI_PROVIDER=gemini
ALLOWED_ORIGINS=chrome-extension://<your-extension-id>
```

Start the server:
```bash
uvicorn app.main:app --reload
```
Navigate to `http://localhost:8000/docs` to view the beautiful Scalar API Documentation!

### 3. The Chrome Extension
```bash
cd taskrebuild/extension
npm install
npm run build
```
1. Open Google Chrome and go to `chrome://extensions/`
2. Enable **Developer Mode** in the top right.
3. Click **Load Unpacked** and select the `taskrebuild/extension/dist` directory.

---

## 🗺️ Roadmap & Future Upgrades
- [ ] **Autonomous Web Scraper:** A background worker that downloads, strips, and embeds the full HTML body of saved URLs for deep-quote searching.
- [ ] **Obsidian-Style Graph UI:** A 3D force-directed React graph to visually explore your Task nodes.
- [ ] **GraphRAG Chatbot:** A conversational UI that traverses the Knowledge Graph to answer complex questions about your saved resources.
