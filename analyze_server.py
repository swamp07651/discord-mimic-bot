import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

def analyze_server_logs():
    input_file = 'data/all_server_messages.json'
    output_file = 'data/server_report_full.md'
    
    print(f"Reading {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Run extract_data.py first.")
        return

    print(f"Loaded {len(messages)} messages.")
    
    # Intelligent sampling to reduce token count
    # Strategy: Sample evenly across time periods and prioritize absclmember messages
    print("Sampling messages for analysis...")
    
    # Separate by role
    absclmember_msgs = [m for m in messages if 'absclmember' in m.get('author_roles', [])]
    other_msgs = [m for m in messages if 'absclmember' not in m.get('author_roles', [])]
    
    # Sample: Take all absclmember (up to 5000) + sample from others
    sampled = absclmember_msgs[:5000]
    
    # Add diverse sample from others (every Nth message to get time diversity)
    if len(other_msgs) > 3000:
        step = len(other_msgs) // 3000
        sampled.extend(other_msgs[::step][:3000])
    else:
        sampled.extend(other_msgs)
    
    # Sort by timestamp
    sampled.sort(key=lambda x: x.get('timestamp', ''))
    
    print(f"Sampled {len(sampled)} messages for analysis.")
    
    # Format messages for analysis
    chat_log = []
    for msg in sampled:
        # Format: [Date] User (Roles): Content
        roles_str = f" ({', '.join(msg.get('author_roles', []))})" if msg.get('author_roles') else ""
        chat_log.append(f"[{msg['timestamp'][:10]}] {msg['author']}{roles_str}: {msg['content']}")
    
    full_log_text = "\n".join(chat_log)
    
    # If text is too long (approx char count check), we might warn or truncate.
    # 1 token ~ 4 chars. 1M tokens ~ 4M chars.
    if len(full_log_text) > 3000000:
        print("Warning: Log is very large. Truncating to last 3M characters to fit context...")
        full_log_text = full_log_text[-3000000:]

    print("Sending to Gemini for analysis (this may take a while)...")
    
    prompt = f"""
    あなたはマインクラフトRPGマップのクリエイティブなゲームデザイナーです。
    ユーザーはこのDiscordサーバーのコミュニティと歴史に基づいたゲームを作りたいと考えています。
    チャットログを分析し、**マインクラフトRPG設定資料**を生成してください。
    
    レポートには以下を含める必要があります（**すべて日本語で記述**）：
    
    # 1. メンバー参加順
    チャットログの最初の発言日時を基に、メンバーの参加順をリスト化してください。
    - **順位**: 1位、2位、3位...
    - **名前**:
    - **初登場日**: YYYY-MM-DD形式
    - **役職**: (absclmemberなど)
    
    # 2. キャラクタークラス設定（「AbsCL」パーティ）
    各主要メンバー（特に「absclmember」役職）について：
    - **名前とRPGクラス**: 性格/趣味に基づいてクラスを割り当て（例：パラディン、ネクロマンサー、吟遊詩人、レッドストーンエンジニア）
    - **アビリティ/スキル**: 名言や習慣に基づいた必殺技
    - **説明**: NPCまたはプレイアブルキャラクターとしての振る舞い
    
    # 3. ワールドの伝承と物語（サーバーの歴史）
    サーバーの歴史をファンタジー伝説に変換：
    - **始まり（2019年）**: 世界がどのように創造されたか
    - **時代区分**: 主要イベントを歴史的時代として記述（例：「ヴァロラントの時代」、「大論争」）
    - **現在の状態**: 今、世界はどうなっているか
    
    # 4. クエストと謎解き
    実際の会話/イベントに基づいて3〜5個のクエストアイデアを作成：
    - **クエスト名**:
    - **目的**: （例：「失われたミームを取り戻せ」、「レイドボスを倒せ」）
    - **背景**: これが基づいている実際のイベント
    
    # 5. 伝説のアイテム
    内輪ネタや好きなゲームに基づいてアイテムを作成：
    - **アイテム名**:
    - **効果**:
    - **由来**: なぜこのアイテムが存在するのか
    
    # 6. ユーザー関係性（パーティダイナミクス）
    - 切っても切れないデュオは誰？
    - ライバル関係は？
    
    ---
    **チャットログ:**
    {full_log_text}
    """
    
    model = genai.GenerativeModel("models/gemini-1.5-pro") # Use Pro for better reasoning on large data
    
    try:
        response = model.generate_content(prompt)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"Analysis complete! Report saved to {output_file}")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        # Fallback to Flash if Pro fails or quota issues
        print("Retrying with Gemini 1.5 Flash...")
        try:
            model_flash = genai.GenerativeModel("models/gemini-2.5-flash")
            response = model_flash.generate_content(prompt)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Analysis complete (Flash)! Report saved to {output_file}")
        except Exception as e2:
            print(f"Flash also failed: {e2}")

if __name__ == "__main__":
    analyze_server_logs()
