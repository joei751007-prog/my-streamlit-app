from supabase import create_client

SUPABASE_URL = "你的URL"
SUPABASE_KEY = "你的anon key"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
