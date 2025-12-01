import os
import json
import glob

def extract_messages(root_dir):
    all_messages = []
    
    # Walk through all subdirectories in the messages folder
    # Pattern: root_dir/c*/messages.json
    pattern = os.path.join(root_dir, "c*", "messages.json")
    files = glob.glob(pattern)
    
    print(f"Found {len(files)} message files.")
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for msg in data:
                        content = msg.get('Contents', '')
                        if content:
                            all_messages.append(content)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    return all_messages

if __name__ == "__main__":
    root_dir = r"c:\Users\swamp\.gemini\discord_mimic_bot\data\swamp_data\メッセージ"
    messages = extract_messages(root_dir)
    
    print(f"Extracted {len(messages)} messages.")
    
    output_path = r"c:\Users\swamp\.gemini\discord_mimic_bot\data\swamp_messages.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        for msg in messages:
            f.write(msg + "\n")
            
    print(f"Saved to {output_path}")
