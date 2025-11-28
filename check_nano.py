import json

with open('data/all_server_messages.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nano_msgs = [m for m in data if m.get('author') == 'nanobananapro']

if nano_msgs:
    print(f"nanobananapro のメッセージ数: {len(nano_msgs)}")
    timestamps = [m['timestamp'][:10] for m in nano_msgs if m.get('timestamp')]
    if timestamps:
        print(f"最古: {min(timestamps)}")
        print(f"最新: {max(timestamps)}")
    
    # Sample messages
    print("\nサンプルメッセージ:")
    for i, msg in enumerate(nano_msgs[:5], 1):
        content = msg.get('content', '')[:100]
        timestamp = msg.get('timestamp', '')[:10]
        if content:
            print(f"{i}. [{timestamp}] {content}")
else:
    print("nanobananapro のメッセージが見つかりませんでした")
