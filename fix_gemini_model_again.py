import codecs

path = 'render-backend/app/services/search_indexer.py'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    'self.model_name = "models/text-embedding-004"',
    'self.model_name = "models/embedding-001"'
)

# the user wants MRL with it, so we leave output_dimensionality=768
# wait, if they meant "text-embedding-004", I should just use "models/text-embedding-004".
# Wait, did the user mean "use text-embedding-004" but mistakenly called it "gemini-embedding-001"?
