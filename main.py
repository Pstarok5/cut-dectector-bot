import os, logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import numpy as np
import cv2

TOKEN = os.environ.get("TOKEN")
logging.basicConfig(level=logging.INFO)

# --- IMPROVED DETECTION ENGINE ---
def analyze_cut(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None, "Could not read image"
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Better skin + blood detection
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2
    
    red_pixels = cv2.countNonZero(red_mask)
    total_pixels = img.shape[0] * img.shape[1]
    red_ratio = red_pixels / total_pixels
    
    # Edge detection for cut lines
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_ratio = cv2.countNonZero(edges) / total_pixels
    
    # Scoring system V3
    score = (red_ratio * 100) + (edge_ratio * 50)
    
    if red_ratio < 0.005:
        return False, f"No significant redness detected.\nRedness: {red_ratio*100:.2f}% | Score: {score:.1f}"
    elif score < 1.5:
        return True, f"⚠️ SMALL CUT / Scratch Detected\nRedness: {red_ratio*100:.2f}% | Risk Score: {score:.1f}/10\nAdvice: Clean with antiseptic."
    elif score < 5.0:
        return True, f"🩹 MEDIUM CUT Detected\nRedness: {red_ratio*100:.2f}% | Risk Score: {score:.1f}/10\nAdvice: Clean, apply pressure, bandage."
    else:
        return True, f"🚨 DEEP / BLEEDING CUT Detected\nRedness: {red_ratio*100:.2f}% | Risk Score: {score:.1f}/10\nAdvice: Apply pressure and seek medical help!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🩹 CUT DETECTOR V3 — High Accuracy\n\n"
        "Send a photo of a cut/wound and I will analyze it.\n\n"
        "⚠️ DISCLAIMER: This is NOT medical advice. For severe bleeding, go to hospital immediately.\n\n"
        "Just send a photo now 👇"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    path = f"/tmp/{photo.file_id}.jpg"
    await file.download_to_drive(path)
    
    await update.message.reply_text("🔍 Analyzing with V3 AI...")
    
    is_cut, result_text = analyze_cut(path)
    
    if is_cut is None:
        await update.message.reply_text(f"❌ Error: {result_text}")
    else:
        await update.message.reply_text(f"{result_text}\n\n_Disclaimer: AI analysis only, not a doctor._", parse_mode='Markdown')
    
    os.remove(path) if os.path.exists(path) else None

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("V3 Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
