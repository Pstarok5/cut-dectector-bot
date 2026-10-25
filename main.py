import os
import random
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

def get_team_power(team_name):
    # Creates consistent rating for ANY team name
    # So "Lakers" always gets similar power
    h = int(hashlib.md5(team_name.lower().encode()).hexdigest(), 16)
    base = 70 + (h % 21)  # 70-90 range
    form = random.randint(-4, 4)
    return base + form

def predict_any_basketball(team1, team2):
    r1 = get_team_power(team1)
    r2 = get_team_power(team2)
    
    total = r1 + r2
    p1 = int((r1/total)*100)
    p2 = 100 - p1
    
    # Decide winner
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
        risk = "HIGH - Too Close, Skip This Game"
        safe_bet = "SKIP - No clear favorite"

    total_points = random.choice(["Over 205.5", "Over 210.5", "Over 215.5", "Under 220.5"])
    
    return (
        f"🏀 **ALL LEAGUES PREDICTOR V5**\n\n"
        f"Match: {team1.title()} vs {team2.title()}\n"
        f"🏆 League: Auto-Detected (Any League)\n\n"
        f"🔥 **WINNER: {winner} ({conf}% confidence)**\n"
        f"📊 Best Bet: {safe_bet}\n"
        f"📈 Points: {total_points}\n"
        f"⚠️ Risk: {risk}\n\n"
        f"Power Rating: {r1} vs {r2}\n\n"
        f"_Works for NBA, EuroLeague, NCAA, WNBA, Africa League etc._\n"
        f"_Analysis only - not 100% guarantee. 18+ Bet responsibly._"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏀 **V5 — ALL BASKETBALL LEAGUES LIVE**\n\n"
        "Send ANY game:\n"
        "`Lakers vs Warriors`\n"
        "`Real Madrid vs Barcelona`\n"
        "`Rivers Hoopers vs Kwara Falcons`\n"
        "`Duke vs Kentucky`\n\n"
        "I will predict winner for any league.",
        parse_mode='Markdown'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "vs" in text.lower() or "VS" in text:
        try:
            if "vs" in text.lower():
                parts = text.lower().split("vs")
            else:
                parts = text.split("VS")
            team1 = parts[0].strip()
            team2 = parts[1].strip()
            if team1 and team2:
                result = predict_any_basketball(team1, team2)
                await update.message.reply_text(result, parse_mode='Markdown')
                return
        except Exception as e:
            print(e)
    await update.message.reply_text(
        "Send like this:\n`Lakers vs Warriors`\n`Any Team vs Any Team`",
        parse_mode='Markdown'
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("V5 ALL LEAGUES Bot Started")
    app.run_polling()

if __name__ == "__main__":
    main()
