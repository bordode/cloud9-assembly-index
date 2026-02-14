import telebot
import os
from twilio.rest import Client
from flask import Flask
import threading

# 1. DEFINE EVERYTHING FIRST
TOKEN = os.getenv('TELEGRAM_TOKEN')
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_SENDER = os.getenv('TWILIO_SENDER', '+18335308584')
TARGET_NUM = '+16045053049'

# THIS LINE MUST BE HERE
bot = telebot.TeleBot(TOKEN)
client = Client(TWILIO_SID, TWILIO_TOKEN)

# 2. THE HEARTBEAT SERVER
server = Flask(__name__)
@server.route("/")
def health_check():
    return "Philotymos Sentinel: Active", 200

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# 3. THE HANDLERS
@bot.message_handler(commands=['status'])
def check_grid(message):
    bot.reply_to(message, "🛡️ Philotymos is Online.")

@bot.message_handler(func=lambda m: True)
def monitor(message):
    try:
        val = float(message.text)
        if val >= 92.0:
            bot.reply_to(message, f"🚨 BREACH: {val} µT.")
            client.calls.create(
                twiml=f'<Response><Say>Resonance breach: {val} microteslas.</Say></Response>',
                to=TARGET_NUM, from_=TWILIO_SENDER
            )
    except: pass

# 4. START EVERYTHING
if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Sentinel Ignited...")
    bot.infinity_polling()
