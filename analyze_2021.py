import json
from collections import Counter
from datetime import datetime

print("Loading data...")
with open('data/all_server_messages.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total messages: {len(data)}")

# Filter 2021 messages
msgs_2021 = [m for m in data if m.get('timestamp', '').startswith('2021')]
print(f"\n2021年のメッセージ数: {len(msgs_2021)}")

if msgs_2021:
    dates = [m['timestamp'][:10] for m in msgs_2021]
    print(f"最古: {min(dates)}")
    print(f"最新: {max(dates)}")
    
    # Channel statistics
    channels = Counter([m.get('channel_name', 'Unknown') for m in msgs_2021])
    print(f"\nチャンネル別メッセージ数 (上位10件):")
    for ch, count in channels.most_common(10):
        print(f"  {ch}: {count}件")
    
    # Author statistics
    authors = Counter([m.get('author', 'Unknown') for m in msgs_2021])
    print(f"\nユーザー別メッセージ数 (上位10件):")
    for author, count in authors.most_common(10):
        print(f"  {author}: {count}件")
    
    # Monthly distribution
    months = Counter([m['timestamp'][:7] for m in msgs_2021])
    print(f"\n月別メッセージ数:")
    for month in sorted(months.keys()):
        print(f"  {month}: {months[month]}件")
    
    # Sample messages
    print(f"\n2021年のサンプルメッセージ (最初の5件):")
    for i, msg in enumerate(sorted(msgs_2021, key=lambda x: x['timestamp'])[:5]):
        print(f"\n{i+1}. [{msg['timestamp']}] {msg.get('author', 'Unknown')} in #{msg.get('channel_name', 'Unknown')}")
        content = msg.get('content', '')[:100]
        if content:
            print(f"   {content}")
else:
    print("2021年のメッセージが見つかりませんでした。")
