import json

path = r'C:\Users\User\Desktop\Taskrebulid\taskrebuild\extension\public\manifest.json'
with open(path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

if "clipboardWrite" not in manifest.get("permissions", []):
    manifest["permissions"].append("clipboardWrite")

with open(path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)
