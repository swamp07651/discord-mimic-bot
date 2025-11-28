import discord
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class DataExtractor(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        
        all_messages = []
        
        for guild in self.guilds:
            print(f'Processing Guild: {guild.name} (ID: {guild.id})')
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).read_messages:
                    print(f'  - Fetching from: {channel.name} (ID: {channel.id})')
                    try:
                        count = 0
                        async for message in channel.history(limit=None): # Fetch all history
                            # if message.author.name == 'takenicle': # Filter removed to fetch ALL messages
                            if not message.author.bot and message.content: # Skip bots and empty messages
                                # Try to get roles if author is a Member
                                roles = []
                                if hasattr(message.author, 'roles'):
                                    roles = [role.name for role in message.author.roles]
                                
                                # Get attachments
                                attachments = [a.url for a in message.attachments]

                                all_messages.append({
                                    'author': message.author.name,
                                    'author_roles': roles,
                                    'content': message.content,
                                    'attachments': attachments,
                                    'channel': channel.name,
                                    'guild': guild.name,
                                    'timestamp': str(message.created_at)
                                })
                                count += 1
                                if count % 500 == 0:
                                    print(f'    Collected {count} messages... (Current: {message.created_at.strftime("%Y-%m-%d")})')
                                    with open('data/all_server_messages.json', 'w', encoding='utf-8') as f:
                                        json.dump(all_messages, f, ensure_ascii=False, indent=4)
                                    
                    except Exception as e:
                        print(f'    Failed to fetch from {channel.name}: {e}')

        with open('data/all_server_messages.json', 'w', encoding='utf-8') as f:
            json.dump(all_messages, f, ensure_ascii=False, indent=4)
        
        print(f'------\nSaved {len(all_messages)} messages to data/raw_messages.json')
        await self.close()

    async def close(self):
        # Ensure data is saved on close if not already
        # Note: This is a simple fallback; for robust interrupt handling, signal handlers are better,
        # but for this script, just ensuring we write before exit in normal flow is key.
        # The previous block writes at the end of on_ready.
        # If we want to save on interrupt, we need a try-finally in on_ready or a signal handler.
        await super().close()


if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.message_content = True # Required to read message content
    
    client = DataExtractor(intents=intents)
    client.run(TOKEN)
