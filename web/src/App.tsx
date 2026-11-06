import React from 'react';
import { ArchitectureDiagram } from './ArchitectureDiagram';

const SYSTEM_ARCHITECTURE_MERMAID = `flowchart TD

subgraph group_extension["Browser extension"]
  node_capture["Browser capture<br/>[index.ts]"]
  node_background["Background worker<br/>[index.ts]"]
  node_workspace["Task workspace<br/>[App.tsx]"]
  node_feature_views["Research views"]
  node_client["API client<br/>[api.ts]"]
end

subgraph group_api["Backend API"]
  node_api_entry["API application<br/>[main.py]"]
  node_task_routes["Task routes<br/>[tasks.py]"]
  node_activity_routes["Activity routes<br/>[activity.py]"]
  node_search_routes["Search routes<br/>[search.py]"]
  node_knowledge_routes["Knowledge routes<br/>[knowledge.py]"]
  node_graph_routes["Graph routes<br/>[graph.py]"]
  node_other_routes["Product routes"]
  node_auth["User authentication<br/>[auth.py]"]
end

subgraph group_domain["Research services"]
  node_activity_service["Activity tracking"]
  node_search["Hybrid search<br/>[search_indexer.py]"]
  node_knowledge["Personal knowledge"]
  node_graph["Research graph<br/>[graph_service.py]"]
  node_clusters["Research clusters<br/>[cluster_service.py]"]
  node_resource_monitor["System monitoring"]
  node_cron_monitor["Link health worker<br/>[cron_monitor.py]"]
end

subgraph group_platform["AI and persistence"]
  node_ai["AI orchestration<br/>[service.py]"]
  node_providers["AI providers<br/>[gemini_provider.py]"]
  node_groq["Groq provider<br/>[groq_provider.py]"]
  node_database[("Supabase database<br/>[supabase.py]")]
end

node_researcher(("Researcher"))
node_website["Project website<br/>[App.tsx]"]

node_researcher -->|"browses"| node_capture
node_researcher -->|"uses"| node_workspace
node_capture -.->|"reports activity"| node_background
node_background -->|"calls"| node_client
node_workspace -->|"requests data"| node_client
node_workspace -->|"renders"| node_feature_views
node_feature_views -->|"loads features"| node_client
node_feature_views -->|"loads metrics"| node_client
node_client -->|"HTTP requests"| node_api_entry
node_api_entry -->|"registers"| node_task_routes
node_api_entry -->|"registers"| node_activity_routes
node_api_entry -->|"registers"| node_search_routes
node_api_entry -->|"registers"| node_knowledge_routes
node_api_entry -->|"registers"| node_graph_routes
node_api_entry -->|"registers"| node_other_routes
node_task_routes -->|"authenticates"| node_auth
node_activity_routes -->|"delegates"| node_activity_service
node_activity_routes -->|"indexes activity"| node_search
node_search_routes -->|"delegates"| node_search
node_knowledge_routes -->|"delegates"| node_knowledge
node_knowledge_routes -->|"requests suggestions"| node_ai
node_graph_routes -.->|"handles graph"| node_graph
node_other_routes -.->|"serves clustering"| node_clusters
node_other_routes -.->|"serves metrics"| node_resource_monitor
node_api_entry -->|"starts worker"| node_cron_monitor
node_ai -->|"dispatches"| node_providers
node_ai -->|"dispatches"| node_groq
node_task_routes -->|"reads and writes"| node_database
node_auth -->|"validates token"| node_database
node_activity_service -->|"stores activity"| node_database
node_search -->|"indexes and searches"| node_database
node_knowledge -->|"stores knowledge"| node_database
node_graph -->|"stores graph"| node_database
node_clusters -->|"reads research"| node_database
node_website -.->|"explains product"| node_researcher

click node_capture "https://github.com/mukeshv-tech/taskrebulid/blob/main/taskrebuild/extension/src/content/index.ts"
click node_background "https://github.com/mukeshv-tech/taskrebulid/blob/main/taskrebuild/extension/src/background/index.ts"
click node_workspace "https://github.com/mukeshv-tech/taskrebulid/blob/main/taskrebuild/extension/src/popup/App.tsx"
click node_feature_views "https://github.com/mukeshv-tech/taskrebulid/tree/main/taskrebuild/extension/src/popup/components"
click node_client "https://github.com/mukeshv-tech/taskrebulid/blob/main/taskrebuild/extension/src/lib/api.ts"
click node_api_entry "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/main.py"
click node_task_routes "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/routes/tasks.py"
click node_activity_routes "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/routes/activity.py"
click node_search_routes "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/routes/search.py"
click node_knowledge_routes "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/routes/knowledge.py"
click node_graph_routes "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/routes/graph.py"
click node_other_routes "https://github.com/mukeshv-tech/taskrebulid/tree/main/render-backend/app/routes"
click node_auth "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/auth.py"
click node_activity_service "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/activity_service.py"
click node_search "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/search_indexer.py"
click node_knowledge "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/knowledge_service.py"
click node_graph "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/graph_service.py"
click node_clusters "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/cluster_service.py"
click node_resource_monitor "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/resource_monitor.py"
click node_cron_monitor "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/cron_monitor.py"
click node_ai "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/ai/service.py"
click node_providers "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/ai/gemini_provider.py"
click node_groq "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/services/ai/groq_provider.py"
click node_database "https://github.com/mukeshv-tech/taskrebulid/blob/main/render-backend/app/supabase.py"
click node_website "https://github.com/mukeshv-tech/taskrebulid/blob/main/web/src/App.tsx"

classDef toneNeutral fill:#0e1326,stroke:#334155,stroke-width:1.5px,color:#f8fafc
classDef toneBlue fill:#0c2340,stroke:#38bdf8,stroke-width:1.5px,color:#e0f2fe
classDef toneAmber fill:#2d1b06,stroke:#f59e0b,stroke-width:1.5px,color:#fef3c7
classDef toneMint fill:#062817,stroke:#10b981,stroke-width:1.5px,color:#dcfce7
classDef toneRose fill:#350a18,stroke:#f43f5e,stroke-width:1.5px,color:#ffe4e6
classDef toneIndigo fill:#19183b,stroke:#818cf8,stroke-width:1.5px,color:#e0e7ff
classDef toneTeal fill:#062624,stroke:#14b8a6,stroke-width:1.5px,color:#ccfbf1

class node_capture,node_background,node_workspace,node_feature_views,node_client toneBlue
class node_api_entry,node_task_routes,node_activity_routes,node_search_routes,node_knowledge_routes,node_graph_routes,node_other_routes,node_auth toneAmber
class node_activity_service,node_search,node_knowledge,node_graph,node_clusters,node_resource_monitor,node_cron_monitor toneMint
class node_ai,node_providers,node_groq,node_database toneRose
class node_researcher toneIndigo
class node_website toneTeal
`;

export const App: React.FC = () => {
  return (
    <>
      <div className="ambient-glow" />
      <div className="ambient-glow-bottom" />

      {/* Navigation */}
      <header className="container">
        <nav className="navbar">
          <div className="logo">
            <span>TaskRebuild</span>
            <span className="logo-badge">v2.0</span>
          </div>
          <ul className="nav-links">
            <li><a href="#features">Features</a></li>
            <li><a href="#architecture">Architecture</a></li>
            <li><a href="https://taskrebulid.onrender.com/docs" target="_blank" rel="noreferrer">API docs</a></li>
            <li>
              <a
                href="https://github.com/mukeshv-tech/Taskrebulid"
                target="_blank"
                rel="noreferrer"
                className="btn-secondary"
              >
                GitHub
              </a>
            </li>
          </ul>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container hero">
        <div className="hero-tag">
          Research tracker and note library
        </div>
        <h1>
          Save browser research to a <br />
          searchable <span>node graph</span>
        </h1>
        <p>
          TaskRebuild logs open tabs by task, groups related links, builds relationship graphs, and keeps notes queryable after you close the browser.
        </p>

        <div className="hero-actions">
          <a
            href="https://github.com/mukeshv-tech/Taskrebulid/tree/main/taskrebuild/extension"
            target="_blank"
            rel="noreferrer"
            className="btn-primary"
          >
            Install extension
          </a>
          <a
            href="https://taskrebulid.onrender.com/docs"
            target="_blank"
            rel="noreferrer"
            className="btn-secondary"
          >
            API docs
          </a>
        </div>
      </section>

      {/* Feature Grid */}
      <section id="features" className="container features-section">
        <div className="section-title">
          <h2>Features</h2>
          <p>Tools to collect, index, and query web research.</p>
        </div>

        <div className="feature-grid">
          <div className="feature-card">
            <h3>Notes</h3>
            <p>Save notes and page excerpts tied to your active task.</p>
          </div>

          <div className="feature-card">
            <h3>Graph</h3>
            <p>Map tasks, pages, and concepts into nodes and edges using Gemini 3.1 Pro.</p>
          </div>

          <div className="feature-card">
            <h3>Hybrid search</h3>
            <p>Combines 3,072-dimension pgvector embeddings with PostgreSQL trigram search via reciprocal rank fusion.</p>
          </div>

          <div className="feature-card">
            <h3>Markdown paths</h3>
            <p>Exports graph relationships as ordered Markdown files with prerequisites.</p>
          </div>

          <div className="feature-card">
            <h3>URL health check</h3>
            <p>Runs scheduled checks on saved links for 404 responses and TLS errors.</p>
          </div>

          <div className="feature-card">
            <h3>Per-user isolation</h3>
            <p>PostgreSQL row-level security scopes all table queries to your Supabase auth id.</p>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="architecture-section">
        <div className="container">
          <div className="section-title">
            <h2>Architecture</h2>
            <p>Data moves from the browser extension to FastAPI, then persists in PostgreSQL.</p>
          </div>

          <div className="arch-boxes">
            <div className="arch-box">
              <h4>Browser extension</h4>
              <p>React 18 interface with background service worker tab listeners.</p>
            </div>

            <div className="arch-arrow">→</div>

            <div className="arch-box">
              <h4>FastAPI service</h4>
              <p>Async API for search indexing, graph generation, and AI routing.</p>
            </div>

            <div className="arch-arrow">→</div>

            <div className="arch-box">
              <h4>PostgreSQL</h4>
              <p>Supabase database with pgvector, trigrams, and row-level security.</p>
            </div>
          </div>

          <ArchitectureDiagram chartDefinition={SYSTEM_ARCHITECTURE_MERMAID} />
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="container">
          <p>© 2026 TaskRebuild. MIT License.</p>
          <p style={{ marginTop: '6px' }}>
            Built with React, FastAPI, Supabase, and Gemini. Hosted on <a href="https://taskrebulid.onrender.com/docs" target="_blank" rel="noreferrer">Render</a>.
          </p>
        </div>
      </footer>
    </>
  );
};

export default App;
