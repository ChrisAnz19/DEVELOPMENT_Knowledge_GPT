from supabase import create_client, Client
import os
import os.path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_supabase_creds():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    logger.info(f"Loading Supabase credentials - URL: {url}, Key: {key[:10] if key else 'None'}...")
    
    if not url or not key:
        try:
            # Try multiple possible locations for secrets.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            secrets_paths = [
                "secrets.json",  # Current working directory
                os.path.join(current_dir, "secrets.json"),  # Same directory as this file
                os.path.join(current_dir, "..", "secrets.json"),  # Parent directory
                os.path.join(os.getcwd(), "secrets.json")  # Current working directory (explicit)
            ]
            secrets = None
            
            for path in secrets_paths:
                try:
                    with open(path) as f:
                        secrets = json.load(f)
                        logger.info(f"Found secrets.json at: {path}")
                        break
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    logger.debug(f"Failed to load {path}: {e}")
                    continue
            
            if secrets:
                # Try both uppercase and lowercase key names for compatibility
                url = url or secrets.get("supabase_url") or secrets.get("SUPABASE_URL")
                key = key or secrets.get("supabase_key") or secrets.get("SUPABASE_KEY")
                logger.info(f"Loaded from secrets.json - URL: {url}, Key: {key[:10] if key else 'None'}...")
            else:
                raise FileNotFoundError("secrets.json not found in any expected location")
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load secrets.json: {e}")
    
    if not url or not key:
        logger.error("Supabase credentials not found. Set SUPABASE_URL and SUPABASE_KEY environment variables or create secrets.json")
        # Return dummy values to prevent import errors, but the client will fail gracefully
        return "https://dummy.supabase.co", "dummy_key"
    
    return url, key

url, key = load_supabase_creds()
logger.info(f"Creating Supabase client with URL: {url}")
supabase: Client = create_client(url, key)

# Test the connection
try:
    # Try a simple query to verify the connection works
    test_result = supabase.table("searches").select("id").limit(1).execute()
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    # Create a dummy client for fallback
    class DummySupabase:
        def table(self, name):
            return DummyTable()
    
    class DummyTable:
        def select(self, *args, **kwargs):
            return self
        def insert(self, data):
            return self
        def delete(self):
            return self
        def eq(self, field, value):
            return self
        def order(self, field, desc=False):
            return self
        def limit(self, limit):
            return self
        def single(self):
            return self
        def execute(self):
            return DummyResult()
    
    class DummyResult:
        def __init__(self):
            self.data = []
            self.count = 0
    
    supabase = DummySupabase() 