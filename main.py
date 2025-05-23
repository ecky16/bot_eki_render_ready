from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters
import os
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

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

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[HANDLE_TEXT] Masuk handler")
    await update.message.reply_text("Halo, aku bot dari Render!")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    application.run_polling()
