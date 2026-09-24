import os
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("NO API KEY")
else:
    genai.configure(api_key=api_key)
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(m.name)
