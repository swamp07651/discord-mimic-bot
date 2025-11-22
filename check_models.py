import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def main():
    print("Listing available models...")
    for m in genai.list_models():
        if "createTunedModel" in m.supported_generation_methods:
            print(f"Name: {m.name}")
            print(f"  Display Name: {m.display_name}")
            print(f"  Description: {m.description}")
            print("-" * 20)

if __name__ == "__main__":
    main()
