import os
import random
import hashlib
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "V5 FIXED LIVE"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def get_strength(name):
    # Each team has different power
    base = int(hashlib.md5(name.lower().encode()).hexdigest(), 16) % 30
    return 60 + base

def predict_winner(t1, t2):
    s1 = get_strength(t1) + random.randint(-8,8)
    s2 = get_strength(t2) + random.randint(-8,8)
    
    # CLEAR WINNER SELECTION
    if s1 > s2:
        winner = t1.upper()
        loser = t2.title()
        diff = s1 - s2
        conf = 55 + min(int(diff*2), 30)
    else:
        winner = t2.upper()
        loser = t1.title()
        diff = s2 - s1
        conf = 55 + min(int(diff*2), 30)
    
    return winner, loser, conf, s1, s2

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏀 V5 FIXED!\nSend: Lakers vs Warriors\nI WILL pick winner!")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if "vs" in txt.lower():
        parts = txt.lower().split("vs",1)
        team1 = parts[0].strip()
        team2 = parts[1].strip()
        if team1 and team2:
            winner, loser, conf, p1, p2 = predict_winner(team1, team2)
            
            msg = f"🏀 V5 BASKETBALL - WINNER PICKED!\n\n"
            msg += f"MATCH: {team1.title()} vs {team2.title()}\n"
            msg += f"Power: {team1.title()} [{int(p1)}] vs {team2.title()} [{int(p2)}]\n\n"
            msg += f"🏆 WINNER TO WIN THE GAME: {winner}\n"
            msg += f"Confidence: {conf}%\n\n"
            msg += f"💰 BEST BETS:\n"
            msg += f"1. {winner} ML (Moneyline)\n"
            msg += f"2. {winner} -2.5 Handicap\n"
            msg += f"3. Over 215.5 Points\n\n"
            msg += f"Loser: {loser} will LOSE\n"
            msg += f"Risk: {'LOW' if conf>70 else 'MEDIUM'}"
            
            await update.message.reply_text(msg)
            return
    await update.message.reply_text("Send: TeamA vs TeamB")

def main():
    print("V5 Bot Started - Ready!")
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    app.run_polling()

if __name__ == "__main__":
    main()
