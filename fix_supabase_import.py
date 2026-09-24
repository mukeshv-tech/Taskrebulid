import codecs
import re

def fix_file(path):
    code = codecs.open(path, 'r', 'utf-8').read()
    code = code.replace("from app.supabase import supabase", "from app.supabase import get_supabase")
    code = code.replace("supabase.rpc(", "get_supabase().rpc(")
    code = code.replace("supabase.table(", "get_supabase().table(")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

fix_file('render-backend/app/routes/search.py')
fix_file('render-backend/app/services/search_indexer.py')
