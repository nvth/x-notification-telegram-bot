from telegram.ext import Updater
from handlers import setup_handlers
from config import tele_data

def main():

    TELEGRAM_BOT_TOKEN, _ = tele_data()

    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    setup_handlers(dispatcher)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()