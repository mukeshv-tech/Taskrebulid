import codecs

path = 'README.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the first paragraph to include "task-aware extension project"
old_intro = "**TaskRebuild** is a next-generation, AI-powered productivity suite and context-aware workspace. It consists of a React Chrome Extension and a massively scalable Python/PostgreSQL backend that act as your automatic \"Second Brain.\""

new_intro = "**TaskRebuild** is an intelligent, **task-aware extension project** designed to act as your automatic \"Second Brain.\" By combining a React-powered Chrome Extension with a massively scalable Python/PostgreSQL backend, it creates a next-generation, context-aware productivity workspace."

content = content.replace(old_intro, new_intro)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
