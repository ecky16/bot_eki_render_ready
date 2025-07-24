from flask import Flask, request
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters
import os
import asyncio
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
application = ApplicationBuilder().token(BOT_TOKEN).build()

@app.route("/")
def index():
    return "Bot is alive!", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    print("[FLASK] Dapat request POST dari Telegram")
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.create_task(application.process_update(update))
    return "OK", 200

# =======================
# HANDLER TEKS (koordinat)
# =======================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[HANDLE_TEXT] Masuk handler")
    text = update.message.text

    # Cari pola koordinat di teks
    match = re.search(r"(-?\d{1,3}\.\d+),\s*(-?\d{1,3}\.\d+)", text)
    if match:
        lat, lon = match.groups()
        await update.message.reply_text(
            f"🎯 Koordinat terdeteksi:\n`{lat}, {lon}`\n📍 https://maps.google.com/?q={lat},{lon}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "Halo, aku bot dari Ecky! Kirim lokasi atau koordinatmu ya!"
        )

# =======================
# HANDLER SHARE LOCATION
# =======================
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        loc = update.message.location
        lat = loc.latitude
        lon = loc.longitude
        await update.message.reply_text(
            f"Lokasimu terdeteksi:\n`{lat}, {lon}`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print("[ERROR][handle_location]", e)

# Tambahkan semua handler
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
application.add_handler(MessageHandler(filters.LOCATION, handle_location))

# =======================
# JALANKAN
# =======================
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start()
    application.run_polling()
