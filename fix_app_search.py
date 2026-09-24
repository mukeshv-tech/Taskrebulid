import codecs
import re

path = 'taskrebuild/extension/src/popup/App.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace("import GraphTab from './components/GraphTab';", "import GraphTab from './components/GraphTab';\nimport SearchTab from './components/SearchTab';")

# Add to the global view
global_search = """
      <SearchTab onNavigateToTask={(tid) => {
        const t = tasks.find(x => x.id === tid);
        if (t) setSelectedTask(t);
      }} />
      
      <div className="tasks-section">
"""
code = code.replace('<div className="tasks-section">', global_search)

# Add to the task view
task_search = """
        <SearchTab taskId={selectedTask.id} />
        <GraphTab taskId={selectedTask.id} />
"""
code = code.replace('<GraphTab taskId={selectedTask.id} />', task_search)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
