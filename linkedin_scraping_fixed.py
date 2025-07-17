import os
import json
import sys
import asyncio
import httpx
import time
from typing import List, Dict, Any, Optional

# Load API key from environment variables or secrets.json with graceful error handling
SCRAPING_DOG_API_KEY = os.getenv("SCRAPING_DOG_API_KEY")
if not SCRAPING_DOG_API_KEY:
    try:
        with open(os.path.join(os.path.dirname(__file__), "secrets.json"), "r") as f:
            _secrets = json.load(f)
        SCRAPING_DOG_API_KEY = _secrets.get("scraping_dog_api_key")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️  Warning: Could not load ScrapingDog API key: {e}")
        print("   LinkedIn scraping will be disabled. Set SCRAPING_DOG_API_KEY environment variable or create secrets.json.")

async def async_scrape_linkedin_profiles(urls: List[str], delay: float = 1.5, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Async scrape LinkedIn profile data via ScrapingDog API with throttling and exponential backoff.
    
    Args:
        urls (list of str): LinkedIn profile URLs to scrape.
        delay (float): Delay in seconds between requests.
        max_retries (int): Max number of retries per request.
        
    Returns:
        list of dict: Scraped profile data for each URL.
    """
    # Input validation
    if not SCRAPING_DOG_API_KEY:
        print("⚠️  LinkedIn scraping disabled - no API key available")
        return []
        
    if not urls:
        print("⚠️  No LinkedIn URLs provided")
        return []
        
    if not isinstance(urls, list):
        print(f"⚠️  Expected list of URLs but got {type(urls)}")
        # Convert to list if it's a string
        if isinstance(urls, str):
            urls = [urls]
        else:
            return []
    
    print(f"🔍 Scraping {len(urls)} LinkedIn profiles with ScrapingDog API (async)...")
    results = []
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            for i, url in enumerate(urls, 1):
                # Skip None or empty URLs
                if not url:
                    print("⚠️  Skipping empty URL")
                    results.append({"error": "Empty URL"})
                    continue
                    
                # Extract username from LinkedIn URL
                if "linkedin.com/in/" in url:
                    username = url.split("linkedin.com/in/")[1].split("/")[0].split("?")[0]
                else:
                    print(f"⚠️  Invalid LinkedIn URL format: {url}")
                    results.append({"error": "Invalid LinkedIn URL", "url": url})
                    continue
                    
                print(f"📊 Scraping profile {i}/{len(urls)}: {username}")
                api_url = "https://api.scrapingdog.com/linkedin"
                params = {
                    "api_key": SCRAPING_DOG_API_KEY,
                    "type": "profile",
                    "linkId": username,
                    "premium": "false"
                }
                
                attempt = 0
                while attempt <= max_retries:
                    try:
                        resp = await client.get(api_url, params=params)
                        if resp.status_code == 200:
                            data = resp.json()
                            print(f"✅ Successfully scraped profile for {username}")
                            # Handle different response formats
                            if isinstance(data, list) and data:
                                results.append(data[0])
                            elif isinstance(data, dict):
                                results.append(data)
                            else:
                                print(f"⚠️  Unexpected response format for {username}: {type(data)}")
                                results.append({"error": "Unexpected response format", "url": url})
                            break
                        elif resp.status_code in (429, 500, 502, 503, 504):
                            # Retry with exponential backoff
                            wait = delay * (2 ** attempt)
                            print(f"⏳ Retry {attempt+1}/{max_retries} for {username} after {wait:.1f}s (status {resp.status_code})")
                            await asyncio.sleep(wait)
                            attempt += 1
                        else:
                            print(f"⚠️  Failed for {username}: {resp.status_code} {resp.text}")
                            results.append({"error": f"HTTP {resp.status_code}", "url": url})
                            break
                    except Exception as e:
                        wait = delay * (2 ** attempt)
                        print(f"⚠️  Exception for {username}: {e}. Retry {attempt+1}/{max_retries} after {wait:.1f}s")
                        await asyncio.sleep(wait)
                        attempt += 1
                else:
                    print(f"❌ Failed to scrape {username} after {max_retries} retries.")
                    results.append({"error": "Max retries exceeded", "url": url})
                
                # Throttle between requests
                await asyncio.sleep(delay)
                
        print(f"✅ Completed LinkedIn scraping: {len(results)} profiles processed")
        return results
    except Exception as e:
        print(f"❌ LinkedIn scraping failed with error: {e}")
        return results  # Return any results we've collected so far

if __name__ == "__main__":
    import asyncio
    if len(sys.argv) > 1:
        urls = json.loads(sys.argv[1])
    else:
        urls = json.loads(input("Enter JSON array of LinkedIn URLs: "))
    results = asyncio.run(async_scrape_linkedin_profiles(urls))
    print(json.dumps(results, indent=2))