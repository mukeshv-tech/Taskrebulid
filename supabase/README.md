# Supabase SQL Schema Directory

This folder contains clean, ordered SQL files ready to copy and run directly in the **Supabase Dashboard SQL Editor**.

## Folder Path
`C:\Users\Mukesh\Taskrebulid\supabase\migrations`

---

## How to Apply via Supabase UI:
1. Log into your [Supabase Dashboard](https://supabase.com/dashboard/project/_).
2. Click on **SQL Editor** in the left sidebar (icon with `>_`).
3. Click **New query**.
4. Open and paste the contents of:
   - `20261031000000_initial_schema.sql` (Creates `profiles`, `tasks`, `task_resources`, `task_activity`, RLS policies & Realtime publications).
   - `20261031000001_personal_knowledge.sql` (Creates `knowledge_items`, `knowledge_edges`, pgvector embeddings, and similarity search functions).
5. Click **Run** (or `Ctrl+Enter`).
