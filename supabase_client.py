from supabase import create_client, Client
import os
import json

def load_supabase_creds():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        with open("secrets.json") as f:
            secrets = json.load(f)
            url = url or secrets.get("supabase_url")
            key = key or secrets.get("supabase_key")
    return url, key

url, key = load_supabase_creds()
supabase: Client = create_client(url, key) 