import os
import shutil
import codecs

# 1. Create directory for local model
model_dir = r"C:\Users\User\Desktop\Taskrebulid\render-backend\app\local_model"
os.makedirs(model_dir, exist_ok=True)

# 2. Copy tokenizer files from Desktop
desktop = r"C:\Users\User\Desktop"
files_to_copy = [
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.txt",
    "special_tokens_map.json",
    "config.json"
]
for f in files_to_copy:
    src = os.path.join(desktop, f)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(model_dir, f))

# 3. Copy quantized ONNX model
onnx_src = os.path.join(desktop, "onnx", "model_quantized.onnx")
if os.path.exists(onnx_src):
    shutil.copy(onnx_src, os.path.join(model_dir, "model_quantized.onnx"))

# 4. Update requirements.txt
req_path = r"C:\Users\User\Desktop\Taskrebulid\render-backend\requirements.txt"
with codecs.open(req_path, 'r', 'utf-8') as f:
    reqs = f.read()

if "onnxruntime" not in reqs:
    reqs += "\nonnxruntime>=1.15.0\ntokenizers>=0.13.3\n"
    with codecs.open(req_path, 'w', 'utf-8') as f:
        f.write(reqs)

def fix_newlines(path):
    with open(path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(content)
fix_newlines(req_path)

print("Files copied and requirements updated.")
