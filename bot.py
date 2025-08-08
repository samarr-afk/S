import os
import sqlite3
import random
import string
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BACKEND_URL = os.getenv("BACKEND_URL")

def generate_code():
    return ''.join(random.choices(string.digits, k=8))

def save_file_info(code, name, size, path, uploader):
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("INSERT INTO files (share_code, file_name, file_size, file_path, uploader_id, upload_date) VALUES (?, ?, ?, ?, ?, ?)",
              (code, name, size, path, uploader, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send me a file and I'll give you a download link.")

def get_link(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /get <sharecode>")
        return
    code = context.args[0]
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("SELECT file_name FROM files WHERE share_code=?", (code,))
    row = c.fetchone()
    conn.close()
    if row:
        update.message.reply_text(f"Download link:\n{BACKEND_URL}/d/{code}")
    else:
        update.message.reply_text("Share code not found.")

def handle_file(update: Update, context: CallbackContext):
    doc = update.message.document
    if not doc:
        update.message.reply_text("Only document uploads supported.")
        return
    forwarded = context.bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    file_info = context.bot.get_file(doc.file_id)
    code = generate_code()
    save_file_info(code, doc.file_name, doc.file_size, file_info.file_path, update.message.from_user.id)
    update.message.reply_text(f"✅ Uploaded!\nShare code: {code}\nDownload: {BACKEND_URL}/d/{code}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get", get_link))
    dp.add_handler(MessageHandler(Filters.document, handle_file))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
