import json
import os
from groq import Groq
from dotenv import load_dotenv
from collections import Counter

# Load API Key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def generate_report():
    themed_path = 'data/themed_reviews.json'
    if not os.path.exists(themed_path):
        print(f"Error: {themed_path} not found.")
        return
        
    with open(themed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    themes = data['themes']
    reviews = data['grouped_reviews']
    
    # Identify Top 3 Themes
    theme_counts = Counter([r['theme'] for r in reviews])
    top_3_themes = [theme for theme, count in theme_counts.most_common(3)]
    
    print(f"Top 3 Themes identified: {top_3_themes}")
    
    report_content = "# Weekly Product Discovery Note - Spotify (Google Play Store)\n\n"
    
    for theme in top_3_themes:
        # Get reviews for this theme
        theme_reviews = [r for r in reviews if r['theme'] == theme]
        
        # Select 3 representative quotes (longest ones usually have more context)
        quotes = sorted(theme_reviews, key=lambda x: len(x['text']), reverse=True)[:3]
        quotes_str = "\n".join([f"- \"{q['text']}\"" for q in quotes])
        
        # Generate 3 action ideas using LLM
        prompt = f"""
        Theme: {theme}
        Representative User Quotes:
        {quotes_str}
        
        Based on this feedback for Spotify, suggest 3 concise, high-impact 'Action Ideas' for the product team.
        Return a JSON list of strings.
        """
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}
            )
            response = json.loads(chat_completion.choices[0].message.content)
            # Handle different JSON structures
            ideas = response.get('action_ideas', response.get('ideas', list(response.values())[0]))
        except Exception as e:
            print(f"Error generating ideas for {theme}: {e}")
            ideas = ["Review feedback manually for insights.", "Consult the product roadmap for alignment.", "Monitor user sentiment carefully."]
            
        # Ensure ideas is a list of strings (Fix for S-t-a rendering bug)
        if isinstance(ideas, str):
            ideas = [ideas]
        elif not isinstance(ideas, list):
            ideas = [str(ideas)]
            
        report_content += f"## Theme: {theme}\n\n"
        report_content += "### Top 3 User Quotes\n"
        report_content += quotes_str + "\n\n"
        report_content += "### 3 Action Ideas\n"
        for idea in ideas[:3]:
            report_content += f"- {idea}\n"
        report_content += "\n---\n\n"
        
    os.makedirs('reports', exist_ok=True)
    report_file = 'reports/weekly_note.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"Report generated successfully: {report_file}")

if __name__ == "__main__":
    generate_report()
