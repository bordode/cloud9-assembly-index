import telebot
import os
from twilio.rest import Client
from flask import Flask        # <--- INSERT THIS
import threading              # <--- INSERT THIS

# ... (Your existing Telebot and Twilio setup) ...

# INSERT THIS SECTION BELOW YOUR SETUP
server = Flask(__name__)
@server.route("/")
def health_check():
    return "Philotymos Sentinel: Active", 200

def run_web_server():
    # This reads the 'Port' you found in the Koyeb settings
    port = int(os.getenv("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# ... (Your existing @bot.message_handler code) ...

if __name__ == "__main__":
    # INSERT THIS LINE JUST BEFORE POLLING
    threading.Thread(target=run_web_server, daemon=True).start()
    
    print("Sentinel Ignited...")
    bot.infinity_polling()
