import os
import google.generativeai as genai

# Just test if the API throws an error for 3.6-flash using a fake or real key
genai.configure(api_key="AIzaSyA-FakeKeyForTestingPurposesOnly")
model = genai.GenerativeModel("gemini-3.6-flash")

try:
    # We just want to see if the library itself rejects the name before sending, or if the server rejects it.
    print("Model initialized locally.")
except Exception as e:
    print("Init error:", str(e))
