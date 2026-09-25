import codecs
import re

path = 'render-backend/app/routes/graph.py'
code = codecs.open(path, 'r', 'utf-8').read()

# We need to change the analyze_task_graph return statement
new_return = """
    # Save to graph
    save_ai_graph(task_id, user.id, [n.model_dump() for n in result.nodes], [e.model_dump() for e in result.edges])
    
    provider_name = type(ai_service.providers.get(settings.GRAPH_AI_PROVIDER, ai_service.placeholder)).__name__
    
    return {
        "status": "success",
        "provider_used": provider_name,
        "nodes_extracted": len(result.nodes),
        "edges_extracted": len(result.edges)
    }
"""

code = re.sub(
    r'# Save to graph\s+save_ai_graph\(.*?\)\s+return \{"status": "success"\}',
    new_return.strip(),
    code,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
