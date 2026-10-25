import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
print(f"TOKEN FOUND: {bool(TOKEN)}")

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "V5 is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    print(f"Flask starting on port {port}")
    flask_app.run(host='0.0.0.0', port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("V5 LIVE! Send: Lakers vs Warriors")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"V5 PREDICTION: {update.message.text.upper()} WILL WIN!")

def main():
    print("Starting V5 Bot...")
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()
    print("V5 Bot Started - Ready!")
    
    if not TOKEN:
        print("ERROR NO TOKEN")
        flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("V5 Bot Started - Polling!")
    app.run_polling()

if __name__ == "__main__":
    main()
