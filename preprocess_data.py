import json
import re
import os

def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove custom emojis <...>
    text = re.sub(r'<:\w+:\d+>', '', text)
    # Remove mentions <@...>
    text = re.sub(r'<@!?\d+>', '', text)
    # Remove extra whitespace
    text = text.strip()
    return text

def main():
    # Load Discord messages
    discord_messages = []
    if os.path.exists('data/raw_messages.json'):
        with open('data/raw_messages.json', 'r', encoding='utf-8') as f:
            discord_messages = json.load(f)
    
    # Load Twitter messages (if exists)
    twitter_messages = []
    if os.path.exists('data/twitter_raw.json'):
        with open('data/twitter_raw.json', 'r', encoding='utf-8') as f:
            twitter_messages = json.load(f)
            print(f"Loaded {len(twitter_messages)} tweets")

    cleaned_messages = []
    
    # Process Discord messages
    for msg in discord_messages:
        content = msg.get('content', '')
        cleaned = clean_text(content)
        if cleaned:
            cleaned_messages.append(cleaned)
            
    # Process Twitter messages
    for content in twitter_messages:
        cleaned = clean_text(content)
        if cleaned:
            cleaned_messages.append(cleaned)

    # Remove duplicates while preserving order
    unique_messages = list(dict.fromkeys(cleaned_messages))
    
    with open('data/cleaned_messages.txt', 'w', encoding='utf-8') as f:
        for msg in unique_messages:
            f.write(msg + '\n')
            
    print(f"Processed {len(discord_messages)} Discord messages and {len(twitter_messages)} tweets.")
    print(f"Saved {len(unique_messages)} unique cleaned messages to data/cleaned_messages.txt")

if __name__ == '__main__':
    main()
