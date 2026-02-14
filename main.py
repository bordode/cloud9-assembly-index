import telebot
import os
from twilio.rest import Client
from flask import Flask
import threading

# 1. THE SOVEREIGN IDENTITY (DIRECT TOKEN INTEGRATION)
TOKEN = "8556570503:AAGfz-l-aQth2X9jDkgxwR8ng26cYTMOUuY"
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_SENDER = os.getenv('TWILIO_SENDER', '+18335308584')
TARGET_NUM = '+16045053049'

# 2. INITIALIZE THE SENTINEL
bot = telebot.TeleBot(TOKEN)
client = Client(TWILIO_SID, TWILIO_TOKEN)
THRESHOLD = 85.0 

# 3. THE HEARTBEAT SERVER (For Koyeb Health Check)
server = Flask(__name__)
@server.route("/")
def health_check():
    return "Philotymos Sentinel: Active", 200

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# 4. COMMAND & RESONANCE HANDLERS
@bot.message_handler(commands=['status'])
def check_grid(message):
    bot.reply_to(message, "🛡️ Philotymos Sentinel is Online. Monitoring English Bay Grid.")

@bot.message_handler(func=lambda m: True)
def monitor_resonance(message):
    try:
        val = float(message.text)
        if val >= THRESHOLD:
            bot.reply_to(message, f"🚨 BREACH DETECTED: {val} µT. Initiating Phone Bridge.")
            client.calls.create(
                twiml=f'<Response><Say>Resonance breach detected: {val} microteslas. The sentinel is alerted.</Say></Response>',
                to=TARGET_NUM, 
                from_=TWILIO_SENDER
            )
        else:
            bot.reply_to(message, f"✅ {val} µT - Grid Secure.")
    except ValueError:
        pass 

# 5. IGNITION
if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Sentinel Ignited with Secure Token...")
    bot.infinity_polling()
