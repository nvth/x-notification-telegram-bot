import sqlite3
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import config_auth, tele_data
import time
from telegram import Bot

# init chrominum
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)  # init driver

# Config
USERNAME, PASSWORD, CRAWL_INTERVAL, YOUR_USERNAME = config_auth()
TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID = tele_data()

telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN) 

# local variable save data target users from db
target_users = []
crawl_thread = None  # multi-thread

# dbconnect
def init_db():
    conn = sqlite3.connect('tweets.db')
    cursor = conn.cursor()
    # Create table tweets if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,  
            time TEXT NOT NULL UNIQUE,
            text TEXT NOT NULL,
            link TEXT NOT NULL UNIQUE
        )
    ''')
    # # Create table tweets if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE 
        )
    ''')
    conn.commit()
    return conn, cursor

# getter user list form database
def load_users(cursor):
    cursor.execute('SELECT username FROM users')
    return [row[0] for row in cursor.fetchall()]

# insert user follow from input
def save_user(cursor, username):
    cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (username,))

# remove user follow
def delete_user(cursor, username):
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))

# X-Logging in
def login_twitter(username, your_username, password):
    try:
        driver.get("https://twitter.com/login")
        print("🔄 Loggin in ...")

        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)
        print("✅ Entering username...")
        # enter username or phone or email
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "text"))
            ).send_keys(your_username) # send entered username or phone or email
            # next button using html inspector
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@role='button']//span[contains(text(), 'Next')]"))
            )
            next_button.click()
            print("✅ email and phone number entered.")
        except Exception as e:
            print(f"❌ Failed: {e}")
            raise

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        print("✅ Logged")

        # Kiểm tra đăng nhập thành công
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/home']"))
        )
        print("🎉 Login success!")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        #driver.save_screenshot("login_error.png")  # ChatGPT debug chu khong biet den ham nay
        driver.quit()
        exit()

# Check item from database is exist
def is_tweet_exists(cursor, time, link):
    cursor.execute('SELECT id FROM tweets WHERE time = ? OR link = ?', (time, link))
    return cursor.fetchone() is not None

# sent message to telegram
def send_to_telegram(username, text, link):
    try:
        message = f"📢 @{username} posted:\n\n{text}\n\n🔗 Link_post: {link}"
        telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("✅ Sended.")
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")

# crawl newest post
def crawl_tweets(target_user, cursor):
    try:
        driver.get(f"https://twitter.com/{target_user}")
        print(f"🔄 Gathering @{target_user}...")

        # searching tweets , 20 or anything to your network speed mtfk
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
        )

        # gathering tweets - right now is 2 post, if wanna 5 post edit this [:2] to 5 [:5]
        tweets = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')[:2]
        for tweet in tweets:
            try:
                tweet_text = tweet.find_element(By.CSS_SELECTOR, 'div[lang]').text
                tweet_time = tweet.find_element(By.TAG_NAME, "time").get_attribute("datetime")
                tweet_link = tweet.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]').get_attribute("href")
                print(f"Username: @{target_user}")
                print(f"Time: {tweet_time}")
                print(f"Text: {tweet_text}")
                print(f"Link: {tweet_link}")
                print("-" * 50)

                # Check tweets is exists
                if not is_tweet_exists(cursor, tweet_time, tweet_link):
                    # if not, save to database
                    cursor.execute('''
                        INSERT INTO tweets (username, time, text, link) VALUES (?, ?, ?, ?)
                    ''', (target_user, tweet_time, tweet_text, tweet_link))
                    print("✅ Saved to database.")

                    # sent to user telegram
                    send_to_telegram(target_user, tweet_text, tweet_link)
                else:
                    print("🟡 The Post is existing in database, skipping.")
            except Exception as e:
                print(f"❌ err: {e}")
    except Exception as e:
        print(f"❌ err crawl @{target_user}: {e}")
        #driver.save_screenshot(f"error_{target_user}.png")  # ChatGPT nhe :))

# add user from database
def add_user(user_input):
    global target_users
    new_users = [username.strip() for username in user_input.split(",")]

    conn, cursor = init_db()
    for user in new_users:
        if user not in target_users:
            target_users.append(user)
            save_user(cursor, user)
    conn.commit()
    conn.close()

# remove user from database
def remove_user(user_input):
    global target_users
    users_to_remove = [username.strip() for username in user_input.split(",")]

    conn, cursor = init_db()
    for user in users_to_remove:
        if user in target_users:
            target_users.remove(user)
            delete_user(cursor, user)
    conn.commit()
    conn.close()

# get list user from database
def list_users():
    global target_users
    return target_users

# crawl multi threading
def start_crawl():
    global target_users, crawl_thread
    if not target_users:
        print("❌ Please add atleast a uuser.")
        return

    # multi threading crawl run
    crawl_thread = threading.Thread(target=crawl_thread_function)
    crawl_thread.start()

def crawl_thread_function():
    global target_users
    # init db sqlit3
    conn, cursor = init_db()

    login_twitter(USERNAME, YOUR_USERNAME, PASSWORD)

    while True:
        for target_user in target_users:
            print(f"🕒 Getting post from  @{target_user}...")
            crawl_tweets(target_user, cursor)
            conn.commit()   # commit this to database new data
        print(f"🕒 W8 {CRAWL_INTERVAL // 60} crawl again...")
        time.sleep(CRAWL_INTERVAL)   # w8 for 