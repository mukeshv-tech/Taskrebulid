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
