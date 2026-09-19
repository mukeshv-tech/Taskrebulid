from app.supabase import get_supabase
from typing import List, Dict, Any

def get_task_graph(task_id: str, user_id: str) -> Dict[str, Any]:
    supabase = get_supabase()
    
    # Verify task ownership
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
        
    nodes = supabase.table("task_nodes").select("*").eq("task_id", task_id).execute()
    edges = supabase.table("task_edges").select("*").eq("task_id", task_id).execute()
    
    return {
        "nodes": nodes.data,
        "edges": edges.data
    }

def delete_node(task_id: str, node_id: str, user_id: str):
    supabase = get_supabase()
    # Verify task ownership
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
    supabase.table("task_nodes").delete().eq("id", node_id).eq("task_id", task_id).eq("user_id", user_id).execute()

def delete_edge(task_id: str, edge_id: str, user_id: str):
    supabase = get_supabase()
    # Verify task ownership
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
    supabase.table("task_edges").delete().eq("id", edge_id).eq("task_id", task_id).eq("user_id", user_id).execute()

def reject_edge(task_id: str, edge_id: str, user_id: str):
    supabase = get_supabase()
    # Verify task ownership
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
    supabase.table("task_edges").update({"is_rejected": True}).eq("id", edge_id).eq("task_id", task_id).eq("user_id", user_id).execute()

def save_ai_graph(task_id: str, user_id: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
    supabase = get_supabase()
    
    # Get existing nodes and edges
    existing_nodes = supabase.table("task_nodes").select("*").eq("task_id", task_id).execute().data
    existing_edges = supabase.table("task_edges").select("*").eq("task_id", task_id).execute().data
    
    node_map = {n['label'].lower(): n for n in existing_nodes}
    
    # Process Nodes
    saved_nodes = {}
    for node in nodes:
        label_lower = node['label'].lower()
        if label_lower in node_map:
            # Update confidence/description if needed, or just keep it
            db_node = node_map[label_lower]
            saved_nodes[node['label']] = db_node['id'] # map exact original label to ID just in case
            saved_nodes[label_lower] = db_node['id']
            # update confidence if AI generated? Maybe keep existing if higher or just leave it alone
        else:
            # Insert new node
            new_node = {
                "task_id": task_id,
                "user_id": user_id,
                "node_type": node.get('node_type', 'concept'),
                "label": node['label'],
                "description": node.get('description'),
                "is_ai_generated": True,
                "confidence": node.get('confidence', 0.5)
            }
            res = supabase.table("task_nodes").insert(new_node).execute()
            if res.data:
                node_id = res.data[0]['id']
                saved_nodes[node['label']] = node_id
                saved_nodes[label_lower] = node_id
                node_map[label_lower] = res.data[0]
                
    # Process Edges
    edge_map = {(e['source_node_id'], e['target_node_id'], e['relationship_type']): e for e in existing_edges}
    
    for edge in edges:
        source_label_lower = edge['source_label'].lower()
        target_label_lower = edge['target_label'].lower()
        
        source_id = saved_nodes.get(source_label_lower)
        target_id = saved_nodes.get(target_label_lower)
        
        if not source_id or not target_id:
            continue
            
        key = (source_id, target_id, edge['relationship_type'])
        
        if key in edge_map:
            existing_edge = edge_map[key]
            if existing_edge['is_rejected']:
                continue # Do not recreate/un-reject rejected edges
            
            # Update confidence and evidence if existing edge is AI generated
            if existing_edge['is_ai_generated']:
                supabase.table("task_edges").update({
                    "confidence": edge.get('confidence', existing_edge['confidence']),
                    "evidence": edge.get('evidence', existing_edge['evidence'])
                }).eq("id", existing_edge['id']).execute()
        else:
            # Prevent self-referential
            if source_id == target_id:
                continue
                
            new_edge = {
                "task_id": task_id,
                "user_id": user_id,
                "source_node_id": source_id,
                "target_node_id": target_id,
                "relationship_type": edge['relationship_type'],
                "is_ai_generated": True,
                "confidence": edge.get('confidence', 0.5),
                "evidence": edge.get('evidence', [])
            }
            supabase.table("task_edges").insert(new_edge).execute()
