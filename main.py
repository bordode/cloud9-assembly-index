import telebot
import os
from twilio.rest import Client
from flask import Flask
import threading

# 1. INITIALIZE CORE IDENTITY
TOKEN = os.getenv('TELEGRAM_TOKEN')
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_SENDER = os.getenv('TWILIO_SENDER', '+18335308584')
TARGET_NUM = '+16045053049'

# These must be defined before the handlers
bot = telebot.TeleBot(TOKEN)
client = Client(TWILIO_SID, TWILIO_TOKEN)

# 2. THE HEARTBEAT SERVER (For Koyeb Health Check)
server = Flask(__name__)
@server.route("/")
def health_check():
    return "Philotymos Sentinel: Active", 200

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# 3. DEFINE COMMAND HANDLERS
@bot.message_handler(commands=['status'])
def check_grid(message):
    bot.reply_to(message, "🛡️ Philotymos Sentinel is Online and Watching.")

@bot.message_handler(func=lambda m: True)
def monitor_resonance(message):
    try:
        val = float(message.text)
        if val >= 92.0:
            bot.reply_to(message, f"🚨 RESONANCE BREACH: {val} µT. Initiating Phone Bridge.")
            client.calls.create(
                twiml=f'<Response><Say>Resonance breach detected: {val} microteslas at the sentinel point.</Say></Response>',
                to=TARGET_NUM, 
                from_=TWILIO_SENDER
            )
        else:
            bot.reply_to(message, f"✅ {val} µT - Grid Secure.")
    except ValueError:
        pass # Ignore non-numeric text

# 4. IGNITION
if __name__ == "__main__":
    # Start the heartbeat in the background
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Sentinel Ignited...")
    # Start the bot
    bot.infinity_polling()
