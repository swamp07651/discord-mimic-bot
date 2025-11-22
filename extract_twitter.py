import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# ターゲットユーザー
TARGET_USER = "takenicle"  # ユーザー名をここに設定（必要に応じて変更）

def extract_tweets():
    print("Starting browser for Twitter extraction...")
    
    # ブラウザの起動（undetected-chromedriverを使用）
    options = uc.ChromeOptions()
    # options.add_argument("--headless") # ヘッドレスモードはログイン時に避ける
    
    driver = uc.Chrome(options=options)
    
    try:
        # Twitterログインページへ
        driver.get("https://twitter.com/login")
        print("Please login to Twitter in the browser window.")
        print("After logging in, press Enter here to continue...")
        input()
        
        # ターゲットユーザーのページへ移動
        print(f"Navigating to {TARGET_USER}'s profile...")
        driver.get(f"https://twitter.com/{TARGET_USER}")
        time.sleep(5)
        
        tweets = set()
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        print("Scrolling and collecting tweets...")
        # スクロールして収集（上限を設定）
        for i in range(50):  # 50回スクロール
            # ツイート要素を取得
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            
            # ツイートテキストを抽出（クラス名は変わる可能性があるため、data-testidを使用）
            tweet_elements = soup.find_all("div", {"data-testid": "tweetText"})
            
            for element in tweet_elements:
                text = element.get_text()
                if text and text not in tweets:
                    tweets.add(text)
                    print(f"Collected: {text[:30]}...")
            
            # スクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # スクロールしても変わらなければ終了
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
            print(f"Scroll {i+1}/50 - Total unique tweets: {len(tweets)}")
        
        # 保存
        with open("data/twitter_raw.json", "w", encoding="utf-8") as f:
            json.dump(list(tweets), f, ensure_ascii=False, indent=2)
            
        print(f"Saved {len(tweets)} tweets to data/twitter_raw.json")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Extraction finished. You can close the browser.")
        # driver.quit() # ユーザーに確認してから閉じる

if __name__ == "__main__":
    extract_tweets()
