import json
import os
import re
from langdetect import detect, detect_langs, DetectorFactory

# Ensure consistent results from langdetect
DetectorFactory.seed = 0

def clean_pii(text):
    if not text:
        return ""
    text = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', text)
    text = re.sub(r'\+?\d[\d -]{7,12}\d', '[PHONE]', text)
    return text

def is_english_strict(text):
    if not text or len(text.strip()) < 5:
        return False
    
    # Heuristic 1: Check for high non-ASCII character count (e.g. Cyrillic, Arabic, etc.)
    # English uses basic ASCII.
    non_ascii = len(re.findall(r'[^\x00-\x7F]', text))
    if non_ascii / len(text) > 0.3: # If more than 30% is non-ASCII, likely not English
        return False

    try:
        # Heuristic 2: Use langdetect with confidence
        results = detect_langs(text)
        for res in results:
            if res.lang == 'en' and res.prob > 0.9: # 90% confidence
                return True
        return False
    except:
        return False

def process_reviews():
    raw_path = 'data/raw_reviews.json'
    clean_path = 'data/cleaned_reviews.json'
    
    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} not found.")
        return
        
    with open(raw_path, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
        
    processed_reviews = []
    print(f"Processing {len(reviews)} raw reviews with strict English filtering...")
    
    removed_lang = 0
    removed_short = 0
    
    for r in reviews:
        text = r.get('text', '')
        
        # 1. Filter: Remove reviews with less than 5 words
        word_count = len(text.split())
        if word_count < 5:
            removed_short += 1
            continue
            
        # 2. Filter: Strict English only
        if not is_english_strict(text):
            removed_lang += 1
            continue
            
        # 3. PII Removal from text
        cleaned_text = clean_pii(text)
        
        processed_reviews.append({
            'review_id': r['review_id'],
            'rating': r['rating'],
            'text': cleaned_text,
            'date': r['date'],
            'is_pii_clean': True,
            'word_count': word_count
        })
        
    os.makedirs('data', exist_ok=True)
    with open(clean_path, 'w', encoding='utf-8') as f:
        json.dump(processed_reviews, f, indent=4, ensure_ascii=False)
        
    print(f"Finished processing.")
    print(f"Original reviews: {len(reviews)}")
    print(f"Removed short: {removed_short}")
    print(f"Removed non-English: {removed_lang}")
    print(f"Final cleaned reviews: {len(processed_reviews)}")
    print(f"Saved to {clean_path}")

if __name__ == "__main__":
    process_reviews()
