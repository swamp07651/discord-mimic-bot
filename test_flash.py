import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("Testing gemini-2.5-flash model specifically...")

try:
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content("こんにちは")
    print(f"✅ Success!")
    print(f"Response: {response.text}")
    print("\nThis model works! Using models/gemini-2.5-flash")
except Exception as e:
    print(f"❌ Error with gemini-2.5-flash: {e}")
    
    # Try gemini-1.5-flash as fallback
    print("\nTrying gemini-1.5-flash as fallback...")
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content("こんにちは")
        print(f"✅ Success!")
        print(f"Response: {response.text}")
        print("\nThis model works! Using models/gemini-1.5-flash")
    except Exception as e2:
        print(f"❌ Error with gemini-1.5-flash: {e2}")
