import os
import requests
import json
import sys

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


def scrape_linkedin_profiles(urls):
    """
    Scrape LinkedIn profile data via ScrapingDog API.
    Args:
        urls (list of str): LinkedIn profile URLs to scrape.
    Returns:
        list of dict: Scraped profile data for each URL.
    """
    if not SCRAPING_DOG_API_KEY:
        print("⚠️  LinkedIn scraping disabled - no API key available")
        return []
    
    if not urls:
        print("⚠️  No LinkedIn URLs provided")
        return []
    
    print(f"🔍 Scraping {len(urls)} LinkedIn profiles with ScrapingDog API...")
    
    results = []
    for i, url in enumerate(urls, 1):
        try:
            # Extract username from LinkedIn URL
            if "linkedin.com/in/" in url:
                username = url.split("linkedin.com/in/")[1].split("/")[0].split("?")[0]
            else:
                print(f"⚠️  Invalid LinkedIn URL format: {url}")
                continue
            
            print(f"📊 Scraping profile {i}/{len(urls)}: {username}")
            
            # ScrapingDog API endpoint
            api_url = "https://api.scrapingdog.com/linkedin"
            params = {
                "api_key": SCRAPING_DOG_API_KEY,
                "type": "profile",
                "linkId": username,
                "premium": "false"
            }
            
            response = requests.get(api_url, params=params, timeout=60)
            response.raise_for_status()
            
            profile_data = response.json()
            
            # Check if we got valid data
            if profile_data and isinstance(profile_data, list) and len(profile_data) > 0:
                print(f"✅ Successfully scraped profile for {username}")
                results.append(profile_data[0])  # Take the first result
            elif profile_data and isinstance(profile_data, dict):
                print(f"✅ Successfully scraped profile for {username}")
                results.append(profile_data)
            else:
                print(f"⚠️  Invalid response for {username}: {profile_data}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Request failed for {url}: {e}")
        except Exception as e:
            print(f"⚠️  Error scraping {url}: {e}")
    
    print(f"✅ Completed LinkedIn scraping: {len(results)} profiles scraped successfully")
    return results


def scrape_linkedin_posts(post_urls):
    """
    Scrape LinkedIn post data via ScrapingDog API for given post URLs.
    Args:
        post_urls (list of str): LinkedIn post URLs to scrape.
    Returns:
        list of dict: Scraped post data for each URL.
    """
    if not SCRAPING_DOG_API_KEY:
        print("⚠️  LinkedIn post scraping disabled - no API key available")
        return []
    
    if not post_urls:
        print("⚠️  No LinkedIn post URLs provided")
        return []
    
    print(f"🔍 Scraping {len(post_urls)} LinkedIn posts with ScrapingDog API...")
    
    results = []
    for i, url in enumerate(post_urls, 1):
        try:
            print(f"📊 Scraping post {i}/{len(post_urls)}")
            
            # ScrapingDog API endpoint for posts
            api_url = "https://api.scrapingdog.com/linkedin"
            params = {
                "api_key": SCRAPING_DOG_API_KEY,
                "type": "post",
                "linkId": url,
                "premium": "false"
            }
            
            response = requests.get(api_url, params=params, timeout=60)
            response.raise_for_status()
            
            post_data = response.json()
            
            # Check if we got valid data
            if post_data and isinstance(post_data, dict):
                print(f"✅ Successfully scraped post {i}")
                results.append(post_data)
            else:
                print(f"⚠️  Invalid response for post {i}: {post_data}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Request failed for post {url}: {e}")
        except Exception as e:
            print(f"⚠️  Error scraping post {url}: {e}")
    
    print(f"✅ Completed LinkedIn post scraping: {len(results)} posts scraped successfully")
    return results


if __name__ == "__main__":
    # Test the scraper
    if len(sys.argv) > 1:
        urls = json.loads(sys.argv[1])
    else:
        urls = json.loads(input("Enter JSON array of LinkedIn URLs: "))

    results = scrape_linkedin_profiles(urls)
    print(json.dumps(results, indent=2))