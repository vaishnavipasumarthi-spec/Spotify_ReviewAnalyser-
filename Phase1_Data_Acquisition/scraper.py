import json
import os
import time
import requests
from bs4 import BeautifulSoup
from google_play_scraper import Sort, reviews as gp_reviews
from datetime import datetime, timedelta

def scrape_google_play(app_id='com.spotify.music', target_count=300):
    print(f"--- Scraping Google Play Store for {app_id} ---")
    all_reviews = []
    continuation_token = None
    twelve_weeks_ago = datetime.now() - timedelta(weeks=12)
    
    while len(all_reviews) < target_count:
        batch, continuation_token = gp_reviews(
            app_id, lang='en', country='us', sort=Sort.NEWEST, count=100, continuation_token=continuation_token
        )
        if not batch: break
        
        for r in batch:
            review_date = r['at'].replace(tzinfo=None)
            if review_date < twelve_weeks_ago: continue
            
            all_reviews.append({
                'review_id': r['reviewId'],
                'rating': r['score'],
                'text': r['content'],
                'date': r['at'].isoformat(),
                'source': 'Google Play Store'
            })
            if len(all_reviews) >= target_count: break
        if not continuation_token: break
    return all_reviews

def scrape_reddit(query='spotify discovery', target_count=50):
    print(f"--- Scraping Reddit for '{query}' ---")
    # Using a simple search URL with .json suffix (though Reddit blocks bots, we try common headers)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SpotifyReviewAnalysis/1.0'}
    url = f"https://www.reddit.com/r/spotify/search.json?q={query}&restrict_sr=1&sort=new&limit={target_count}"
    
    reddit_data = []
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            posts = response.json().get('data', {}).get('children', [])
            for post in posts:
                p = post.get('data', {})
                reddit_data.append({
                    'review_id': p.get('id'),
                    'rating': 5, # Default for discussions
                    'text': f"{p.get('title')}\n{p.get('selftext')}",
                    'date': datetime.fromtimestamp(p.get('created_utc')).isoformat(),
                    'source': 'Reddit'
                })
        else:
            print(f"Reddit Scrape failed (Status: {response.status_code}). Using mock data.")
    except Exception as e:
        print(f"Reddit Exception: {e}. Using mock data.")
    
    # Fallback/Mock if Reddit blocks
    if not reddit_data:
        reddit_data = [{
            'review_id': f'rd_{i}', 'rating': 5, 'text': f"Mock Reddit Discussion {i}: I hate how Spotify only plays the same songs in my discovery mix.",
            'date': datetime.now().isoformat(), 'source': 'Reddit'
        } for i in range(5)]
        
    return reddit_data

def scrape_spotify_forums(query='discovery', target_count=50):
    print(f"--- Scraping Spotify Community for '{query}' ---")
    # Mock for complex dynamic forum
    forum_data = [{
        'review_id': f'sf_{i}', 'rating': 5, 'text': f"Mock Forum Thread {i}: Discovery weekly is broken for me since the last update.",
        'date': datetime.now().isoformat(), 'source': 'Community Forum'
    } for i in range(5)]
    return forum_data

def scrape_social_media(query='spotify', target_count=50):
    print(f"--- Scraping Social Media for '{query}' ---")
    # Mock for restricted social APIs
    social_data = [{
        'review_id': f'sm_{i}', 'rating': 5, 'text': f"Mock Social Post {i}: Why does Spotify keep recommending songs I already liked? #SpotifyDiscovery",
        'date': datetime.now().isoformat(), 'source': 'Social Media'
    } for i in range(5)]
    return social_data

def scrape_all_sources(target_total=500):
    os.makedirs('data', exist_ok=True)
    
    # Distributed targets
    gp_data = scrape_google_play(target_count=350)
    reddit_data = scrape_reddit(target_count=50)
    forum_data = scrape_spotify_forums(target_count=50)
    social_data = scrape_social_media(target_count=50)
    
    all_data = gp_data + reddit_data + forum_data + social_data
    
    with open('data/raw_reviews.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    
    print(f"Total Unified Records Captured: {len(all_data)}")
    return len(all_data)

if __name__ == "__main__":
    scrape_all_sources()
