import codecs
import re

path = 'taskrebuild/extension/src/lib/api.ts'
code = codecs.open(path, 'r', 'utf-8').read()

new_exports = '''export const toggleAutoMonitor = (taskId: string) => fetchApi(`/api/tasks/${taskId}/toggle-monitor`, { method: 'POST' });
export const checkAllMonitored = () => fetchApi(`/api/monitoring/check-all`, { method: 'POST' });'''

code += '\n' + new_exports + '\n'

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
