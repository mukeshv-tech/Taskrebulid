import codecs

path = 'render-backend/app/routes/metrics.py'
code = codecs.open(path, 'r', 'utf-8').read()

script_tag = """
    <script>
        function formatUptime(seconds) {
            const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
            const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
            const s = Math.floor(seconds % 60).toString().padStart(2, '0');
            return `${h}:${m}:${s}`;
        }

        async function fetchMetrics() {
            try {
                const response = await fetch('/api/metrics', {
                    headers: { 'Accept': 'application/json' }
                });
                const data = await response.json();

                if(data.error) {
                    console.error("API Error:", data.error);
                    return;
                }

                document.getElementById('cpu-val').innerText = data.server.cpu_usage_percent.toFixed(1);
                document.getElementById('cpu-bar').style.width = `${Math.min(100, data.server.cpu_usage_percent)}%`;
                document.getElementById('ram-val').innerText = data.server.ram_usage_mb;
                document.getElementById('uptime-val').innerText = formatUptime(data.server.uptime_seconds);
                document.getElementById('model-val').innerText = data.server.model_loaded;
                document.getElementById('tasks-val').innerText = data.database.total_tasks;
                document.getElementById('nodes-val').innerText = data.database.knowledge_graph_nodes;
                document.getElementById('edges-val').innerText = data.database.knowledge_graph_edges;
                document.getElementById('vectors-val').innerText = data.database.indexed_search_documents;

            } catch (err) {
                console.error("Failed to fetch metrics", err);
            }
        }

        fetchMetrics();
        setInterval(fetchMetrics, 2000);
    </script>
</body>
</html>
"""

# The file currently ends with </div>\n"""
code = code.replace('</div>\n"""', '</div>\n' + script_tag + '"""')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(path)
