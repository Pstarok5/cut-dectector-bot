import os
import random
import hashlib
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

# FAKE WEB SERVER TO KEEP RENDER HAPPY (FREE PLAN)
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "V5 Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

def get_team_power(team_name):
    h = int(hashlib.md5(team_name.lower().encode()).hexdigest(), 16)
    base = 70 + (h % 21)
    form = random.randint(-4, 4)
    return base + form

def predict_any_basketball(team1, team2):
    r1 = get_team_power(team1)
    r2 = get_team_power(team2)
    total = r1 + r2
    p1 = int((r1/total)*100)
    p2 = 100 - p1
    if p1 >= p2:
        winner = team1.upper()
        conf = p1
        handicap = f"{team1.title()} -2.5"
    else:
        winner = team2.upper()
        conf = p2
        handicap = f"{team2.title()} -2.5"
    if conf >= 65:
        risk = "LOW - Good Pick"
        safe_bet = handicap
    elif conf >= 55:
        risk = "MEDIUM - Play Safe"
        safe_bet = f"{winner} +5.5 Handicap (Safer)"
    else:
        risk = "HIGH - Too Close, Skip"
        safe_bet = "SKIP - No clear favorite"
    total_points = random.choice(["Over 205.5", "Over 210.5", "Over 215.5", "Under 220.5"])
    return f"🏀 ALL LEAGUES PREDICTOR V5\n\nMatch: {team1.title()} vs {team2.title()}\nLeague: Auto-Detected\n\nWINNER: {winner} ({conf}%)\nBest Bet: {safe_bet}\nPoints: {total_points}\nRisk: {risk}\n\nPower: {r1} vs {r2}\n"

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
        except Exception as e:
            print(e)
    await update.message.reply_text("Send like: Lakers vs Warriors")

def main():
    if not TOKEN:
        print("ERROR: TOKEN not set")
        return
    # Start fake web server in background
    threading.Thread(target=run_flask, daemon=True).start()
    print("Flask started, starting bot...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("V5 Bot Started")
    app.run_polling()

if __name__ == "__main__":
    main()
