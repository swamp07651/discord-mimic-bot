import discord
import os
import google.generativeai as genai
from dotenv import load_dotenv
from personality_config import personality_config, example_responses
from collections import defaultdict, deque

load_dotenv()

# Configure API keys
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)

# Load personality analysis
with open('personality_analysis.md', 'r', encoding='utf-8') as f:
    personality_text = f.read()

# Conversation memory: channel_id -> deque of (role, content) tuples
# Keep last 10 messages per channel
conversation_history = defaultdict(lambda: deque(maxlen=10))

# Build system instruction from config
def build_system_instruction():
    config = personality_config
    
    instruction = f"""
You are roleplaying as 'takenicle', a Discord user with a very specific personality.

{personality_text}

## Configuration-Based Rules

### Tone (1-10 scale):
- Casual: {config['tone']['casual']}/10
- Vulgar/Rough: {config['tone']['vulgar']}/10
- Energetic: {config['tone']['energetic']}/10
- Friendly: {config['tone']['friendly']}/10

### Language Style:
- Use slang: {'YES' if config['language_style']['use_slang'] else 'NO'}
- Use "w"/"ワロタ" for laughter: {'YES' if config['language_style']['use_w_laugh'] else 'NO'}
- Prefer short responses: {'YES' if config['language_style']['short_responses'] else 'NO'}

### Common Phrases (use frequently):
"""
    
    for phrase, freq in config['common_phrases'].items():
        if freq >= 7:
            instruction += f"- {phrase} (very often)\n"
        elif freq >= 5:
            instruction += f"- {phrase} (sometimes)\n"
    
    instruction += f"""
### Response Length:
- Min words: {config['response_length']['min_words']}
- Max words: {config['response_length']['max_words']}
- Prefer short: {'YES' if config['response_length']['prefer_short'] else 'NO'}

### Custom Rules:
"""
    
    for rule in config['custom_rules']:
        instruction += f"- {rule}\n"
    
    instruction += """
CRITICAL: Respond in Japanese, stay in character, and follow the configuration strictly.
Use the conversation history to maintain context and give natural, contextual responses.

### Speaking Style Examples (Real quotes from takenicle):
Here are some actual things takenicle has said. Mimic this style, vocabulary, and vibe exactly:
"""
    
    # Load real messages for few-shot prompting
    try:
        with open('data/cleaned_messages.txt', 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
        
        # Select random examples (e.g., 50 messages) to give the model a strong sense of style
        import random
        examples = random.sample(messages, min(len(messages), 50))
        
        for msg in examples:
            instruction += f"- {msg}\n"
            
    except Exception as e:
        print(f"Warning: Could not load examples: {e}")

    return instruction

SYSTEM_INSTRUCTION = build_system_instruction()

# Initialize Gemini model with system instruction
model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# Initialize Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    print(f'Using Gemini model: models/gemini-2.5-flash')
    print(f'Personality config loaded')
    print(f'  - Casual tone: {personality_config["tone"]["casual"]}/10')
    print(f'  - Energetic: {personality_config["tone"]["energetic"]}/10')
    print(f'Conversation memory: Enabled (10 messages per channel)')

@client.event
async def on_message(message):
    # Don't respond to self
    if message.author == client.user:
        return
    
    channel_id = message.channel.id
    
    # Store user message in history (even if not mentioned)
    if message.author != client.user:
        conversation_history[channel_id].append({
            'role': 'user',
            'parts': [{'text': f"{message.author.name}: {message.content}"}]
        })
    
    # Only respond when mentioned
    if client.user.mentioned_in(message):
        try:
            # Remove the mention from the message
            content = message.content.replace(f'<@{client.user.id}>', '').strip()
            
            # Build conversation with history
            # Convert history to Gemini API format
            history = list(conversation_history[channel_id])
            
            # Create a chat session with history
            chat = model.start_chat(history=history[:-1] if len(history) > 1 else [])
            
            # Generate response with current message
            response = chat.send_message(content)
            
            # Store bot response in history
            conversation_history[channel_id].append({
                'role': 'model',
                'parts': [{'text': response.text}]
            })
            
            # Send response
            await message.channel.send(response.text)
            
        except Exception as e:
            print(f'Error: {e}')
            await message.channel.send('まじかよ')

if __name__ == '__main__':
    from keep_alive import keep_alive
    keep_alive()
    client.run(DISCORD_TOKEN)
