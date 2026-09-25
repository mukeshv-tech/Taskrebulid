import onnxruntime as ort
import os
import json

model_path = r"C:\Users\User\Desktop\Taskrebulid\render-backend\app\local_model\model_quantized.onnx"
session = ort.InferenceSession(model_path)
print("Inputs:")
for i in session.get_inputs():
    print(i.name, i.shape, i.type)

print("\nOutputs:")
for o in session.get_outputs():
    print(o.name, o.shape, o.type)
