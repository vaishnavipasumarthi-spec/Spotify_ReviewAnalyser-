import json
import os
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
import random
import time

# Load API Key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key or api_key == "your_groq_api_key_here":
    print("Error: GROQ_API_KEY not found in .env file.")
    print("Please create a .env file with GROQ_API_KEY=your_actual_key")
    exit(1)

client = Groq(api_key=api_key)

def get_discovery_questions():
    return [
        "1. Why do users struggle to discover new music?",
        "2. What are the most common frustrations with recommendations?",
        "3. What listening behaviors are users trying to achieve?",
        "4. What causes users to repeatedly listen to the same content?",
        "5. Which user segments experience different discovery challenges?",
        "6. What unmet needs emerge consistently across reviews?"
    ]

def generate_themes(reviews_sample):
    print("Generating top 6 themes based on sample reviews...")
    
    # Format sample for LLM
    sample_text = "\n".join([f"- {r['text']}" for r in reviews_sample])
    
    questions = "\n".join(get_discovery_questions())
    
    prompt = f"""
    Analyze the following Spotify user reviews and generate exactly 6 core themes that address these discovery questions:
    {questions}
    
    Reviews Sample:
    {sample_text}
    
    Return the 6 themes as a clean JSON list of strings. Each theme should be a short, descriptive phrase.
    Example: ["Difficulty discovering niche genres", "Frustration with repetitive 'Daily Mixes'", ...]
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )
    
    response = json.loads(chat_completion.choices[0].message.content)
    # Depending on LLM response structure, extract the list
    themes = response.get('themes', list(response.values())[0])
    return themes[:6]

def classify_reviews(reviews, themes):
    print(f"Grouping {len(reviews)} reviews into themes...")
    
    # We will classify in batches to save tokens/time
    batch_size = 50
    results = []
    
    themes_str = ", ".join(themes)
    
    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i+batch_size]
        batch_text = "\n".join([f"ID: {r['review_id']} | Text: {r['text']}" for r in batch])
        
        prompt = f"""
        Classify each review below into exactly ONE of the following themes:
        Themes: {themes_str}
        
        Reviews:
        {batch_text}
        
        Return a JSON object where keys are the review IDs and values are the chosen theme name.
        """
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant", # Faster model for classification
                response_format={"type": "json_object"}
            )
            
            classifications = json.loads(chat_completion.choices[0].message.content)
            
            for r in batch:
                theme = classifications.get(r['review_id'], "Other")
                r['theme'] = theme
                results.append(r)
                
            print(f"Processed {min(i+batch_size, len(reviews))}/{len(reviews)} reviews...")
            # Reduced sleep to speed up local execution
            time.sleep(0.1) 
            
        except Exception as e:
            print(f"Error processing batch {i}: {e}")
            for r in batch:
                r['theme'] = "Unclassified"
                results.append(r)
                
    return results

def run_phase_3():
    with open('data/cleaned_reviews.json', 'r', encoding='utf-8') as f:
        reviews = json.load(f)
        
    if not reviews:
        print("No reviews found to analyze.")
        return
        
    # Step 1: Generate Themes from a sample (e.g., 50 reviews)
    sample_size = min(50, len(reviews))
    sample = random.sample(reviews, sample_size)
    themes = generate_themes(sample)
    print(f"Generated Themes: {themes}")
    
    # Step 2: Classify all reviews
    # To save time and the user's credits, we'll limit the actual classification 
    # to a reasonable number or let them run all.
    # For now, let's process the first 500 reviews as a proof of concept if they run it.
    process_limit = 500 
    reviews_to_process = reviews[:process_limit]
    
    grouped_reviews = classify_reviews(reviews_to_process, themes)
    
    output = {
        "themes": themes,
        "grouped_reviews": grouped_reviews
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/themed_reviews.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
        
    print(f"Phase 3 Complete. Themed reviews saved to data/themed_reviews.json")

if __name__ == "__main__":
    run_phase_3()
