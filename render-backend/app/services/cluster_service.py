import json
from app.supabase import get_supabase
from app.config import settings
from typing import List, Dict, Any

# Configure Gemini
if settings.GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_clusters_for_task(task_id: str, user_id: str) -> List[Dict[str, Any]]:
    """
    Analyzes the knowledge graph (nodes and edges) for a task and groups
    nodes (sub-tasks and entities) into meaningful clusters.
    """
    supabase = get_supabase()
    
    # 1. Fetch the graph data
    nodes_res = supabase.table("task_nodes").select("*").eq("task_id", task_id).eq("user_id", user_id).execute()
    edges_res = supabase.table("task_edges").select("*").eq("task_id", task_id).eq("user_id", user_id).execute()
    
    nodes = nodes_res.data
    edges = edges_res.data
    
    if not nodes:
        return []
        
    # Prepare the context for the LLM
    node_descriptions = []
    for n in nodes:
        node_descriptions.append(f"- ID: {n['id']} | Type: {n['node_type']} | Label: {n['label']} | Desc: {n.get('description', '')}")
        
    edge_descriptions = []
    # Map node IDs to labels for better LLM comprehension
    node_map = {n['id']: n['label'] for n in nodes}
    for e in edges:
        source = node_map.get(e['source_node_id'], e['source_node_id'])
        target = node_map.get(e['target_node_id'], e['target_node_id'])
        edge_descriptions.append(f"- {source} [{e['relationship_type']}] {target}")
        
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
    model = genai.GenerativeModel('gemini-3.1-pro-low')
    response = model.generate_content(prompt)
    
    # Parse JSON
    try:
        text = response.text
        if text.startswith('```json'):
            text = text[7:-3]
        elif text.startswith('```'):
            text = text[3:-3]
        clusters_data = json.loads(text.strip())
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return []
        
    # 2. Delete existing clusters (dynamic reclustering)
    # The ON DELETE CASCADE on task_cluster_members handles the cleanup of relations
    supabase.table("task_clusters").delete().eq("task_id", task_id).eq("user_id", user_id).execute()
    
    # 3. Save new clusters
    saved_clusters = []
    for c_data in clusters_data:
        # Insert cluster
        cluster_insert = {
            "task_id": task_id,
            "user_id": user_id,
            "label": c_data["label"],
            "summary": c_data.get("summary", ""),
            "rationale": c_data.get("rationale", "")
        }
        c_res = supabase.table("task_clusters").insert(cluster_insert).execute()
        
        if c_res.data:
            cluster_id = c_res.data[0]['id']
            saved_clusters.append(c_res.data[0])
            
            # Insert members
            members_insert = []
            for n_id in c_data.get("node_ids", []):
                members_insert.append({
                    "cluster_id": cluster_id,
                    "node_id": n_id
                })
                
            if members_insert:
                supabase.table("task_cluster_members").insert(members_insert).execute()
                
    return saved_clusters

def get_task_clusters(task_id: str, user_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    clusters = supabase.table("task_clusters").select("*").eq("task_id", task_id).eq("user_id", user_id).execute().data
    
    # Fetch members for each cluster
    for c in clusters:
        members = supabase.table("task_cluster_members").select("node_id, task_nodes(label, node_type)").eq("cluster_id", c['id']).execute().data
        c['members'] = members
        
    return clusters
