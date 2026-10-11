import json
from app.supabase import get_supabase
from app.config import settings
from typing import List, Dict, Any

# Configure Gemini
if settings.GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)

async def generate_clusters_for_task(task_id: str, user_id: str) -> List[Dict[str, Any]]:
    """
    Analyzes the knowledge graph (nodes and edges) for a task and groups
    nodes (sub-tasks and entities) into meaningful clusters.
    """
    supabase = get_supabase()
    
    # 1. Fetch the graph data
    nodes_res = supabase.table("task_nodes").select("*").eq("task_id", task_id).execute()
    edges_res = supabase.table("task_edges").select("*").eq("task_id", task_id).execute()
    
    nodes = nodes_res.data or []
    edges = edges_res.data or []
    
    # If no nodes exist yet, attempt to auto-extract graph from task activity & resources
    if not nodes:
        res_res = supabase.table("task_resources").select("id, url, title").eq("task_id", task_id).limit(30).execute()
        act_res = supabase.table("task_activity").select("id, event_type, url, title, timestamp").eq("task_id", task_id).limit(50).execute()
        
        if res_res.data or act_res.data:
            from app.services.ai.service import ai_service
            from app.services.ai.schemas import AIAnalysisInput, TaskResourceInput, TaskActivityInput
            from app.services.graph_service import save_ai_graph
            
            task_res = supabase.table("tasks").select("name").eq("id", task_id).execute()
            task_name = task_res.data[0]["name"] if task_res.data else "Research Task"
            
            resources = [TaskResourceInput(id=r["id"], url=r["url"], title=r.get("title")) for r in (res_res.data or [])]
            activity = [TaskActivityInput(id=a["id"], event_type=a["event_type"], url=a.get("url"), title=a.get("title"), timestamp=a.get("timestamp")) for a in (act_res.data or [])]
            
            input_data = AIAnalysisInput(
                task_id=task_id,
                task_name=task_name,
                resources=resources,
                activity=activity
            )
            
            graph_result = await ai_service.analyze_graph(input_data)
            save_ai_graph(task_id, user_id, [n.model_dump() for n in graph_result.nodes], [e.model_dump() for e in graph_result.edges])
            
            # Re-fetch nodes and edges
            nodes = supabase.table("task_nodes").select("*").eq("task_id", task_id).execute().data or []
            edges = supabase.table("task_edges").select("*").eq("task_id", task_id).execute().data or []
            
    if not nodes:
        raise ValueError("No graph nodes found to cluster. Please add task activity or resources first to generate a knowledge graph.")
        
    # Prepare the context for the LLM
    node_descriptions = []
    for n in nodes:
        node_descriptions.append(f"- ID: {n['id']} | Type: {n.get('node_type', 'concept')} | Label: {n['label']} | Desc: {n.get('description', '')}")
        
    edge_descriptions = []
    # Map node IDs to labels for better LLM comprehension
    node_map = {n['id']: n['label'] for n in nodes}
    for e in edges:
        source = node_map.get(e['source_node_id'], e['source_node_id'])
        target = node_map.get(e['target_node_id'], e['target_node_id'])
        edge_descriptions.append(f"- {source} [{e.get('relationship_type', 'related_to')}] {target}")
        
    prompt = f"""
    You are an AI tasked with clustering related sub-tasks and concepts from a knowledge graph.
    
    Below is the knowledge graph representing a user's task, including its sub-tasks and related entities (nodes) and their dependencies/relationships (edges).
    
    Your goal is to group the nodes into logical, meaningful clusters based on semantic similarity, dependencies, shared entities, and relationships. 
    Every node should belong to exactly one cluster.
    
    Nodes:
    {chr(10).join(node_descriptions)}
    
    Edges (Relationships):
    {chr(10).join(edge_descriptions)}
    
    Output a JSON array of clusters, adhering strictly to this schema:
    [
      {{
        "label": "Short, descriptive name of the cluster",
        "summary": "1-sentence summary of what this cluster represents",
        "rationale": "Brief explanation of why these nodes are grouped together based on their relationships",
        "node_ids": ["uuid-1", "uuid-2"]
      }}
    ]
    
    Return ONLY valid JSON.
    """
    
    import google.generativeai as genai
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
    model_candidates = ['gemini-3.1-pro-low', settings.GEMINI_MODEL_NAME, 'gemini-1.5-flash', 'gemini-2.0-flash']
    models_to_try = []
    for m in model_candidates:
        if m and m not in models_to_try:
            models_to_try.append(m)
            
    response = None
    last_err = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                break
        except Exception as err:
            last_err = err
            print(f"Clustering with model '{model_name}' failed: {err}. Trying fallback...")
            
    if not response or not response.text:
        raise ValueError(f"Failed to generate clusters from Gemini. Error: {last_err}")
    
    # Parse JSON
    try:
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3]
        elif text.startswith('```'):
            text = text[3:-3]
        clusters_data = json.loads(text.strip())
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        raise ValueError(f"Gemini returned invalid JSON for clusters: {e}")
        
    # 2. Delete existing clusters (dynamic reclustering)
    supabase.table("task_clusters").delete().eq("task_id", task_id).eq("user_id", user_id).execute()
    
    # 3. Save new clusters
    saved_clusters = []
    for c_data in clusters_data:
        cluster_insert = {
            "task_id": task_id,
            "user_id": user_id,
            "label": c_data["label"],
            "summary": c_data.get("summary", ""),
            "rationale": c_data.get("rationale", "")
        }
        c_res = supabase.table("task_clusters").insert(cluster_insert).execute()
        
        if c_res.data:
            cluster_row = c_res.data[0]
            cluster_id = cluster_row['id']
            
            node_ids = c_data.get("node_ids", [])
            members_insert = [{"cluster_id": cluster_id, "node_id": n_id} for n_id in node_ids]
            if members_insert:
                supabase.table("task_cluster_members").insert(members_insert).execute()
                
            cluster_row["cluster_name"] = cluster_row.get("label", "")
            cluster_row["node_ids"] = node_ids
            cluster_row["members"] = [{"node_id": n_id, "task_nodes": {"label": node_map.get(n_id, ""), "node_type": "concept"}} for n_id in node_ids]
            saved_clusters.append(cluster_row)
                
    return saved_clusters

def get_task_clusters(task_id: str, user_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    clusters = supabase.table("task_clusters").select("*").eq("task_id", task_id).eq("user_id", user_id).execute().data or []
    
    # Fetch members for each cluster
    for c in clusters:
        members = supabase.table("task_cluster_members").select("node_id, task_nodes(label, node_type)").eq("cluster_id", c['id']).execute().data or []
        c['members'] = members
        c['node_ids'] = [m['node_id'] for m in members if 'node_id' in m]
        c['cluster_name'] = c.get('label', '')
        
    return clusters
