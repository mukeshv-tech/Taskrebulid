import React from 'react';

export const App: React.FC = () => {
  return (
    <>
      <div className="ambient-glow" />
      <div className="ambient-glow-bottom" />

      {/* Navigation */}
      <header className="container">
        <nav className="navbar">
          <div className="logo">
            <span>🧠 TaskRebuild</span>
            <span className="logo-badge">v2.0 • Phase 9</span>
          </div>
          <ul className="nav-links">
            <li><a href="#features">Features</a></li>
            <li><a href="#architecture">Architecture</a></li>
            <li><a href="https://taskrebulid.onrender.com/docs" target="_blank" rel="noreferrer">API Docs</a></li>
            <li>
              <a
                href="https://github.com/mukeshv-tech/Taskrebulid"
                target="_blank"
                rel="noreferrer"
                className="btn-secondary"
              >
                GitHub Repo ↗
              </a>
            </li>
          </ul>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container hero">
        <div className="hero-tag">
          ✨ Turn Transient Browsing Into Persistent Personal Knowledge
        </div>
        <h1>
          The Knowledge Operating System <br />
          for Your <span>Browser Research</span>
        </h1>
        <p>
          TaskRebuild tracks active tasks, clusters sub-task research, synthesizes knowledge graphs with Gemini AI, and preserves provenanced personal knowledge that never disappears when you close a tab.
        </p>

        <div className="hero-actions">
          <a
            href="https://github.com/mukeshv-tech/Taskrebulid/tree/main/taskrebuild/extension"
            target="_blank"
            rel="noreferrer"
            className="btn-primary"
          >
            📦 Download Chrome Extension
          </a>
          <a
            href="https://taskrebulid.onrender.com/docs"
            target="_blank"
            rel="noreferrer"
            className="btn-secondary"
          >
            Explore API Docs ↗
          </a>
        </div>
      </section>

      {/* Feature Grid */}
      <section id="features" className="container features-section">
        <div className="section-title">
          <h2>Engineered for Deep Research</h2>
          <p>TaskRebuild bridges the gap between scattered browser tabs and reusable intelligence.</p>
        </div>

        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3>Personal Knowledge System</h3>
            <p>Turn transient browser tabs and AI summaries into reusable concepts, notes, and topics. Preserves provenance and links across projects.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🕸️</div>
            <h3>Dynamic Knowledge Graph</h3>
            <p>Automatically maps tasks, visited pages, and extracted concepts into a connected node-edge network powered by Gemini 3.1 Pro.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>3072-Dim RRF Search</h3>
            <p>Hybrid semantic and full-text search combining PostgreSQL pgvector and trigrams via Reciprocal Rank Fusion.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3>Auto-Documentation</h3>
            <p>Transforms raw research graph nodes and edges into structured, sequenced Markdown learning paths with prerequisite mappings.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🛡️</div>
            <h3>Self-Healing Workspaces</h3>
            <p>Automated cron worker monitors dead links, 404s, and SSL failures, using AI to suggest replacement references.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3>Strict Privacy & RLS</h3>
            <p>All data is bound to your authenticated Supabase identity. Database-level Row Level Security guarantees complete isolation.</p>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="architecture-section">
        <div className="container">
          <div className="section-title">
            <h2>Three-Tier Scalable Architecture</h2>
            <p>From client-side Chrome storage to asynchronous FastAPI workers and Supabase pgvector.</p>
          </div>

          <div className="arch-boxes">
            <div className="arch-box">
              <h4>Chrome Extension (Vite)</h4>
              <p>React 18 + TypeScript popup, live tab listener, background service worker & local storage sync.</p>
            </div>

            <div className="arch-arrow">→</div>

            <div className="arch-box">
              <h4>Render FastAPI Backend</h4>
              <p>Python 3.14 async API, Gemini 3.1 Pro Low & Groq fallbacks, and task clustering engines.</p>
            </div>

            <div className="arch-arrow">→</div>

            <div className="arch-box">
              <h4>Supabase PostgreSQL</h4>
              <p>pgvector (3072-dim), Row Level Security (RLS), Trigrams, and HNSW cosine similarity search.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="container">
          <p>© 2026 TaskRebuild. Open source under the MIT License.</p>
          <p style={{ marginTop: '6px' }}>
            Built with React, FastAPI, Supabase, and Gemini AI. Hosted on <a href="https://taskrebulid.onrender.com/docs" target="_blank" rel="noreferrer">Render</a>.
          </p>
        </div>
      </footer>
    </>
  );
};

export default App;
