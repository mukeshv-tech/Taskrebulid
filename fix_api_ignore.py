import codecs

path = 'taskrebuild/extension/src/lib/api.ts'
code = codecs.open(path, 'r', 'utf-8').read()

new_api = "export const toggleResourceIgnore = (taskId: string, resourceId: string) => fetchApi(`/api/tasks/${taskId}/resources/${resourceId}/toggle-ignore`, { method: 'POST' });\n"

code = code.replace("export const triggerResourceCheck", new_api + "export const triggerResourceCheck")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
