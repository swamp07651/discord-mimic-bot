import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("Testing Gemini API...")
print("\n1. Listing available models:")

try:
    models = list(genai.list_models())
    print(f"Found {len(models)} models")
    
    # Filter for models that support generateContent
    content_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
    
    print(f"\nModels supporting generateContent ({len(content_models)}):")
    for model in content_models[:5]:
        print(f"  - {model.name}")
    
    if content_models:
        # Try using the first available model
        test_model_name = content_models[0].name
        print(f"\n2. Testing model: {test_model_name}")
        
        model = genai.GenerativeModel(test_model_name)
        response = model.generate_content("こんにちは")
        print(f"Response: {response.text}")
        print("\n✅ Success! This model works.")
        print(f"Use this model name in bot.py: {test_model_name}")
    else:
        print("\n❌ No models supporting generateContent found")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
