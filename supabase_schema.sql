create table public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.tasks (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.tasks enable row level security;

create policy "Users can view their own profile"
on public.profiles
for select
using (auth.uid() = id);

create policy "Users can update their own profile"
on public.profiles
for update
using (auth.uid() = id);

create policy "Users can view their own tasks"
on public.tasks
for select
using (auth.uid() = user_id);

create policy "Users can create their own tasks"
on public.tasks
for insert
with check (auth.uid() = user_id);

create policy "Users can update their own tasks"
on public.tasks
for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users can delete their own tasks"
on public.tasks
for delete
using (auth.uid() = user_id);

create table public.task_resources (
    id uuid primary key default gen_random_uuid(),
    task_id uuid not null references public.tasks(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    url text not null,
    title text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.task_resources enable row level security;

create policy "Users can view their own resources"
on public.task_resources
for select
using (auth.uid() = user_id);

create policy "Users can create their own resources"
on public.task_resources
for insert
with check (auth.uid() = user_id);

create policy "Users can update their own resources"
on public.task_resources
for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users can delete their own resources"
on public.task_resources
for delete
using (auth.uid() = user_id);

create table public.task_activity (
    id uuid primary key default gen_random_uuid(),
    task_id uuid not null references public.tasks(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    event_type text not null,
    url text,
    title text,
    tab_id text,
    window_id text,
    timestamp timestamptz not null default now(),
    metadata jsonb
);

alter table public.task_activity enable row level security;

create policy "Users can view their own activity"
on public.task_activity for select using (auth.uid() = user_id);

create policy "Users can insert their own activity"
on public.task_activity for insert with check (auth.uid() = user_id);

create policy "Users can delete their own activity"
on public.task_activity for delete using (auth.uid() = user_id);

create index idx_task_activity_task_id on public.task_activity(task_id);
create index idx_task_activity_user_id on public.task_activity(user_id);
create index idx_task_activity_timestamp on public.task_activity(timestamp desc);

create table public.task_ai_analyses (
    id uuid primary key default gen_random_uuid(),
    task_id uuid not null references public.tasks(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    analysis_type text not null,
    model_name text,
    model_version text,
    input_activity_count integer,
    input_resource_count integer,
    result jsonb not null,
    created_at timestamptz not null default now()
);

alter table public.task_ai_analyses enable row level security;

create policy "Users can view their own AI analyses"
on public.task_ai_analyses for select using (auth.uid() = user_id);

create policy "Users can insert their own AI analyses"
on public.task_ai_analyses for insert with check (auth.uid() = user_id);

create policy "Users can delete their own AI analyses"
on public.task_ai_analyses for delete using (auth.uid() = user_id);

create index idx_task_ai_analyses_task_id on public.task_ai_analyses(task_id);
create index idx_task_ai_analyses_user_id on public.task_ai_analyses(user_id);
create index idx_task_ai_analyses_created_at on public.task_ai_analyses(created_at desc);

-- PHASE 5: Knowledge Graph

create table public.task_nodes (
    id uuid primary key default gen_random_uuid(),
    task_id uuid not null references public.tasks(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    node_type text not null,
    label text not null,
    description text,
    is_ai_generated boolean default false,
    confidence float,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique(task_id, label, node_type)
);

alter table public.task_nodes enable row level security;

create policy "Users can view their own task nodes"
on public.task_nodes for select using (auth.uid() = user_id);

create policy "Users can insert their own task nodes"
on public.task_nodes for insert with check (auth.uid() = user_id);

create policy "Users can update their own task nodes"
on public.task_nodes for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Users can delete their own task nodes"
on public.task_nodes for delete using (auth.uid() = user_id);

create index idx_task_nodes_task_id on public.task_nodes(task_id);
create index idx_task_nodes_user_id on public.task_nodes(user_id);
create index idx_task_nodes_label on public.task_nodes(label);


create table public.task_edges (
    id uuid primary key default gen_random_uuid(),
    task_id uuid not null references public.tasks(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    source_node_id uuid not null references public.task_nodes(id) on delete cascade,
    target_node_id uuid not null references public.task_nodes(id) on delete cascade,
    relationship_type text not null,
    is_ai_generated boolean default false,
    confidence float,
    evidence jsonb,
    is_rejected boolean default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique(task_id, source_node_id, target_node_id, relationship_type)
);

alter table public.task_edges enable row level security;

create policy "Users can view their own task edges"
on public.task_edges for select using (auth.uid() = user_id);

create policy "Users can insert their own task edges"
on public.task_edges for insert with check (auth.uid() = user_id);

create policy "Users can update their own task edges"
on public.task_edges for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Users can delete their own task edges"
on public.task_edges for delete using (auth.uid() = user_id);

create index idx_task_edges_task_id on public.task_edges(task_id);
create index idx_task_edges_user_id on public.task_edges(user_id);
create index idx_task_edges_source on public.task_edges(source_node_id);
create index idx_task_edges_target on public.task_edges(target_node_id);


-- Phase 6: Task Snapshots
CREATE TABLE public.task_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    snapshot_type TEXT NOT NULL,
    summary TEXT,
    state JSONB NOT NULL,
    activity_count INTEGER,
    resource_count INTEGER,
    graph_node_count INTEGER,
    graph_edge_count INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.task_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own task snapshots" ON public.task_snapshots FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own task snapshots" ON public.task_snapshots FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own task snapshots" ON public.task_snapshots FOR DELETE USING (auth.uid() = user_id);

CREATE INDEX idx_task_snapshots_task_id ON public.task_snapshots(task_id);
CREATE INDEX idx_task_snapshots_user_id ON public.task_snapshots(user_id);
CREATE INDEX idx_task_snapshots_task_created ON public.task_snapshots(task_id, created_at DESC);
-- Phase 7: Resource Monitoring
ALTER TABLE public.task_resources ADD COLUMN check_status text;
ALTER TABLE public.task_resources ADD COLUMN content_hash text;
ALTER TABLE public.task_resources ADD COLUMN last_checked_at timestamptz;
ALTER TABLE public.task_resources ADD COLUMN replaced_at timestamptz;
ALTER TABLE public.task_resources ADD COLUMN replaced_by_resource_id uuid REFERENCES public.task_resources(id) ON DELETE SET NULL;

CREATE TABLE public.resource_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_id UUID NOT NULL REFERENCES public.task_resources(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    check_status TEXT NOT NULL,
    change_type TEXT,
    change_severity TEXT,
    content_hash TEXT,
    error_message TEXT,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.resource_checks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own resource checks" ON public.resource_checks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own resource checks" ON public.resource_checks FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own resource checks" ON public.resource_checks FOR DELETE USING (auth.uid() = user_id);

CREATE INDEX idx_resource_checks_resource_id ON public.resource_checks(resource_id);
CREATE INDEX idx_resource_checks_task_id ON public.resource_checks(task_id);
- -   P h a s e   7 :   A u t o m a t e d   C r o n   M o n i t o r i n g  
 A L T E R   T A B L E   p u b l i c . t a s k s   A D D   C O L U M N   a u t o _ m o n i t o r _ e n a b l e d   b o o l e a n   D E F A U L T   f a l s e ;  
 A L T E R   T A B L E   p u b l i c . t a s k _ r e s o u r c e s   A D D   C O L U M N   i s _ i g n o r e d   b o o l e a n   D E F A U L T   f a l s e ;  
 

-- Phase 7: Automated Cron Monitoring
ALTER TABLE public.tasks ADD COLUMN auto_monitor_enabled boolean DEFAULT false;
ALTER TABLE public.task_resources ADD COLUMN is_ignored boolean DEFAULT false;
-- Phase 8: Search & Discovery
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE public.search_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,
    source_id UUID NOT NULL,
    title TEXT,
    content TEXT,
    metadata JSONB,
    embedding vector(3072),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(source_type, source_id)
);

CREATE TABLE public.search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.search_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.search_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own search documents" ON public.search_documents FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own search documents" ON public.search_documents FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own search documents" ON public.search_documents FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own search documents" ON public.search_documents FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own search history" ON public.search_history FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own search history" ON public.search_history FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own search history" ON public.search_history FOR DELETE USING (auth.uid() = user_id);

CREATE INDEX idx_search_documents_user_id ON public.search_documents(user_id);
CREATE INDEX idx_search_documents_task_id ON public.search_documents(task_id);
CREATE INDEX idx_search_documents_embedding ON public.search_documents USING hnsw (embedding vector_cosine_ops);

CREATE OR REPLACE FUNCTION hybrid_search_documents(
    query_embedding vector(3072),
    query_text text,
    match_count int,
    match_threshold float,
    p_user_id uuid
)
RETURNS TABLE (
    id uuid,
    task_id uuid,
    source_type text,
    source_id uuid,
    title text,
    snippet text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.task_id,
        d.source_type,
        d.source_id,
        d.title,
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM search_documents d
    WHERE 
        (d.user_id = p_user_id) AND
        (
            (1 - (d.embedding <=> query_embedding) > match_threshold)
            OR
            (query_text IS NOT NULL AND (d.title ILIKE '%' || query_text || '%' OR d.content ILIKE '%' || query_text || '%'))
        )
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- PHASE 6: Task Clustering

CREATE TABLE public.task_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    summary TEXT,
    rationale TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.task_clusters ENABLE ROW LEVEL SECURITY;

CREATE POLICY ""Users can view their own task clusters""
ON public.task_clusters FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY ""Users can insert their own task clusters""
ON public.task_clusters FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY ""Users can update their own task clusters""
ON public.task_clusters FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY ""Users can delete their own task clusters""
ON public.task_clusters FOR DELETE USING (auth.uid() = user_id);

CREATE INDEX idx_task_clusters_task_id ON public.task_clusters(task_id);
CREATE INDEX idx_task_clusters_user_id ON public.task_clusters(user_id);


CREATE TABLE public.task_cluster_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cluster_id UUID NOT NULL REFERENCES public.task_clusters(id) ON DELETE CASCADE,
    node_id UUID NOT NULL REFERENCES public.task_nodes(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(cluster_id, node_id)
);

ALTER TABLE public.task_cluster_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY ""Users can view their own task cluster members""
ON public.task_cluster_members FOR SELECT 
USING (
    cluster_id IN (SELECT id FROM public.task_clusters WHERE user_id = auth.uid())
);

CREATE POLICY ""Users can insert their own task cluster members""
ON public.task_cluster_members FOR INSERT 
WITH CHECK (
    cluster_id IN (SELECT id FROM public.task_clusters WHERE user_id = auth.uid())
);

CREATE POLICY ""Users can delete their own task cluster members""
ON public.task_cluster_members FOR DELETE 
USING (
    cluster_id IN (SELECT id FROM public.task_clusters WHERE user_id = auth.uid())
);

CREATE INDEX idx_task_cluster_members_cluster_id ON public.task_cluster_members(cluster_id);
CREATE INDEX idx_task_cluster_members_node_id ON public.task_cluster_members(node_id);

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
