import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def main():
    dataset_path = 'finetune_dataset.jsonl'
    if not os.path.exists(dataset_path):
        print(f"Dataset not found: {dataset_path}")
        return

    print("Uploading dataset...")
    
    # Reading the JSONL to pass as object
    import json
    training_data = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                training_data.append(json.loads(line))
    
    print(f"Loaded {len(training_data)} examples.")
    
    # Base model for tuning
    base_model = "models/gemini-1.5-flash-001-tuning"
    
    print(f"Starting fine-tuning job based on {base_model}...")
    
    try:
        operation = genai.create_tuned_model(
            display_name="takenicle-mimic-v1",
            source_model=base_model,
            epoch_count=5,
            batch_size=4,
            learning_rate=0.001,
            training_data=training_data,
        )
        
        print(f"Tuning job started: {operation.name}")
        print("Waiting for completion... (This may take minutes)")
        
        # Poll for status
        for status in operation.wait_bar():
            time.sleep(10)
            
        result = operation.result()
        print(f"Fine-tuning complete!")
        print(f"Tuned Model Name: {result.name}")
        
        # Save the model name to a file so the bot can use it
        with open('data/tuned_model_name.txt', 'w') as f:
            f.write(result.name)
            
    except Exception as e:
        print(f"Fine-tuning failed: {e}")
        # Fallback: Print instructions if SDK fails
        print("If the SDK failed, please check the API documentation or quotas.")

if __name__ == '__main__':
    main()
