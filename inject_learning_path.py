import codecs

path = 'taskrebuild/extension/src/popup/App.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Import
if "LearningPathTab" not in content:
    content = content.replace("import GraphTab from './components/GraphTab';", "import GraphTab from './components/GraphTab';\nimport LearningPathTab from './components/LearningPathTab';")

# 2. Add Component to render
if "<LearningPathTab taskId={selectedTask.id} />" not in content:
    content = content.replace("<GraphTab taskId={selectedTask.id} />", "<GraphTab taskId={selectedTask.id} />\n        <LearningPathTab taskId={selectedTask.id} />")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

def fix_newlines(path):
    with open(path, 'rb') as f:
        file_content = f.read()
    file_content = file_content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(file_content)
fix_newlines(path)
