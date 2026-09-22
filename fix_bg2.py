import codecs

path = 'taskrebuild/extension/src/background/index.ts'
code = codecs.open(path, 'r', 'utf-8').read()

start_idx = code.find('// --- Phase 7 Automated Resource Monitoring ---')
if start_idx != -1:
    code = code[:start_idx]
    
with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
