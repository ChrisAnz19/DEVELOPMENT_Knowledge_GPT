import os
import requests
import json
import sys

# Load API key from environment variables or secrets.json with graceful error handling
BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY")
if not BRIGHT_DATA_API_KEY:
    try:
        with open(os.path.join(os.path.dirname(__file__), "secrets.json"), "r") as f:
            _secrets = json.load(f)
        BRIGHT_DATA_API_KEY = _secrets.get("bright_data_api_key")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️  Warning: Could not load Bright Data API key: {e}")
        print("   LinkedIn scraping will be disabled. Set BRIGHT_DATA_API_KEY environment variable or create secrets.json.")


def scrape_linkedin_profiles(urls):
    """
    Scrape LinkedIn profile data via BrightData Dataset API.
    Args:
        urls (list of str): LinkedIn profile URLs to scrape.
    Returns:
        list of dict: Scraped profile data for each URL.
    """
    if not BRIGHT_DATA_API_KEY:
        print("⚠️  LinkedIn scraping disabled - no API key available")
        return []
    
    try:
        bd_url = "https://api.brightdata.com/datasets/v3/trigger"
        headers = {
            "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}",
            "Content-Type": "application/json",
        }
        params = {
            "dataset_id": "gd_l1viktl72bvl7bjuj0",
            "include_errors": "true",
        }
        # Prepare request body
        data = [{"url": url} for url in urls]
        response = requests.post(bd_url, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  LinkedIn API request failed: {e}")
        return []
    except Exception as e:
        print(f"⚠️  LinkedIn scraping error: {e}")
        return []


def scrape_linkedin_posts(post_urls):
    """
    Scrape LinkedIn post data via BrightData Dataset API for given post URLs.
    Args:
        post_urls (list of str): LinkedIn post URLs to scrape.
    Returns:
        list of dict: Scraped post data for each URL.
    """
    if not BRIGHT_DATA_API_KEY:
        print("⚠️  LinkedIn post scraping disabled - no API key available")
        return []
    
    try:
        bd_posts_url = "https://api.brightdata.com/datasets/v3/trigger"
        headers = {
            "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}",
            "Content-Type": "application/json",
        }
        params = {
            "dataset_id": "gd_lyy3tktm25m4avu764",
            "include_errors": "true",
        }
        data = [{"url": url} for url in post_urls]
        response = requests.post(bd_posts_url, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  LinkedIn posts API request failed: {e}")
        return []
    except Exception as e:
        print(f"⚠️  LinkedIn post scraping error: {e}")
        return []


if __name__ == "__main__":
    # Expect a JSON list of URLs as the first CLI argument or from input
    if len(sys.argv) > 1:
        urls = json.loads(sys.argv[1])
    else:
        urls = json.loads(input("Enter JSON array of LinkedIn URLs: "))

    results = scrape_linkedin_profiles(urls)
    print(json.dumps(results, indent=2))

    # After printing profile scraping results:
    for profile in results:
        posts = profile.get("posts") or []
        recent_posts = posts[:5]
        if recent_posts:
            print(f"\nScraping up to 5 recent posts for {profile.get('name')}:")
            posts_data = scrape_linkedin_posts(recent_posts)
            print(json.dumps(posts_data, indent=2))