import json
import random

def main():
    input_file = 'data/cleaned_messages.txt'
    output_file = 'finetune_dataset.jsonl'
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    print(f"Loaded {len(messages)} messages.")
    
    training_data = []
    
    # システムプロンプト（短めに）
    system_instruction = "You are a Discord user named 'takenicle'. You speak in a casual, sometimes rough Japanese dialect. You love gaming (VALORANT, GTA) and often use slang."

    # データ生成ロジック
    # 実際の会話履歴がないため、擬似的な会話ペアを作成する
    # 方法: 
    # 1. メッセージをランダムに選んで「ユーザーの問いかけ」とし、次のメッセージを「返答」とする（文脈があると仮定）
    # 2. 一般的な挨拶や質問に対する返答としてメッセージを割り当てる
    
    # 今回はシンプルに、メッセージそのものを学習させるため、
    # "user": "（適当なプロンプト）", "model": "（メッセージ）" の形式にする
    # ただし、これだと「どんな質問にもこの口調で返す」という学習になる
    
    common_prompts = [
        "元気？", "何してる？", "最近どう？", "ゲームしようぜ", 
        "VALORANTやる？", "お腹すいた", "眠い", "暇", 
        "これ見て", "おはよう", "おやすみ", "つかれた"
    ]
    
    for i, msg in enumerate(messages):
        # 簡易的なデータセット作成
        # 実際には会話履歴があればベストだが、単発メッセージのスタイル学習として構成
        
        # ランダムなプロンプト、または前のメッセージをプロンプトにする（文脈学習）
        if i > 0 and random.random() < 0.3:
            user_input = messages[i-1] # 前の発言に対する返答として学習
        else:
            user_input = random.choice(common_prompts)

        # Gemini tuning data format (text_input -> output)
        # System instruction is implicitly handled or prepended
        
        full_input = f"{system_instruction}\n\nUser: {user_input}"
        
        entry = {
            "text_input": full_input,
            "output": msg
        }
        training_data.append(entry)

    # JSONLとして保存
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in training_data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
            
    print(f"Generated {len(training_data)} training examples in {output_file}")

if __name__ == '__main__':
    main()
