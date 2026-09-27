import codecs
from app.supabase import get_supabase
import json

supabase = get_supabase()
res = supabase.table("search_documents").select("id, source_type, title, content, metadata").limit(5).execute()

print(json.dumps(res.data, indent=2))
