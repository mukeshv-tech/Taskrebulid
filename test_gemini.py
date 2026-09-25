import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(r"C:\Users\User\Desktop\Taskrebulid\render-backend\.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.6-flash")

try:
    response = model.generate_content("Hello")
    print("Response:", response.text)
except Exception as e:
    print("Error:", str(e))
