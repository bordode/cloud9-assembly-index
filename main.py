import telebot
import os
from flask import Flask
import threading

# 1. THE SOVEREIGN IDENTITY
TOKEN = os.getenv('TG_TOKEN') 

# 2. INITIALIZE MONITOR
bot = telebot.TeleBot(TOKEN)
THRESHOLD = 85.0 

# 3. THE PERSISTENCE LAYER
app = Flask(__name__)

@app.route("/")
def pulse_check():
    return "Status: Operational", 200

def start_persistence():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 4. DATA HANDLERS
@bot.message_handler(commands=['status'])
def report_status(message):
    bot.reply_to(message, "🛡️ System Online. Monitoring Grid.")

@bot.message_handler(func=lambda m: True)
def process_data(message):
    try:
        val = float(message.text.strip())
        if val >= THRESHOLD:
            bot.reply_to(message, f"🚨 ALERT: {val} µT. Threshold exceeded.")
        else:
            bot.reply_to(message, f"✅ {val} µT - Normal.")
    except:
        pass

# 5. IGNITION
if __name__ == "__main__":
    threading.Thread(target=start_persistence, daemon=True).start()
    bot.infinity_polling()
