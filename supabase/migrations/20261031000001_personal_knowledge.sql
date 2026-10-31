-- ==================================================
-- PHASE 9: Personal Knowledge System Migration
-- ==================================================

-- 1. Knowledge Items Table
CREATE TABLE IF NOT EXISTS public.knowledge_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('concept', 'topic', 'question', 'insight', 'note', 'resource')),
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    summary TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    origin TEXT NOT NULL DEFAULT 'user' CHECK (origin IN ('user', 'ai_approved')),
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    archived_at TIMESTAMPTZ
);

-- 2. Knowledge Sources (Provenance & Traceability)
CREATE TABLE IF NOT EXISTS public.knowledge_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    knowledge_id UUID NOT NULL REFERENCES public.knowledge_items(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL CHECK (source_type IN ('task', 'resource', 'activity', 'ai_analysis', 'snapshot', 'other')),
    source_id UUID,
    source_name TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Knowledge Edges (Relationships between knowledge items)
CREATE TABLE IF NOT EXISTS public.knowledge_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    source_knowledge_id UUID NOT NULL REFERENCES public.knowledge_items(id) ON DELETE CASCADE,
    target_knowledge_id UUID NOT NULL REFERENCES public.knowledge_items(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('related_to', 'supports', 'contradicts', 'depends_on', 'explains', 'derived_from')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_no_self_loop CHECK (source_knowledge_id <> target_knowledge_id),
    CONSTRAINT uq_knowledge_relationship UNIQUE (user_id, source_knowledge_id, target_knowledge_id, relationship_type)
);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.knowledge_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_edges ENABLE ROW LEVEL SECURITY;

-- 5. RLS Policies for knowledge_items
DROP POLICY IF EXISTS "Users can view their own knowledge items" ON public.knowledge_items;
CREATE POLICY "Users can view their own knowledge items"
    ON public.knowledge_items FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own knowledge items" ON public.knowledge_items;
CREATE POLICY "Users can insert their own knowledge items"
    ON public.knowledge_items FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own knowledge items" ON public.knowledge_items;
CREATE POLICY "Users can update their own knowledge items"
    ON public.knowledge_items FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own knowledge items" ON public.knowledge_items;
CREATE POLICY "Users can delete their own knowledge items"
    ON public.knowledge_items FOR DELETE
    USING (auth.uid() = user_id);

-- 6. RLS Policies for knowledge_sources
DROP POLICY IF EXISTS "Users can view their own knowledge sources" ON public.knowledge_sources;
CREATE POLICY "Users can view their own knowledge sources"
    ON public.knowledge_sources FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own knowledge sources" ON public.knowledge_sources;
CREATE POLICY "Users can insert their own knowledge sources"
    ON public.knowledge_sources FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own knowledge sources" ON public.knowledge_sources;
CREATE POLICY "Users can delete their own knowledge sources"
    ON public.knowledge_sources FOR DELETE
    USING (auth.uid() = user_id);

-- 7. RLS Policies for knowledge_edges
DROP POLICY IF EXISTS "Users can view their own knowledge edges" ON public.knowledge_edges;
CREATE POLICY "Users can view their own knowledge edges"
    ON public.knowledge_edges FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own knowledge edges" ON public.knowledge_edges;
CREATE POLICY "Users can insert their own knowledge edges"
    ON public.knowledge_edges FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own knowledge edges" ON public.knowledge_edges;
CREATE POLICY "Users can delete their own knowledge edges"
    ON public.knowledge_edges FOR DELETE
    USING (auth.uid() = user_id);

-- 8. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_items_user_status ON public.knowledge_items(user_id, status);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_user_type ON public.knowledge_items(user_id, type);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_user_created ON public.knowledge_items(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_knowledge ON public.knowledge_sources(knowledge_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_source ON public.knowledge_sources(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_user ON public.knowledge_sources(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_source ON public.knowledge_edges(source_knowledge_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_target ON public.knowledge_edges(target_knowledge_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_user ON public.knowledge_edges(user_id);
