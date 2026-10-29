import React, { useState } from 'react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'graph' | 'knowledge' | 'search' | 'monitoring'>('graph');

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
            <li><a href="#interactive-demo">Live Demo</a></li>
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
          <a href="#interactive-demo" className="btn-primary">
            Explore Interactive Demo ↓
          </a>
          <a
            href="https://github.com/mukeshv-tech/Taskrebulid/tree/main/taskrebuild/extension"
            target="_blank"
            rel="noreferrer"
            className="btn-secondary"
          >
            📦 Download Extension
          </a>
        </div>

        {/* Live Interactive Product Showcase */}
        <div id="interactive-demo" className="showcase-wrapper">
          <div className="showcase-header">
            <div className="traffic-dots">
              <span className="dot dot-red" />
              <span className="dot dot-yellow" />
              <span className="dot dot-green" />
            </div>
            <div className="showcase-tabs">
              <button
                className={`showcase-tab ${activeTab === 'graph' ? 'active' : ''}`}
                onClick={() => setActiveTab('graph')}
              >
                🕸️ Knowledge Graph
              </button>
              <button
                className={`showcase-tab ${activeTab === 'knowledge' ? 'active' : ''}`}
                onClick={() => setActiveTab('knowledge')}
              >
                🧠 Personal Knowledge
              </button>
              <button
                className={`showcase-tab ${activeTab === 'search' ? 'active' : ''}`}
                onClick={() => setActiveTab('search')}
              >
                🔍 Hybrid Vector Search
              </button>
              <button
                className={`showcase-tab ${activeTab === 'monitoring' ? 'active' : ''}`}
                onClick={() => setActiveTab('monitoring')}
              >
                🛡️ Link Health Monitor
              </button>
            </div>
          </div>

          <div className="showcase-content">
            {activeTab === 'graph' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div>
                    <h3 style={{ color: '#ffffff', fontSize: '16px' }}>Task: Researching Browser Content Scripts</h3>
                    <p style={{ color: '#94a3b8', fontSize: '12px' }}>AI-Synthesized Graph with Nodes, Edges, and Confidence Weights</p>
                  </div>
                  <span style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '4px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600 }}>
                    Gemini 3.1 Pro Low Powered
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginTop: '16px' }}>
                  <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong style={{ color: '#38bdf8', fontSize: '12px' }}>DOM Injection</strong>
                      <span style={{ fontSize: '10px', color: '#10b981' }}>98%</span>
                    </div>
                    <p style={{ fontSize: '11px', color: '#94a3b8', marginTop: '6px' }}>Content scripts execute in isolated worlds but share the document DOM.</p>
                    <div style={{ marginTop: '8px', fontSize: '10px', color: '#6366f1' }}>Connected: Message Passing →</div>
                  </div>

                  <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong style={{ color: '#a855f7', fontSize: '12px' }}>Isolated Worlds</strong>
                      <span style={{ fontSize: '10px', color: '#10b981' }}>94%</span>
                    </div>
                    <p style={{ fontSize: '11px', color: '#94a3b8', marginTop: '6px' }}>Prevents conflicts with webpage JS variables and window prototypes.</p>
                    <div style={{ marginTop: '8px', fontSize: '10px', color: '#6366f1' }}>Relationship: explains → Security</div>
                  </div>

                  <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong style={{ color: '#10b981', fontSize: '12px' }}>Message Passing</strong>
                      <span style={{ fontSize: '10px', color: '#10b981' }}>92%</span>
                    </div>
                    <p style={{ fontSize: '11px', color: '#94a3b8', marginTop: '6px' }}>chrome.runtime.sendMessage communicates asynchronously with background workers.</p>
                    <div style={{ marginTop: '8px', fontSize: '10px', color: '#6366f1' }}>Depends on: Service Worker →</div>
                  </div>
                </div>

                <div style={{ marginTop: '20px', padding: '12px', background: 'rgba(99, 102, 241, 0.08)', borderRadius: '8px', border: '1px solid rgba(99, 102, 241, 0.2)', fontSize: '12px', color: '#cbd5e1' }}>
                  📚 <strong>Auto-Documentation:</strong> Automatically converts the above relationship graph into structured Markdown learning paths with ordered prerequisites.
                </div>
              </div>
            )}

            {activeTab === 'knowledge' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div>
                    <h3 style={{ color: '#ffffff', fontSize: '16px' }}>Personal Knowledge Base (Phase 9)</h3>
                    <p style={{ color: '#94a3b8', fontSize: '12px' }}>Persistent, cross-task knowledge with provenance tracking</p>
                  </div>
                  <span style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', padding: '4px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600 }}>
                    RLS Isolated • Private
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h4 style={{ color: '#38bdf8', fontSize: '13px' }}>Prior Art in Software Patents</h4>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <span style={{ background: '#1e293b', color: '#cbd5e1', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>concept</span>
                        <span style={{ background: '#4c1d95', color: '#ddd6fe', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>AI Approved</span>
                      </div>
                    </div>
                    <p style={{ fontSize: '12px', color: '#cbd5e1', margin: '8px 0' }}>
                      Prior art consists of all information made available to the public before a patent filing. Evaluates novelty and non-obviousness under 35 U.S.C. 103.
                    </p>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>
                      📍 <strong>Sources:</strong> Task: Patent Research • Resource: USPTO MPEP Manual
                      <br />
                      🔗 <strong>Backlinks:</strong> Used in <em>AI Search Project</em> and <em>Semantic Patent Research</em>
                    </div>
                  </div>

                  <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h4 style={{ color: '#38bdf8', fontSize: '13px' }}>Vector Embeddings with RRF Fusion</h4>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <span style={{ background: '#1e293b', color: '#cbd5e1', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>insight</span>
                        <span style={{ background: '#065f46', color: '#a7f3d0', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>User Created</span>
                      </div>
                    </div>
                    <p style={{ fontSize: '12px', color: '#cbd5e1', margin: '8px 0' }}>
                      Combining Reciprocal Rank Fusion with 3072-dim embeddings overcomes keyword sparsity without sacrificing exact lexical precision.
                    </p>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>
                      📍 <strong>Sources:</strong> Task: Search Engine Upgrade
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'search' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div>
                    <h3 style={{ color: '#ffffff', fontSize: '16px' }}>3072-Dimensional Reciprocal Rank Fusion (Phase 8)</h3>
                    <p style={{ color: '#94a3b8', fontSize: '12px' }}>Combines PostgreSQL Trigrams, Full-Text, and Gemini Vector Embeddings</p>
                  </div>
                  <span style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#a5b4fc', padding: '4px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600 }}>
                    HNSW Vector Indexing
                  </span>
                </div>

                <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '10px 14px', display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                  <span style={{ color: '#38bdf8' }}>🔍</span>
                  <input
                    type="text"
                    readOnly
                    value="how do browser isolated worlds protect javascript globals?"
                    style={{ background: 'transparent', border: 'none', color: '#f8fafc', width: '100%', outline: 'none', fontSize: '13px', fontFamily: 'var(--font-mono)' }}
                  />
                  <span style={{ background: '#6366f1', color: 'white', padding: '3px 8px', borderRadius: '4px', fontSize: '11px' }}>RRF Search</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ background: '#090d1a', border: '1px solid #1e293b', borderRadius: '6px', padding: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong style={{ color: '#38bdf8', fontSize: '12px' }}>MDN: Isolated Worlds in Browser Extensions</strong>
                      <span style={{ color: '#10b981', fontSize: '11px' }}>Score: 0.94 (Semantic Match)</span>
                    </div>
                    <p style={{ color: '#94a3b8', fontSize: '11px', marginTop: '4px' }}>
                      An isolated world is a private execution environment that is not accessible to the page or other extensions...
                    </p>
                  </div>
                  <div style={{ background: '#090d1a', border: '1px solid #1e293b', borderRadius: '6px', padding: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong style={{ color: '#38bdf8', fontSize: '12px' }}>Knowledge: Content Script Security Architecture</strong>
                      <span style={{ color: '#10b981', fontSize: '11px' }}>Score: 0.89 (Personal Knowledge)</span>
                    </div>
                    <p style={{ color: '#94a3b8', fontSize: '11px', marginTop: '4px' }}>
                      Prevents webpage malicious scripts from overriding Window methods or accessing extension storage tokens...
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'monitoring' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div>
                    <h3 style={{ color: '#ffffff', fontSize: '16px' }}>Resource Health & Automated Recovery (Phase 7)</h3>
                    <p style={{ color: '#94a3b8', fontSize: '12px' }}>Continuously checks URLs for HTTP 404s, SSL expiry, or content drift</p>
                  </div>
                  <span style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', padding: '4px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600 }}>
                    Self-Healing Workspaces
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ color: '#ef4444' }}>● HTTP 404 Not Found</span>
                        <strong style={{ color: '#f8fafc', fontSize: '12px' }}>developer.chrome.com/docs/extensions/mv2</strong>
                      </div>
                      <p style={{ fontSize: '11px', color: '#94a3b8', marginTop: '4px' }}>
                        Broken link detected in task "Manifest V3 Migration".
                      </p>
                    </div>
                    <button style={{ background: '#10b981', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '6px', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}>
                      Auto-Replace with MV3 Guide ↗
                    </button>
                  </div>

                  <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ color: '#10b981' }}>● HTTP 200 OK</span>
                        <strong style={{ color: '#f8fafc', fontSize: '12px' }}>fastapi.tiangolo.com/tutorial/security</strong>
                      </div>
                      <p style={{ fontSize: '11px', color: '#94a3b8', marginTop: '4px' }}>
                        Last checked: 2 minutes ago • Content checksum valid.
                      </p>
                    </div>
                    <span style={{ color: '#64748b', fontSize: '11px' }}>Monitored</span>
                  </div>
                </div>
              </div>
            )}
          </div>
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
