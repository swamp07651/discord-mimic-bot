import discord
import os
import google.generativeai as genai
from dotenv import load_dotenv
from personality_config import personality_config, example_responses
from collections import defaultdict, deque
import json
import datetime

load_dotenv()

# Configure API keys
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)

# Load personality analysis
with open('personality_analysis.md', 'r', encoding='utf-8') as f:
    personality_text = f.read()

# Conversation memory: channel_id -> deque of (role, content) tuples (last 10 messages per channel)
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
    instruction += """
"""
    instruction += """
### Response Length:
- Min words: {config['response_length']['min_words']}
- Max words: {config['response_length']['max_words']}
- Prefer short: {'YES' if config['response_length']['prefer_short'] else 'NO'}
"""
    instruction += """
### Custom Rules:
"""
    for rule in config['custom_rules']:
        instruction += f"- {rule}\n"
    instruction += """
"""
    instruction += "CRITICAL: Respond in Japanese, stay in character, and follow the configuration strictly.\nUse the conversation history to maintain context and give natural, contextual responses.\n"
    instruction += """
### Speaking Style Examples (Real quotes from takenicle):
Here are some actual things takenicle has said. Mimic this style, vocabulary, and vibe exactly:
"""
    try:
        with open('data/cleaned_messages.txt', 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
        import random
        examples = random.sample(messages, min(len(messages), 50))
        for msg in examples:
            instruction += f"- {msg}\n"
    except Exception as e:
        print(f"Warning: Could not load examples: {e}")

    # Add dynamic context
    current_hour = datetime.datetime.now().hour
    time_desc = "深夜 (Late Night)" if 0 <= current_hour < 5 else \
                "朝 (Morning)" if 5 <= current_hour < 11 else \
                "昼 (Daytime)" if 11 <= current_hour < 17 else \
                "夕方/夜 (Evening/Night)"
    
    instruction += f"""
### Current Context:
- Time: {time_desc} (Hour: {current_hour})
- Status: Chilling on Discord

### CRITICAL ROLEPLAY RULES:
1. **ABSOLUTELY NO POLITE JAPANESE (Desu/Masu)**. Use casual "Tameguchi" (e.g., "だね", "じゃん", "だよ").
2. **You are NOT an AI**. Never say "As an AI" or offer to "assist". You are just a guy hanging out.
3. **Be Imperfect**. Real humans make typos, use fragments, and don't write essays.
4. **React Naturally**. If someone says something funny, laugh ("w" or "草"). If they say something weird, say "きしょ".
5. **Match the Vibe**. If the user is hyped, be hyped. If they are chill, be chill.
"""
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
import discord
import os
import google.generativeai as genai
from dotenv import load_dotenv
from personality_config import personality_config, example_responses
from collections import defaultdict, deque
import json
import datetime

load_dotenv()

# Configure API keys
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)

# Load personality analysis
with open('personality_analysis.md', 'r', encoding='utf-8') as f:
    personality_text = f.read()

# Conversation memory: channel_id -> deque of (role, content) tuples (last 10 messages per channel)
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
    instruction += """
"""
    instruction += """
### Response Length:
- Min words: {config['response_length']['min_words']}
- Max words: {config['response_length']['max_words']}
- Prefer short: {'YES' if config['response_length']['prefer_short'] else 'NO'}
"""
    instruction += """
### Custom Rules:
"""
    for rule in config['custom_rules']:
        instruction += f"- {rule}\n"
    instruction += """
"""
    instruction += "CRITICAL: Respond in Japanese, stay in character, and follow the configuration strictly.\nUse the conversation history to maintain context and give natural, contextual responses.\n"
    instruction += """
### Speaking Style Examples (Real quotes from takenicle):
Here are some actual things takenicle has said. Mimic this style, vocabulary, and vibe exactly:
"""
    try:
        with open('data/cleaned_messages.txt', 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
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
    print('Using Gemini model: models/gemini-2.5-flash')
    print('Personality config loaded')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Hidden restart command (owner only)
    if message.content == '!restart':
        OWNER_ID = 123456789012345678  # TODO: replace with actual owner ID
        if message.author.id != OWNER_ID:
            await message.channel.send('権限がありません。')
            return
        await message.channel.send('再起動します...')
        import sys, os
        os.execv(sys.executable, [sys.executable] + sys.argv)
        return

    # Hidden command for server analysis
    if message.content == '!secret_analyze':
        if not message.guild:
            await message.channel.send('DMじゃ無理だわ。サーバーでやってくれ。')
            return
        await message.channel.send('おっ、ガチ分析始めるか... ログ漁るから時間かかるぞ。')
        print(f"Starting deep analysis for guild: {message.guild.name}")
        try:
            guild = message.guild
            print('Fetching messages...')
            chat_log = []
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).read_messages:
                    try:
                        async for msg in channel.history(limit=500):
                            if not msg.author.bot and msg.content:
                                chat_log.append(f"[{msg.created_at.strftime('%Y-%m-%d')}] {msg.author.name}: {msg.content}")
                    except Exception as e:
                        print(f"Skipped {channel.name}: {e}")
            chat_log.sort()
            full_log_text = "\n".join(chat_log)
            print(f"Collected {len(chat_log)} messages. Sending to Gemini...")
            analysis_prompt = f"""
You are an expert community analyst. Analyze the following Discord chat log and generate a detailed report in Markdown format.

The report MUST include:

# 1. Member Profiles
For each active member found in the logs (infer from their messages), list:
- **Name**
- **Hobbies/Interests** (Infer from their conversations)
- **Personality/Vibe**
- **Notable Quotes** (if any)

# 2. Server History (Chronological)
Summarize the server's history based on the logs. Divide into time periods (e.g., by month or major event).
- **Games Played**: What games were they playing?
- **Topics**: What were they talking about?
- **Events**: Any memorable moments?

# 3. Overall Vibe
A brief summary of the server's atmosphere.

---
**Chat Log:**
{full_log_text}
"""
            analysis_model = genai.GenerativeModel("models/gemini-2.5-flash")
            response = analysis_model.generate_content(analysis_prompt)
            output_path = 'data/server_report.md'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            await message.channel.send(f"分析完了。レポート書いといたぞ: `{output_path}`\n中身見てみろよ、面白いもんあるかもな。")
            print(f"Report saved to {output_path}")
        except Exception as e:
            print(f"Analysis failed: {e}")
            await message.channel.send(f"わりぃ、分析失敗したわ: {e}")
        return

    # Store user message in history
    channel_id = message.channel.id
    if message.author != client.user:
        conversation_history[channel_id].append({
            'role': 'user',
            'parts': [{'text': f"{message.author.name}: {message.content}"}]
        })

    # Determine if bot should respond
    should_respond = client.user.mentioned_in(message)
    
    # Also respond if it's a reply to the bot
    if not should_respond and message.reference:
        try:
            if replied_msg.author == client.user:
                should_respond = True
        except:
            pass

    # Respond logic
    if should_respond:
        try:
            # Remove the mention from the message if present
            content = message.content.replace(f'<@{client.user.id}>', '').strip()
            
            # Identify user context from personality_config AND profiles.json
            user_context = ""
            author_name = message.author.name
            author_display = message.author.display_name
            author_id = str(message.author.id)
            
            # 1. Static Config (personality_config.py)
            found_member = None
            for key, info in personality_config['server_members'].items():
                if key.lower() in author_name.lower() or key.lower() in author_display.lower():
                    found_member = info
                    break
            
            # 2. Dynamic Profile (profiles.json)
            dynamic_profile = {}
            try:
                with open('profiles.json', 'r', encoding='utf-8') as pf:
                    all_profiles = json.load(pf)
                    dynamic_profile = all_profiles.get(author_id, {})
            except (FileNotFoundError, json.JSONDecodeError):
                all_profiles = {}

            # Construct Context String
            user_context_parts = []
            user_context_parts.append(f"User: {author_display} ({author_name})")
            
            if found_member:
                user_context_parts.append(f"Relationship: {found_member.get('relationship', 'Unknown')}")
                user_context_parts.append(f"Tone: {found_member.get('tone_with_them', 'Casual')}")
                user_context_parts.append(f"Static Interests: {found_member.get('interests', '')}")
            
            if dynamic_profile:
                # Add learned info
                if 'notes' in dynamic_profile:
                    user_context_parts.append(f"Learned Memory: {', '.join(dynamic_profile['notes'])}")
                for k, v in dynamic_profile.items():
                    if k != 'notes':
                        user_context_parts.append(f"{k}: {v}")

            user_context_str = "\n".join(user_context_parts)
            
            system_note = f"""
[System Note: You are talking to a specific user.
{user_context_str}

**MEMORY UPDATE INSTRUCTION**:
If you learn something NEW and IMPORTANT about this user during this conversation (e.g., their hobby, favorite game, birthday, or a specific preference), output a memory tag at the END of your response like this:
[[MEMORY: The user likes sushi]]
[[MEMORY: The user is good at Valorant]]
This tag will be hidden from the user but saved to your memory. Only use it for NEW information.]
"""
            
            # Build conversation with history
            history = list(conversation_history[channel_id])
            
            # Create a chat session with history
            chat = model.start_chat(history=history[:-1] if len(history) > 1 else [])
            
            # Combine user context with content
            final_prompt = f"{system_note}\n{content}"
            
            # Generate response
            response = chat.send_message(final_prompt)
            response_text = response.text
            
            # Parse and Save Memory
            import re
            memory_matches = re.findall(r'\[\[MEMORY: (.*?)\]\]', response_text)
            if memory_matches:
                # Remove tags from output
                response_text = re.sub(r'\[\[MEMORY: .*?\]\]', '', response_text).strip()
                
                # Update profiles.json
                try:
                    with open('profiles.json', 'r', encoding='utf-8') as pf:
                        current_profiles = json.load(pf)
                except (FileNotFoundError, json.JSONDecodeError):
                    current_profiles = {}
                
                user_p = current_profiles.get(author_id, {})
                if 'notes' not in user_p:
                    user_p['notes'] = []
                
                for mem in memory_matches:
                    if mem not in user_p['notes']:
                        user_p['notes'].append(mem)
                        print(f"Learned new info about {author_name}: {mem}")
                
                current_profiles[author_id] = user_p
                with open('profiles.json', 'w', encoding='utf-8') as pf:
                    json.dump(current_profiles, pf, ensure_ascii=False, indent=2)

            # Store bot response in history (clean text)
            conversation_history[channel_id].append({
                'role': 'model',
                'parts': [{'text': response_text}]
            })
            
            # Send response
            if response_text:
                await message.channel.send(response_text)
            
        except Exception as e:
            print(f'Error: {e}')
            await message.channel.send('まじかよ')

if __name__ == '__main__':
    from keep_alive import keep_alive
    keep_alive()
    client.run(DISCORD_TOKEN)
