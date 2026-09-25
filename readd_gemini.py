import codecs

req_path = 'render-backend/requirements.txt'
reqs = codecs.open(req_path, 'r', 'utf-8').read()

if "google-generativeai" not in reqs:
    reqs += "\ngoogle-generativeai>=0.8.6\n"
    with codecs.open(req_path, 'w', 'utf-8') as f:
        f.write(reqs)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)

fix_newlines(req_path)
