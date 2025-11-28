import json
from collections import Counter, defaultdict
from datetime import datetime

print("Loading data...")
with open('data/all_server_messages.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total messages: {len(data)}")

# Analyze per user
user_stats = defaultdict(lambda: {
    'total_messages': 0,
    'channels': Counter(),
    'years': Counter(),
    'months': Counter(),
    'first_message': None,
    'last_message': None,
    'sample_messages': []
})

for msg in data:
    author = msg.get('author', 'Unknown')
    if author == 'Unknown':
        continue
    
    timestamp = msg.get('timestamp', '')
    channel = msg.get('channel_name', 'Unknown')
    content = msg.get('content', '')
    
    user_stats[author]['total_messages'] += 1
    user_stats[author]['channels'][channel] += 1
    
    if timestamp:
        year = timestamp[:4]
        month = timestamp[:7]
        user_stats[author]['years'][year] += 1
        user_stats[author]['months'][month] += 1
        
        if not user_stats[author]['first_message'] or timestamp < user_stats[author]['first_message']:
            user_stats[author]['first_message'] = timestamp
        if not user_stats[author]['last_message'] or timestamp > user_stats[author]['last_message']:
            user_stats[author]['last_message'] = timestamp
    
    # Store sample messages
    if len(user_stats[author]['sample_messages']) < 10 and content:
        user_stats[author]['sample_messages'].append({
            'timestamp': timestamp,
            'channel': channel,
            'content': content[:200]
        })

# Sort users by total messages
sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['total_messages'], reverse=True)

# Generate profiles
output = []
output.append("# AbsCL サーバーメンバープロフィール\n")
output.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
output.append(f"総メッセージ数: {len(data)}件\n")
output.append(f"分析対象ユーザー数: {len(user_stats)}名\n")
output.append("\n" + "="*80 + "\n\n")

for rank, (username, stats) in enumerate(sorted_users, 1):
    output.append(f"## {rank}. {username}\n\n")
    output.append(f"### 📊 基本統計\n")
    output.append(f"- **総メッセージ数**: {stats['total_messages']:,}件\n")
    
    if stats['first_message'] and stats['last_message']:
        first_date = stats['first_message'][:10]
        last_date = stats['last_message'][:10]
        output.append(f"- **初メッセージ**: {first_date}\n")
        output.append(f"- **最終メッセージ**: {last_date}\n")
    
    # Active years
    if stats['years']:
        years_str = ", ".join(sorted(stats['years'].keys()))
        output.append(f"- **活動年**: {years_str}\n")
    
    # Most active channels
    if stats['channels']:
        output.append(f"\n### 💬 よく使うチャンネル（上位5件）\n")
        for ch, count in stats['channels'].most_common(5):
            percentage = (count / stats['total_messages']) * 100
            output.append(f"- **{ch}**: {count}件 ({percentage:.1f}%)\n")
    
    # Yearly activity
    if stats['years']:
        output.append(f"\n### 📅 年別活動\n")
        for year in sorted(stats['years'].keys()):
            count = stats['years'][year]
            output.append(f"- **{year}年**: {count}件\n")
    
    # Most active months
    if stats['months']:
        output.append(f"\n### 🔥 最も活発だった月（上位5件）\n")
        for month, count in stats['months'].most_common(5):
            output.append(f"- **{month}**: {count}件\n")
    
    # Sample messages
    if stats['sample_messages']:
        output.append(f"\n### 💭 サンプルメッセージ\n")
        for i, msg in enumerate(stats['sample_messages'][:5], 1):
            date = msg['timestamp'][:10] if msg['timestamp'] else 'Unknown'
            channel = msg['channel']
            content = msg['content'].replace('\n', ' ')[:100]
            if content:
                output.append(f"{i}. [{date}] #{channel}\n")
                output.append(f"   > {content}\n\n")
    
    output.append("\n" + "-"*80 + "\n\n")

# Write to file
with open('data/absmember', 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print(f"\n✅ プロフィールを生成しました: data/absmember")
print(f"   ユーザー数: {len(user_stats)}名")
print(f"   上位10名:")
for rank, (username, stats) in enumerate(sorted_users[:10], 1):
    print(f"   {rank}. {username}: {stats['total_messages']:,}件")
