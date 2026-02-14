import telebot
import os
from flask import Flask
import threading

# 1. THE SOVEREIGN IDENTITY
# Secrets are pulled from the hidden environment layer.
TOKEN = os.getenv('TG_TOKEN') 
IDENTITY_ID = os.getenv('IDENTITY_ID') 

# 2. INITIALIZE MONITOR
bot = telebot.TeleBot(TOKEN)
THRESHOLD = 85.0 

# 3. THE PERSISTENCE LAYER
# This ensures the process stays alive on the hosting infrastructure.
app = Flask(__name__)

@app.route("/")
def pulse_check():
    return "Status: Operational", 200

def start_persistence():
    # Automatically detects the port assigned by the host
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 4. RESONANCE HANDLERS
@bot.message_handler(commands=['status'])
def report_status(message):
    bot.reply_to(message, "🛡️ System is Online. Monitoring Grid.")

@bot.message_handler(func=lambda m: True)
def process_data(message):
    try:
        val = float(message.text.strip())
        if val >= THRESHOLD:
            bot.reply_to(message, f"🚨 ALERT: {val} µT. Threshold exceeded.")
        else:
            bot.reply_to(message, f"✅ {val} µT - Normal.")
    except Exception:
        # Silently ignore noise or invalid data
        pass

# 5. IGNITION
if __name__ == "__main__":
    # Start persistence in a separate thread
    threading.Thread(target=start_persistence, daemon=True).start()
    print("System activated in stealth mode...")
    bot.infinity_polling()
