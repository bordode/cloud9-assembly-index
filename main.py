import os
import io
import telebot
import pandas as pd
import requests
from flask import Flask, request, abort

TOKEN = os.getenv('TG_TOKEN')
FILE_ID = '1zDOSv7jG_SblC65fOVkSRN9meKVwQ4zA'
THRESHOLD = 85.0

app = Flask(__name__)

try:
    bot = telebot.TeleBot(TOKEN) if TOKEN else None
except Exception as e:
    bot = None

def fetch_data():
    url = f'https://drive.google.com/uc?export=download&id={FILE_ID}'
    r = requests.get(url, timeout=10, verify=False)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))

if bot:
    @bot.message_handler(commands=["analyze"])
    def analyze_data(message):
        try:
            df = fetch_data()
            peak_val = df["BT"].max()
            status = "🚨 DANGER" if peak_val > THRESHOLD else "✅ STABLE"
            bot.reply_to(message, f"📊 CLOUD REPORT\nPeak: {peak_val} µT\nStatus: {status}")
        except Exception as e:
            bot.reply_to(message, f"❌ Sync Error: {e}")

    @bot.message_handler(func=lambda m: True)
    def process_manual_input(message):
        try:
            val = float(message.text.strip())
            if val >= THRESHOLD:
                bot.send_message(message.chat.id, f"🚨 ALERT: {val} µT!")
            else:
                bot.reply_to(message, f"✅ {val} µT - Stable")
        except:
            bot.reply_to(message, "Send a number or /analyze")

@app.route("/")
def health_check():
    return f"Sentinel Active | TOKEN: {bool(TOKEN)} | Bot: {bool(bot)}", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if not bot:
        abort(500, "Bot not initialized")
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
