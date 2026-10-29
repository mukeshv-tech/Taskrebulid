# TaskRebuild Architecture

## System Overview
TaskRebuild is an intelligent productivity system consisting of:
1. **Chrome Extension (Frontend)**: React, Vite, TypeScript popup with active task tracking, knowledge graph visualizer, clustering, monitoring, auto-documentation, and personal knowledge management.
2. **FastAPI Backend (`render-backend`)**: Python 3.14 API service with Gemini / Groq AI integrations, vector embeddings, and background monitoring.
3. **Database (Supabase PostgreSQL)**: Database with pgvector, Row Level Security (RLS), and reciprocal rank fusion search.

## Complete Phases Architecture
- **Phase 0–3**: User authentication, tasks, resources, and live tab tracking.
- **Phase 4**: Task AI synthesis with prompt fallback chains.
- **Phase 5**: Knowledge graph extraction, node & edge management.
- **Phase 6**: Task workspace resume & state snapshots.
- **Phase 7**: Dead resource monitoring, integrity checks, and auto-replacement.
- **Phase 8**: Hybrid search with 3072-dimensional vector embeddings, text search, and reciprocal rank fusion (RRF).
- **Phase 9 (Personal Knowledge System)**:
  - Persistent, user-controlled knowledge layer independent of transient tasks.
  - Controlled knowledge types (`concept`, `topic`, `question`, `insight`, `note`, `resource`).
  - Controlled relationship types (`related_to`, `supports`, `contradicts`, `depends_on`, `explains`, `derived_from`).
  - Source tracking and provenance (`knowledge_sources`).
  - AI knowledge and relationship suggestions requiring explicit user approval.
  - Duplicate detection before creation.
  - Row Level Security (RLS) ensuring strict cross-user isolation.
  - Backlinks and cross-task reuse mapping.
  - Bounded graph traversal limits (`MAX_KNOWLEDGE_DEPTH = 3`, `MAX_KNOWLEDGE_NODES = 50`, `MAX_KNOWLEDGE_EDGES = 100`).
