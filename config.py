def config_auth():
    USERNAME = "your_email"  
    PASSWORD = "your_password"  
    CRAWL_INTERVAL = 10 
    YOUR_USERNAME = "your_username"

    return USERNAME, PASSWORD, CRAWL_INTERVAL, YOUR_USERNAME

def tele_data():
    TELEGRAM_BOT_TOKEN = 'your_bot_token' #get bot token from @botfather
    CHAT_ID = 'your_chat_id' # from https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates get chat_id (before that, please chat with bot first)
    return TELEGRAM_BOT_TOKEN, CHAT_ID