import codecs

path = 'taskrebuild/extension/src/popup/components/SearchTab.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'const handleSearch = async (e: React.FormEvent) => {',
    'const handleSearch = async (e: React.FormEvent) => {\n    console.log("Search button clicked! Query:", query);'
)
code = code.replace(
    'const endpoint =',
    'console.log("Making fetch request to endpoint:", taskId ? `/api/search?q=${encodeURIComponent(query)}&task_id=${taskId}` : `/api/search?q=${encodeURIComponent(query)}`);\n        const endpoint ='
)
code = code.replace(
    'const data = await fetchApi(endpoint);',
    'console.log("Calling fetchApi...");\n        const data = await fetchApi(endpoint);\n        console.log("Fetch returned:", data);'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
