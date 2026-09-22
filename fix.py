import codecs
with codecs.open('render-backend/app/services/ai/groq_provider.py', 'r', 'utf-8') as f:
    text = f.read()
text = text.replace('"""', '\"\"\"')
with codecs.open('render-backend/app/services/ai/groq_provider.py', 'w', 'utf-8') as f:
    f.write(text)
