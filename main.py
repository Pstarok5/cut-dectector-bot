import os, time, json, re
import urllib.request
import urllib.parse

TOKEN = os.environ.get("TOKEN")

# --- SMART ANALYSIS ENGINE ---
def analyze_leg(leg):
    leg_lower = leg.lower()
    risk_score = 0
    reason = []

    # High risk patterns
    if "away" in leg_lower or "trier" in leg_lower or "guest" in leg_lower:
        risk_score += 40
        reason.append("Away team underdog")
    if "over" in leg_lower and ("2.5" in leg or "3.5" in leg):
        risk_score += 30
        reason.append("Over goals risky")
    if "both" in leg_lower or "btts" in leg_lower or "gg" in leg_lower:
        risk_score += 35
        reason.append("BTTS very risky")
    if "win" in leg_lower and "away" in leg_lower:
        risk_score += 50
        reason.append("Away win is #1 cutter")
    if "handicap" in leg_lower or " -" in leg:
        risk_score += 20
        reason.append("Handicap risky")
    
    # Low risk patterns
    if "home" in leg_lower or "1x" in leg_lower or "double chance" in leg_lower:
        risk_score -= 20
        reason.append("Home/DC safer")

    if risk_score >= 50:
        return f"🔴 CUT RISK {risk_score}% - {', '.join(reason)}"
    elif risk_score >= 25:
        return f"🟡 MEDIUM {risk_score}% - {', '.join(reason)}"
    else:
        return f"🟢 SAFE {risk_score}% - {', '.join(reason) if reason else 'Stable pick'}"

def send(chat_id, text):
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        urllib.request.urlopen(url, data, timeout=10)
    except Exception as e:
        print(e)

print("✅ V2 SMART BOT LIVE!")
offset = 0

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?timeout=10&offset={offset}"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode())
        
        for upd in data.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message", {})
            chat_id = msg.get("chat", {}).get("id")
            text = msg.get("text", "").strip()
            if not chat_id or not text:
                continue
            
            if text.startswith("/start"):
                send(chat_id, "🎯 WELCOME TO CUT DETECTOR V2\n\nPaste your ticket like:\nVechta vs Trier - Away Win\nKerasus vs Kocaeli - Home\n\nI will tell you which leg will CUT!")
                continue

            legs = [l.strip() for l in text.split("\n") if l.strip()]
            reply = f"🔍 V2 ANALYSIS - {len(legs)} LEGS:\n\n"
            cut_count = 0
            
            for i, leg in enumerate(legs, 1):
                result = analyze_leg(leg)
                if "🔴" in result:
                    cut_count += 1
                reply += f"{i}. {leg}\n   -> {result}\n\n"
            
            if cut_count > 0:
                reply += f"⚠️ WARNING: {cut_count} leg(s) likely to CUT!\nRemove 🔴 legs."
            else:
                reply += "✅ Ticket looks SAFE!"

            send(chat_id, reply)

    except Exception as e:
        print(f"Loop: {e}")
        time.sleep(2)
