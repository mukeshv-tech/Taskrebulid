# Personal Knowledge System (Phase 9)

## 1. Overview
The Personal Knowledge System separates temporary, project-specific task workflows from persistent, reusable personal knowledge. While tasks, browser activity, and research sessions are transient, personal knowledge captures distilled insights, topics, questions, concepts, and notes that remain private to the user and can be linked across projects.

## 2. Controlled Knowledge Types
Knowledge items are strictly categorized into controlled types to prevent arbitrary AI-generated categories:
- `concept`: Core foundational idea or theory (e.g. *Prior art in software patents*).
- `topic`: Broad subject area (e.g. *Browser extension architecture*).
- `question`: Open question or line of inquiry requiring further study.
- `insight`: Novel observation or conclusion derived from analysis.
- `note`: Freeform user observation or reference.
- `resource`: Canonical link or permanent document reference.

## 3. Relationships & Edges
Knowledge items can be connected to other knowledge items using controlled relationship types:
- `related_to`
- `supports`
- `contradicts`
- `depends_on`
- `explains`
- `derived_from`

**Integrity Constraints**:
- Self-relationships (`source == target`) are strictly prevented.
- Duplicate relationships are blocked via a unique constraint `(user_id, source_knowledge_id, target_knowledge_id, relationship_type)`.
- Cross-user relationships are blocked at both database RLS and application layers.

## 4. Sources & Provenance (Traceability)
Every knowledge item records where it came from via `knowledge_sources`:
- Source types supported: `task`, `resource`, `activity`, `ai_analysis`, `snapshot`, `other`.
- Preserves the originating task and resources so the user can always see why and where a piece of knowledge originated.

## 5. Provenance & Confidence
- **Origin**: Marked as either `user` (manually created) or `ai_approved` (suggested by AI and explicitly approved by the user).
- **Confidence**: AI suggestions display confidence as a metric for user review, never as factual certainty. The user must approve or reject suggestions.

## 6. Duplicate Detection
Before creating new knowledge, duplicate detection checks:
1. Exact match (case-insensitive title comparison).
2. Normalized title match (punctuation stripped, normalized whitespace).
If a similar item exists, the user is alerted with links to the existing knowledge item and the option to view or proceed.

## 7. Privacy & Row Level Security (RLS)
- Private by default: knowledge items belong strictly to the authenticated `user_id`.
- Supabase Row Level Security (RLS) is enabled on `knowledge_items`, `knowledge_sources`, and `knowledge_edges` for SELECT, INSERT, UPDATE, and DELETE.
- Cross-user access is impossible.

## 8. API Reference
- `POST /api/knowledge`: Create a knowledge item.
- `GET /api/knowledge`: List personal knowledge (supports `type`, `status`, `task_id`, `source_id`, `limit`, `offset`).
- `GET /api/knowledge/{id}`: Detailed view including sources, relationships, and backlinks.
- `PATCH /api/knowledge/{id}`: Edit title, type, content, or summary.
- `DELETE /api/knowledge/{id}`: Permanently delete knowledge and linked sources/edges.
- `POST /api/knowledge/{id}/archive`: Archive knowledge without deleting data.
- `POST /api/knowledge/{id}/restore`: Restore archived knowledge.
- `POST /api/knowledge/check-duplicate`: Check for duplicate titles.
- `POST /api/knowledge/{id}/relationships`: Add a relationship edge.
- `DELETE /api/knowledge/{id}/relationships/{rel_id}`: Remove a relationship edge.
- `POST /api/tasks/{task_id}/knowledge/suggestions`: Request AI suggestions from task data.
- `POST /api/tasks/{task_id}/knowledge/save-from-task`: Save task summary as knowledge with provenance.
- `POST /api/tasks/{task_id}/knowledge/resources/{resource_id}/save-as-knowledge`: Save a resource as a knowledge item.

## 9. Search & Graph Integration
- Every knowledge item is indexed into `search_documents` (`source_type = 'knowledge'`) with vector embeddings for semantic and hybrid search.
- Knowledge graph traversal enforces limits: `MAX_KNOWLEDGE_DEPTH = 3`, `MAX_KNOWLEDGE_NODES = 50`, `MAX_KNOWLEDGE_EDGES = 100`.
