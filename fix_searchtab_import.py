import codecs

path = 'taskrebuild/extension/src/popup/components/SearchTab.tsx'
code = codecs.open(path, 'r', 'utf-8').read()
code = code.replace("'../lib/api'", "'../../lib/api'")
with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
