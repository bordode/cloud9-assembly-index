import os
import telebot
import pandas as pd
from flask import Flask
import threading

# 1. THE SECRET HANDSHAKE
# This pulls the token from the "Spot for secrets" you found in Koyeb
TOKEN = os.getenv('TG_TOKEN')
FILE_ID = '1zDOSv7jG_SblC65fOVkSRN9meKVwQ4zA'
FILE_URL = f'https://drive.google.com/uc?id={FILE_ID}'
THRESHOLD = 85.0

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. THE HEARTBEAT (Keeps Koyeb from sleeping)
@app.route('/')
def health_check():
    return "Sentinel Active", 200

# 3. THE COMMANDS
@bot.message_handler(commands=['analyze'])
def analyze_data(message):
    try:
        df = pd.read_csv(FILE_URL)
        peak_val = df['BT'].max()
        status = "🚨 DANGER" if peak_val > THRESHOLD else "✅ STABLE"
        bot.reply_to(message, f"📊 CLOUD REPORT\nPeak: {peak_val} µT\nStatus: {status}")
    except Exception as e:
        bot.reply_to(message, "❌ Sync Error. Ensure Drive link is Public.")

@bot.message_handler(func=lambda m: True)
def process_manual_input(message):
    try:
        val = float(message.text.strip())
        if val >= THRESHOLD:
            bot.send_message(message.chat.id, f"🚨 ALERT: {val} µT!", disable_notification=False)
        else:
            bot.reply_to(message, f"✅ {val} µT", disable_notification=True)
    except:
        pass

# 4. THE ENGINE ROOM
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Run the bot and the web server simultaneously
    threading.Thread(target=run_bot).start()
    # Koyeb listens on port 8080
    app.run(host='0.0.0.0', port=8080)
