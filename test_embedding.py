import os
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("NO API KEY!")
else:
    print("Key is set.")
    genai.configure(api_key=api_key)
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content="test query",
            task_type="retrieval_document"
        )
        print("Success:", len(result['embedding']))
    except Exception as e:
        print("Error:", e)
