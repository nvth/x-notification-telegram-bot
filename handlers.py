from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from functions import add_user, remove_user, list_users, start_crawl

def setup_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("add_user", handle_add_user))
    dispatcher.add_handler(CommandHandler("remove_user", handle_remove_user))
    dispatcher.add_handler(CommandHandler("list_users", handle_list_users))
    dispatcher.add_handler(CommandHandler("start_crawl", handle_start_crawl))

def handle_add_user(update: Update, context: CallbackContext):
    user_input = update.message.text.replace("/add_user", "").strip()
    add_user(user_input)
    update.message.reply_text(f"✅ User added: {user_input}")

def handle_remove_user(update: Update, context: CallbackContext):
    user_input = update.message.text.replace("/remove_user", "").strip()
    remove_user(user_input)
    update.message.reply_text(f"✅ Removed: {user_input}")

def handle_list_users(update: Update, context: CallbackContext):
    users = list_users()
    if users:
        update.message.reply_text(f"📋 Listing:\n{', '.join(users)}")
    else:
        update.message.reply_text("❌ Not user found.")

def handle_start_crawl(update: Update, context: CallbackContext):
    start_crawl()
    update.message.reply_text("✅ Getting post started.")