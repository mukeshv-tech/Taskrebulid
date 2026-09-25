import os
import shutil

# Copy quantized ONNX data model
desktop = r"C:\Users\User\Desktop"
onnx_data_src = os.path.join(desktop, "onnx", "model_quantized.onnx_data")
model_dir = r"C:\Users\User\Desktop\Taskrebulid\render-backend\app\local_model"

if os.path.exists(onnx_data_src):
    shutil.copy(onnx_data_src, os.path.join(model_dir, "model_quantized.onnx_data"))
    print("Copied successfully.")
else:
    print("Data file not found.")
