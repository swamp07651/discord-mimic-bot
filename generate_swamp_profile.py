import google.generativeai as genai
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

def generate_profile():
    # Load messages
    with open('data/swamp_messages.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Sample messages (random 500)
    sample_size = min(len(lines), 500)
    sample_messages = random.sample(lines, sample_size)
    sample_text = "\n".join(sample_messages)
    
    print(f"Loaded {len(lines)} messages. Sampling {sample_size} for analysis.")
    
    prompt = f"""
    You are an expert personality profiler. Analyze the following Discord messages from a user named "swamp" and create a personality JSON configuration file for a mimic bot.
    
    The JSON structure MUST match this exactly:
    {{
      "name": "swamp",
      "description": "A brief description of the personality.",
      "analysis": "A detailed markdown analysis of the speaking style, tone, and interests.",
      "config": {{
        "tone": {{
          "casual": 0-10,
          "vulgar": 0-10,
          "energetic": 0-10,
          "friendly": 0-10
        }},
        "language_style": {{
          "use_slang": boolean,
          "use_w_laugh": boolean,
          "short_responses": boolean,
          "use_emojis": boolean
        }},
        "common_phrases": {{
          "phrase": frequency(1-10)
        }},
        "topic_reactions": {{
          "gaming": 0-10,
          "anime": 0-10,
          "sports": 0-10,
          "tech": 0-10
        }},
        "interests": {{
          "favorite_games": ["list", "of", "games"],
          "favorite_anime": ["list", "of", "anime"],
          "favorite_topics": ["list", "of", "topics"],
          "common_references": {{
            "category": ["terms"]
          }}
        }},
        "topic_styles": {{
          "gaming": {{ "excitement_level": 0-10, "use_technical_terms": boolean, "call_for_teammates": boolean }},
          "winning": {{ "phrases": [] }},
          "losing": {{ "phrases": [] }}
        }},
        "server_members": {{
             // Leave empty or infer if specific names appear often, but better to leave empty for now as we don't have relationship context
        }},
        "response_length": {{
          "min_words": int,
          "max_words": int,
          "prefer_short": boolean
        }},
        "custom_rules": [
          "list of specific behavioral rules derived from analysis"
        ]
      }},
      "examples": {{
        "greeting": [],
        "agreement": [],
        "surprise": [],
        "laughter": [],
        "praise": [],
        "negative": []
      }}
    }}
    
    **Messages Sample:**
    {sample_text}
    
    Output ONLY the valid JSON string. Do not use markdown code blocks.
    """
    
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    
    try:
        # Clean response if it contains markdown
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
            
        profile = json.loads(text)
        
        # Save to file
        with open('personalities/swamp.json', 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
            
        print("Successfully created personalities/swamp.json")
        
    except Exception as e:
        print(f"Error parsing or saving JSON: {e}")
        print("Raw response:", response.text)

if __name__ == "__main__":
    generate_profile()
