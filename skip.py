import codecs
import re

path = 'supabase_schema.sql'
code = codecs.open(path, 'r', 'utf-8').read()

# I will just write a new script to update the RPC string in supabase_schema.sql directly, but it's easier to just output the artifact for the user since that's what they actually run in the UI.
