import os
import random
import hashlib
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "V5 Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

def get_team_power(team_name):
    h = int(hashlib.md5(team_name.lower().encode()).hexdigest(), 16)
    return 70 + (h % 21) + random.randint(-4, 4)

def predict_any_basketball(team1, team2):
    r1 = get_team_power(team1)
    r2 = get_team_power(team2)
    total = r1 + r2
    p1 = int((r1/total)*100)
    if p1 >= 50:
        winner = team1.upper()
        conf = p1
    else:
        winner = team2.upper()
        conf = 100-p1
    return f"🏀 V5 ALL LEAGUES\n\nMatch: {team1.title()} vs {team2.title()}\nWINNER: {winner} ({conf}%)\nBest Bet: {winner} -2.5\nRisk: LOW\n"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏀 V5 LIVE — Send: Lakers vs Warriors")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "vs" in text.lower():
        try:
            parts = text.lower().split("vs")
            team1 = parts[0].strip()
            team2 = parts[1].strip()
            if team1 and team2:
                result = predict_any_basketball(team1, team2)
                await update.message.reply_text(result)
                return
        except: pass
    await update.message.reply_text("Send like: Lakers vs Warriors")

def main():
    if not TOKEN:
        print("ERROR: TOKEN not set")
        return
    threading.Thread(target=run_flask, daemon=True).start()
    print("Flask started")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("V5 Bot Started - Ready!")
    app.run_polling()

if __name__ == "__main__":
    main()
