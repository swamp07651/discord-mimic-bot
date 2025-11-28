import json
import re
from collections import Counter, defaultdict
from datetime import datetime

# Expanded game keywords
GAMES = {
    'マインクラフト': ['マイクラ', 'minecraft', 'マインクラフト', 'クラフト', 'サバイバル', '建築'],
    'Valorant': ['valorant', 'ヴァロ', 'ヴァロラント', 'バロ', 'バロラント', 'valo'],
    'League of Legends': ['lol', 'リーグ', 'league', 'レーン', 'ジャングル', 'サポート'],
    'Apex Legends': ['apex', 'エペ', 'エーペックス'],
    '原神': ['原神', 'genshin', '璃月', '稲妻', 'スメール'],
    'モンスターハンター': ['モンハン', 'mh', 'モンスターハンター', 'ハンター'],
    'Palworld': ['palworld', 'パルワールド', 'パル'],
    'Tarkov': ['tarkov', 'タルコフ'],
    'Rainbow Six': ['r6', 'rainbow', 'レインボー', 'シージ'],
    'その他ゲーム': ['ゲーム', 'game', 'プレイ', 'やる', 'やろう']
}

# Expanded hobby/interest keywords
HOBBIES = {
    '配信': ['配信', 'stream', 'ストリーム', 'ライブ'],
    '動画': ['動画', 'youtube', 'ニコニコ', 'video'],
    '音楽': ['音楽', '曲', 'song', '歌', 'ボカロ', 'アーティスト'],
    'アニメ': ['アニメ', 'anime', '作画', '声優'],
    '映画': ['映画', 'movie', '映画館'],
    '漫画': ['漫画', 'マンガ', 'manga', 'コミック'],
    '本': ['本', '小説', '読書', 'book'],
    '料理': ['料理', '料理', '食べ物', 'レシピ'],
    '旅行': ['旅行', '旅', 'travel', '観光'],
    'スポーツ': ['スポーツ', 'サッカー', '野球', 'バスケ', '運動'],
    'イラスト': ['イラスト', '絵', '描く', 'draw', 'art'],
    '写真': ['写真', 'photo', 'カメラ', '撮影'],
    'プログラミング': ['プログラミング', 'コード', 'code', 'python', 'javascript', 'プログラム'],
    'VTuber': ['vtuber', 'にじさんじ', 'ホロライブ', 'vチューバー'],
    'Twitter/SNS': ['twitter', 'ツイート', 'x.com', 'インスタ', 'tiktok'],
    '雑談': ['雑談', 'おしゃべり', 'トーク'],
}

# Personality indicators (expanded)
PERSONALITY_PATTERNS = {
    '積極的': ['やろう', 'やりたい', '行く', '参加', 'いいね', 'やる'],
    'フレンドリー': ['ありがと', 'おつ', 'よろしく', 'おはよ', 'おやすみ', 'www', 'w', '笑', 'ｗ'],
    'リーダーシップ': ['みんな', '集合', '募集', '企画', '予定', '計画'],
    '分析的': ['どう思う', 'なぜ', 'なんで', '理由', '考え', 'どうして'],
    'クリエイティブ': ['作る', '建築', 'デザイン', '描く', '制作', '創作'],
    'サポート的': ['手伝う', '助ける', 'サポート', '大丈夫', 'どうした'],
    'ユーモラス': ['草', 'ww', 'www', '笑', 'ワロタ', 'クソ'],
    '真面目': ['確認', 'ルール', '注意', '禁止', '必要'],
}

# Role prediction based on activity patterns
def predict_role(stats):
    """Predict user's server role based on their activity"""
    roles = []
    
    # Admin/Moderator indicators
    if any(keyword in str(stats.get('message_samples', [])).lower() 
           for keyword in ['ルール', '禁止', '確認', 'サーバー', '管理']):
        roles.append('管理者・モデレーター候補')
    
    # Active gamer
    if stats.get('valid_messages', 0) > 2000:
        roles.append('超アクティブメンバー')
    elif stats.get('valid_messages', 0) > 1000:
        roles.append('アクティブメンバー')
    
    # Game specialist
    if stats.get('games'):
        top_game = stats['games'].most_common(1)[0]
        if top_game[1] > 30:
            roles.append(f'{top_game[0]}プレイヤー')
    
    # Content creator
    if any(stats.get('topics', {}).get(topic, 0) > 5 
           for topic in ['配信', '動画', 'イラスト']):
        roles.append('クリエイター')
    
    # Social butterfly
    if stats.get('personality_traits', {}).get('フレンドリー', 0) > 100:
        roles.append('ムードメーカー')
    
    # Leader
    if stats.get('personality_traits', {}).get('リーダーシップ', 0) > 20:
        roles.append('リーダー気質')
    
    # Long-term member
    years = len(stats.get('years', {}))
    if years >= 4:
        roles.append('古参メンバー')
    elif years >= 2:
        roles.append('中堅メンバー')
    
    return roles if roles else ['メンバー']

def is_bot_command(text):
    """Check if message is a bot command"""
    if not text:
        return True
    text = text.strip()
    if text.startswith(('!', '/', '.', '$', '>', '<@')):
        return True
    if text.startswith('http') and len(text.split()) == 1:
        return True
    if len(text) < 2:
        return True
    return False

def clean_message(text):
    """Remove URLs and mentions from message"""
    if not text:
        return ""
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'<@!?\d+>', '', text)
    text = re.sub(r'<#\d+>', '', text)
    text = re.sub(r'<:\w+:\d+>', '', text)  # Remove custom emojis
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
    'hobbies': Counter(),
    'personality_traits': Counter(),
    'message_samples': [],
    'years': Counter(),
    'months': Counter(),
    'first_message': None,
    'last_message': None,
})

for msg in data:
    author = msg.get('author', 'Unknown')
    if author == 'Unknown':
        continue
    
    content = msg.get('content', '')
    timestamp = msg.get('timestamp', '')
    
    user_analysis[author]['total_messages'] += 1
    
    if is_bot_command(content):
        continue
    
    cleaned = clean_message(content)
    if not cleaned or len(cleaned) < 3:
        continue
    
    user_analysis[author]['valid_messages'] += 1
    
    content_lower = content.lower()
    
    # Analyze games
    for game, keywords in GAMES.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                user_analysis[author]['games'][game] += 1
                break
    
    # Analyze hobbies
    for hobby, keywords in HOBBIES.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                user_analysis[author]['hobbies'][hobby] += 1
                break
    
    # Analyze personality
    for trait, patterns in PERSONALITY_PATTERNS.items():
        for pattern in patterns:
            if pattern in content_lower:
                user_analysis[author]['personality_traits'][trait] += 1
    
    # Store sample messages
    if len(user_analysis[author]['message_samples']) < 30:
        user_analysis[author]['message_samples'].append({
            'timestamp': timestamp,
            'content': cleaned[:200]
        })
    
    # Time tracking
    if timestamp:
        year = timestamp[:4]
        month = timestamp[:7]
        user_analysis[author]['years'][year] += 1
        user_analysis[author]['months'][month] += 1
        
        if not user_analysis[author]['first_message'] or timestamp < user_analysis[author]['first_message']:
            user_analysis[author]['first_message'] = timestamp
        if not user_analysis[author]['last_message'] or timestamp > user_analysis[author]['last_message']:
            user_analysis[author]['last_message'] = timestamp

# Sort users by valid messages
sorted_users = sorted(user_analysis.items(), 
                     key=lambda x: x[1]['valid_messages'], 
                     reverse=True)

# Generate detailed profiles
output = []
output.append("# AbsCL サーバーメンバー 超詳細プロフィール\n\n")
output.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
output.append(f"総メッセージ数: {len(data):,}件\n")
output.append(f"分析対象ユーザー数: {len(user_analysis)}名\n\n")
output.append("※ botコマンドとURLは除外して分析\n")
output.append("※ 趣味・性格は発言内容から自動推測\n\n")
output.append("="*80 + "\n\n")

for rank, (username, stats) in enumerate(sorted_users[:40], 1):
    if stats['valid_messages'] < 10:
        continue
    
    output.append(f"## {rank}. {username}\n\n")
    
    # Basic stats
    output.append(f"### 📊 基本統計\n")
    output.append(f"- **総メッセージ数**: {stats['total_messages']:,}件\n")
    output.append(f"- **分析対象メッセージ**: {stats['valid_messages']:,}件\n")
    
    if stats['first_message'] and stats['last_message']:
        first_date = stats['first_message'][:10]
        last_date = stats['last_message'][:10]
        output.append(f"- **初メッセージ**: {first_date}\n")
        output.append(f"- **最終メッセージ**: {last_date}\n")
    
    # Activity period
    if stats['years']:
        years_str = ", ".join(sorted(stats['years'].keys()))
        output.append(f"- **活動期間**: {years_str}\n")
    
    # Games (expanded)
    if stats['games']:
        output.append(f"\n### 🎮 プレイゲーム\n")
        for game, count in stats['games'].most_common(10):
            if count >= 3:
                output.append(f"- **{game}**: {count}回言及\n")
    
    # Hobbies (NEW - detailed)
    if stats['hobbies']:
        output.append(f"\n### 💡 趣味・興味\n")
        for hobby, count in stats['hobbies'].most_common(15):
            if count >= 3:
                output.append(f"- **{hobby}**: {count}回言及\n")
    
    # Personality (expanded)
    if stats['personality_traits']:
        output.append(f"\n### 🧠 性格分析\n")
        total_traits = sum(stats['personality_traits'].values())
        for trait, count in stats['personality_traits'].most_common(8):
            percentage = (count / total_traits) * 100
            if percentage >= 8:
                output.append(f"- **{trait}**: {percentage:.1f}% ({count}回)\n")
    
    # Most active months
    if stats['months']:
        output.append(f"\n### 📅 最も活発だった月（上位5件）\n")
        for month, count in stats['months'].most_common(5):
            output.append(f"- **{month}**: {count}件\n")
    
    # Sample messages (more samples)
    if stats['message_samples']:
        output.append(f"\n### 💬 メッセージサンプル（性格・趣味の参考）\n")
        for i, msg in enumerate(stats['message_samples'][:8], 1):
            content = msg['content']
            if content and len(content) > 5:
                date = msg['timestamp'][:10] if msg['timestamp'] else 'Unknown'
                output.append(f"{i}. [{date}] {content}\n")
    
    output.append("\n" + "-"*80 + "\n\n")

# Write detailed profile
with open('data/absmember', 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print(f"\n✅ 超詳細プロフィールを生成: data/absmember")

# Generate role predictions (separate file)
role_output = []
role_output.append("# AbsCL サーバーメンバー 役職予想\n\n")
role_output.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
role_output.append(f"※ 発言内容と活動パターンから自動予想\n")
role_output.append(f"※ あとで編集可能\n\n")
role_output.append("="*80 + "\n\n")

for rank, (username, stats) in enumerate(sorted_users[:40], 1):
    if stats['valid_messages'] < 10:
        continue
    
    roles = predict_role(stats)
    
    role_output.append(f"## {username}\n\n")
    role_output.append(f"### 予想される役職・特徴\n")
    for role in roles:
        role_output.append(f"- {role}\n")
    
    # Supporting evidence
    role_output.append(f"\n### 根拠\n")
    role_output.append(f"- メッセージ数: {stats['valid_messages']:,}件\n")
    role_output.append(f"- 活動年数: {len(stats['years'])}年\n")
    
    if stats['games']:
        top_games = [f"{g}({c}回)" for g, c in stats['games'].most_common(3)]
        role_output.append(f"- 主なゲーム: {', '.join(top_games)}\n")
    
    if stats['personality_traits']:
        top_traits = [f"{t}({c}回)" for t, c in stats['personality_traits'].most_common(3)]
        role_output.append(f"- 性格傾向: {', '.join(top_traits)}\n")
    
    role_output.append("\n" + "-"*80 + "\n\n")

# Write role predictions
with open('data/member_roles.txt', 'w', encoding='utf-8') as f:
    f.write(''.join(role_output))

print(f"✅ 役職予想を生成: data/member_roles.txt")
print(f"\n上位10名の役職予想:")
for rank, (username, stats) in enumerate(sorted_users[:10], 1):
    roles = predict_role(stats)
    print(f"   {rank}. {username}: {', '.join(roles)}")
