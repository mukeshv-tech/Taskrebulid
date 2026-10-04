# 🧠 TaskRebuild

**TaskRebuild** is an intelligent, **task-aware extension project** designed to act as your automatic "Second Brain." By combining a React-powered Chrome Extension with a massively scalable Python/PostgreSQL backend, it creates a next-generation, context-aware productivity workspace.

---

## 🤔 What actually is TaskRebuild?

### The Problem: Context Decay
When you research a complex topic or write code, you usually open 50 StackOverflow tabs, save a few disjointed bookmarks, and scribble some notes. If you close your browser and come back a week later, your "context" is entirely gone. You have no idea *why* you saved a specific link or how it connects to the overall problem you were trying to solve. 

### The Solution: An Automatic Second Brain
**TaskRebuild** completely solves this by tracking your research automatically and mapping it into a visual, searchable graph. 

Whenever you browse the web, the TaskRebuild Chrome Extension silently observes your active tabs and ties them to a specific **Task** (e.g., "Fix Authentication Bug"). Behind the scenes, the Python backend uses Google's **Gemini AI** to read what you are looking at, understand the content, and map out exactly how your web searches connect to your final solutions. 

When you need to find something months later, you don't just search for a keyword—you talk to a 3072-dimension semantic search engine that instantly pulls up the exact paragraph you read 6 months ago, highlighting the exact sentence you need.

---

## ✨ Core Technical Engines

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
