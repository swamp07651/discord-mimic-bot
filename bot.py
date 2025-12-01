import discord
from discord import app_commands
from discord.ext import commands
import os
import google.generativeai as genai
from dotenv import load_dotenv
from personality_manager import PersonalityManager
from collections import defaultdict, deque
import json
import datetime
import sys

load_dotenv()

# Configure API keys
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Personality Manager
pm = PersonalityManager()
try:
    pm.load_personality('takenicle')
except Exception as e:
    print(f"Failed to load default personality: {e}")

# Conversation memory: channel_id -> deque of (role, content) tuples (last 10 messages per channel)
conversation_history = defaultdict(lambda: deque(maxlen=10))

# Build system instruction from config
def build_system_instruction():
    p_data = pm.get_current_config()
    if not p_data:
        return "Error: No personality loaded."
    
    config = p_data['config']
    personality_text = p_data.get('analysis', '')

    instruction = f"""
You are roleplaying as '{p_data.get('name', 'Unknown')}', a Discord user with a very specific personality.

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
### Speaking Style Examples (Real quotes from {p_data.get('name', 'Unknown')}):
Here are some actual things {p_data.get('name', 'Unknown')} has said. Mimic this style, vocabulary, and vibe exactly:
"""
    # Use examples from the loaded personality config
    examples_dict = p_data.get('examples', {})
    all_examples = []
    for category, msgs in examples_dict.items():
        if isinstance(msgs, list):
            all_examples.extend(msgs)
    
    import random
    if all_examples:
        # Shuffle and pick up to 50 examples
        selected_examples = random.sample(all_examples, min(len(all_examples), 50))
        for msg in selected_examples:
            instruction += f"- {msg}\n"
    else:
        # Fallback if no examples found in JSON
        instruction += "- (No specific examples found in configuration)\n"
    
    return instruction

SYSTEM_INSTRUCTION = build_system_instruction()

# Initialize Gemini model with system instruction
model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# Initialize Discord client with commands extension
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Enable members intent for permission checks
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Using Gemini model: models/gemini-2.5-flash')
    print(f"Personality loaded: {pm.current_personality_name}")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Slash Command: Mimic
@bot.tree.command(name="mimic", description="Switch the bot's personality")
@app_commands.describe(name="The name of the personality to switch to")
async def mimic(interaction: discord.Interaction, name: str):
    await interaction.response.defer()
    target_name = name.strip()
    try:
        pm.load_personality(target_name)
        global SYSTEM_INSTRUCTION, model
        SYSTEM_INSTRUCTION = build_system_instruction()
        model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        msg = f"Personality switched to: {target_name}"
        
        # Change nickname
        if interaction.guild:
            new_nick = f"BOT{{{target_name}}}"
            try:
                await interaction.guild.me.edit(nick=new_nick)
                msg += f"\nNickname changed to: {new_nick}"
            except discord.Forbidden:
                msg += "\n(Nickname change failed: Missing permissions)"
            except Exception as e:
                print(f"Failed to change nickname: {e}")
        
        await interaction.followup.send(msg)
        print(f"Switched personality to {target_name}")
        
    except FileNotFoundError:
        await interaction.followup.send(f"Personality '{target_name}' not found.")
    except Exception as e:
        await interaction.followup.send(f"Error switching personality: {e}")

# Autocomplete for mimic command
@mimic.autocomplete('name')
async def mimic_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    personalities = pm.list_personalities()
    return [
        app_commands.Choice(name=p, value=p)
        for p in personalities if current.lower() in p.lower()
    ]

# Slash Command: Mimic List
@bot.tree.command(name="mimic_list", description="List available personalities")
async def mimic_list(interaction: discord.Interaction):
    personalities = pm.list_personalities()
    await interaction.response.send_message(f"Available personalities: {', '.join(personalities)}")

# Text Command: Mimic
@bot.command(name="mimic")
async def mimic_text(ctx, name: str):
    target_name = name.strip()
    try:
        pm.load_personality(target_name)
        global SYSTEM_INSTRUCTION, model
        SYSTEM_INSTRUCTION = build_system_instruction()
        model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        msg = f"Personality switched to: {target_name}"
        
        # Change nickname
        if ctx.guild:
            new_nick = f"BOT{{{target_name}}}"
            try:
                await ctx.guild.me.edit(nick=new_nick)
                msg += f"\nNickname changed to: {new_nick}"
            except discord.Forbidden:
                msg += "\n(Nickname change failed: Missing permissions)"
            except Exception as e:
                print(f"Failed to change nickname: {e}")
        
        await ctx.send(msg)
        print(f"Switched personality to {target_name}")
        
    except FileNotFoundError:
        await ctx.send(f"Personality '{target_name}' not found.")
    except Exception as e:
        await ctx.send(f"Error switching personality: {e}")

# Text Command: Mimic List
@bot.command(name="mimic_list")
async def mimic_list_text(ctx):
    personalities = pm.list_personalities()
    await ctx.send(f"Available personalities: {', '.join(personalities)}")

# Command: Restart (Admin only)
@bot.command(name="restart", aliases=['kill'])
async def restart(ctx):
    # Check for Administrator permission
    if ctx.author.guild_permissions.administrator:
        await ctx.send('再起動します...')
        print(f"Restart initiated by {ctx.author.name}")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        # Debug: Show what permissions the bot sees
        perms = [p[0] for p in ctx.author.guild_permissions if p[1]]
        await ctx.send(f'権限がありません。管理者のみ実行可能です。\n認識されている権限: {", ".join(perms) if perms else "なし"}')

# Error handler for other commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('権限がありません。')
    print(f"Command error: {error}")

# Command: Secret Analyze
@bot.command(name="secret_analyze")
async def secret_analyze(ctx):
    if not ctx.guild:
        await ctx.send('DMじゃ無理だわ。サーバーでやってくれ。')
        return
    await ctx.send('おっ、ガチ分析始めるか... ログ漁るから時間かかるぞ。')
    print(f"Starting deep analysis for guild: {ctx.guild.name}")
    try:
        guild = ctx.guild
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
        await ctx.send(f"分析完了。レポート書いといたぞ: `{output_path}`\n中身見てみろよ、面白いもんあるかもな。")
        print(f"Report saved to {output_path}")
    except Exception as e:
        print(f"Analysis failed: {e}")
        await ctx.send(f"わりぃ、分析失敗したわ: {e}")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Process commands first
    await bot.process_commands(message)

    # "Mama" Auto-reply for specific user
    if "一生奈良素敵大" in message.author.display_name or "一生奈良素敵大" in message.author.name:
        if message.content == "ママー！":
            await message.channel.send("はいはい、ママでちゅよ♡")
            return

    # Store user message in history
    channel_id = message.channel.id
    if message.author != bot.user:
        conversation_history[channel_id].append({
            'role': 'user',
            'parts': [{'text': f"{message.author.name}: {message.content}"}]
        })

    # Determine if bot should respond
    should_respond = bot.user.mentioned_in(message)
    
    # Also respond if it's a reply to the bot
    if not should_respond and message.reference:
        try:
            replied_msg = await message.channel.fetch_message(message.reference.message_id)
            if replied_msg.author == bot.user:
                should_respond = True
        except Exception as e:
            print(f"Error fetching replied message: {e}")
            pass

    # Respond logic
    if should_respond:
        try:
            # Remove the mention from the message if present
            content = message.content.replace(f'<@{bot.user.id}>', '').strip()
            
            # Identify user context from personality_config AND profiles.json
            user_context = ""
            author_name = message.author.name
            author_display = message.author.display_name
            author_id = str(message.author.id)
            
            # 1. Static Config (personality_config.py)
            found_member = None
            current_config = pm.get_current_config()['config']
            for key, info in current_config['server_members'].items():
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
    bot.run(DISCORD_TOKEN)
