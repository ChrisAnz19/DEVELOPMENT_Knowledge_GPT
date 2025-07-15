from supabase import create_client, Client
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_supabase_creds():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        try:
            with open("secrets.json") as f:
                secrets = json.load(f)
                url = url or secrets.get("supabase_url")
                key = key or secrets.get("supabase_key")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load secrets.json: {e}")
    
    if not url or not key:
        logger.error("Supabase credentials not found. Set SUPABASE_URL and SUPABASE_KEY environment variables or create secrets.json")
        # Return dummy values to prevent import errors, but the client will fail gracefully
        return "https://dummy.supabase.co", "dummy_key"
    
    return url, key

url, key = load_supabase_creds()
supabase: Client = create_client(url, key) 