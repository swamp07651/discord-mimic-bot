import json
import re
from collections import Counter, defaultdict
from datetime import datetime

# Game keywords
GAMES = {
    'マインクラフト': ['マイクラ', 'minecraft', 'マインクラフト', 'クラフト'],
    'Valorant': ['valorant', 'ヴァロ', 'ヴァロラント', 'バロ', 'バロラント'],
    'League of Legends': ['lol', 'リーグ', 'league'],
    'Apex Legends': ['apex', 'エペ', 'エーペックス'],
    '原神': ['原神', 'genshin'],
    'モンスターハンター': ['モンハン', 'mh', 'モンスターハンター'],
    'Palworld': ['palworld', 'パルワールド'],
    'その他ゲーム': ['ゲーム', 'game', 'プレイ', 'やる']
}

# Personality indicators
PERSONALITY_PATTERNS = {
    '積極的': ['やろう', 'やりたい', '行く', '参加', 'いいね'],
    'フレンドリー': ['ありがと', 'おつ', 'よろしく', 'おはよ', 'おやすみ', 'www', 'w', '笑'],
    'リーダーシップ': ['みんな', '集合', '募集', '企画', '予定'],
    '分析的': ['どう思う', 'なぜ', 'なんで', '理由', '考え'],
    'クリエイティブ': ['作る', '建築', 'デザイン', '描く', '制作'],
    'サポート的': ['手伝う', '助ける', 'サポート', '大丈夫'],
}

def is_bot_command(text):
    """Check if message is a bot command"""
    if not text:
        return True
    text = text.strip()
    # Bot commands
    if text.startswith(('!', '/', '.', '$', '>', '<@')):
        return True
    # Only URLs
    if text.startswith('http') and len(text.split()) == 1:
        return True
    # Very short messages
    if len(text) < 2:
        return True
    return False

def clean_message(text):
    """Remove URLs and mentions from message"""
    if not text:
        return ""
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    # Remove mentions
    text = re.sub(r'<@!?\d+>', '', text)
    # Remove channel mentions
    text = re.sub(r'<#\d+>', '', text)
    return text.strip()

print("Loading data...")
with open('data/all_server_messages.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total messages: {len(data)}")

# Analyze per user
user_analysis = defaultdict(lambda: {
    'total_messages': 0,
    'valid_messages': 0,
    'games': Counter(),
    'personality_traits': Counter(),
    'topics': Counter(),
    'message_samples': [],
    'years': Counter(),
})

for msg in data:
    author = msg.get('author', 'Unknown')
    if author == 'Unknown':
        continue
    
    content = msg.get('content', '')
    timestamp = msg.get('timestamp', '')
    
    user_analysis[author]['total_messages'] += 1
    
    # Skip bot commands and URLs
    if is_bot_command(content):
        continue
    
    cleaned = clean_message(content)
    if not cleaned or len(cleaned) < 3:
        continue
    
    user_analysis[author]['valid_messages'] += 1
    
    # Analyze games
    content_lower = content.lower()
    for game, keywords in GAMES.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                user_analysis[author]['games'][game] += 1
                break
    
    # Analyze personality
    for trait, patterns in PERSONALITY_PATTERNS.items():
        for pattern in patterns:
            if pattern in content_lower:
                user_analysis[author]['personality_traits'][trait] += 1
    
    # Extract topics (nouns and keywords)
    # Simple keyword extraction
    keywords = ['配信', '動画', '音楽', 'アニメ', '映画', '漫画', '本', '料理', 
                '旅行', 'スポーツ', 'イラスト', '写真', 'プログラミング', 'コード']
    for keyword in keywords:
        if keyword in content:
            user_analysis[author]['topics'][keyword] += 1
    
    # Store sample messages
    if len(user_analysis[author]['message_samples']) < 20:
        user_analysis[author]['message_samples'].append({
            'timestamp': timestamp,
            'content': cleaned[:150]
        })
    
    # Year tracking
    if timestamp:
        year = timestamp[:4]
        user_analysis[author]['years'][year] += 1

# Sort users by valid messages
sorted_users = sorted(user_analysis.items(), 
                     key=lambda x: x[1]['valid_messages'], 
                     reverse=True)

# Generate enhanced profiles
output = []
output.append("# AbsCL サーバーメンバー詳細プロフィール\n")
output.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
output.append(f"総メッセージ数: {len(data)}件\n")
output.append(f"分析対象ユーザー数: {len(user_analysis)}名\n\n")
output.append("※ botコマンドとURLは除外して分析しています\n")
output.append("\n" + "="*80 + "\n\n")

for rank, (username, stats) in enumerate(sorted_users[:30], 1):  # Top 30 users
    if stats['valid_messages'] < 10:  # Skip users with too few messages
        continue
    
    output.append(f"## {rank}. {username}\n\n")
    
    # Basic stats
    output.append(f"### 📊 基本統計\n")
    output.append(f"- **総メッセージ数**: {stats['total_messages']:,}件\n")
    output.append(f"- **分析対象メッセージ**: {stats['valid_messages']:,}件\n")
    
    # Games
    if stats['games']:
        output.append(f"\n### 🎮 よくプレイするゲーム\n")
        for game, count in stats['games'].most_common(5):
            if count >= 3:  # Only show if mentioned 3+ times
                output.append(f"- **{game}**: {count}回言及\n")
    
    # Personality
    if stats['personality_traits']:
        output.append(f"\n### 🧠 性格分析\n")
        total_traits = sum(stats['personality_traits'].values())
        for trait, count in stats['personality_traits'].most_common(5):
            percentage = (count / total_traits) * 100
            if percentage >= 10:  # Only show significant traits
                output.append(f"- **{trait}**: {percentage:.1f}%\n")
    
    # Topics/Hobbies
    if stats['topics']:
        output.append(f"\n### 💡 興味・趣味\n")
        for topic, count in stats['topics'].most_common(5):
            if count >= 3:
                output.append(f"- **{topic}**: {count}回言及\n")
    
    # Activity years
    if stats['years']:
        years_str = ", ".join(sorted(stats['years'].keys()))
        output.append(f"\n### 📅 活動期間\n")
        output.append(f"- {years_str}\n")
    
    # Sample messages for context
    if stats['message_samples']:
        output.append(f"\n### 💬 メッセージサンプル（性格・趣味の参考）\n")
        for i, msg in enumerate(stats['message_samples'][:5], 1):
            content = msg['content']
            if content and len(content) > 5:
                date = msg['timestamp'][:10] if msg['timestamp'] else 'Unknown'
                output.append(f"{i}. [{date}] {content}\n")
    
    output.append("\n" + "-"*80 + "\n\n")

# Write to file
with open('data/absmember', 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print(f"\n✅ 詳細プロフィールを生成しました: data/absmember")
print(f"   分析対象ユーザー数: {len([u for u in user_analysis.values() if u['valid_messages'] >= 10])}名")
print(f"\n上位10名:")
for rank, (username, stats) in enumerate(sorted_users[:10], 1):
    games_str = ", ".join([g for g, _ in stats['games'].most_common(3)])
    print(f"   {rank}. {username}: {stats['valid_messages']:,}件")
    if games_str:
        print(f"      ゲーム: {games_str}")
