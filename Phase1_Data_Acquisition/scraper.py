import json
import os
from google_play_scraper import Sort, reviews
import pandas as pd
from datetime import datetime, timedelta
import time

def scrape_reviews(app_id='com.spotify.music', target_count=500):
    print(f"Starting batch scrape for {app_id}...")
    
    twelve_weeks_ago = datetime.now() - timedelta(weeks=12)
    all_reviews = []
    continuation_token = None
    
    while len(all_reviews) < target_count:
        batch, continuation_token = reviews(
            app_id,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=200,
            continuation_token=continuation_token
        )
        
        if not batch:
            print("No more reviews found.")
            break
            
        stop_fetching = False
        for r in batch:
            review_date = r['at'].replace(tzinfo=None)
            if review_date < twelve_weeks_ago:
                stop_fetching = True
                break
            
            all_reviews.append({
                'review_id': r['reviewId'],
                'rating': r['score'],
                'title': r['userName'],
                'text': r['content'],
                'date': r['at'].isoformat(),
                'is_pii_clean': False
            })
            
            if len(all_reviews) >= target_count:
                stop_fetching = True
                break
        
        print(f"Fetched {len(all_reviews)} reviews so far...")
        
        if stop_fetching:
            print("Reached date limit or target count.")
            break
            
        time.sleep(0.1)
    
    os.makedirs('data', exist_ok=True)
    with open('data/raw_reviews.json', 'w', encoding='utf-8') as f:
        json.dump(all_reviews, f, indent=4, ensure_ascii=False)
    
    print(f"Saved {len(all_reviews)} reviews to data/raw_reviews.json")

if __name__ == "__main__":
    scrape_reviews(target_count=500)
