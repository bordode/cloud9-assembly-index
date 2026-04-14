import os
import io
import telebot
import pandas as pd
import requests
from flask import Flask, request, abort

# Configuration - ALL sensitive data from environment variables
TOKEN = os.getenv('TG_TOKEN')
FILE_ID = os.getenv('GDRIVE_FILE_ID')  # Move to env var
THRESHOLD = float(os.getenv('THRESHOLD', '85.0'))  # Configurable with default

app = Flask(__name__)

# Initialize bot with error handling
bot = None
if TOKEN:
    try:
        bot = telebot.TeleBot(TOKEN)
    except Exception as e:
        print(f"Bot initialization failed: {e}")
else:
    print("Warning: TG_TOKEN not set")

def fetch_data():
    """Fetch CSV from Google Drive with proper error handling"""
    if not FILE_ID:
        raise ValueError("GDRIVE_FILE_ID environment variable not set")
    
    url = f'https://drive.google.com/uc?export=download&id={FILE_ID}'
    session = requests.Session()
    
    try:
        r = session.get(url, timeout=15, allow_redirects=True)
        r.raise_for_status()
        return pd.read_csv(io.StringIO(r.text))
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch data: {e}")

if bot:
    @bot.message_handler(commands=["start", "help"])
    def send_welcome(message):
        help_text = (
            "🛡️ Cloud Sentinel Bot\n\n"
            "Commands:\n"
            "/analyze - Check magnetic field data\n"
            "Or send a value directly to check status"
        )
        bot.reply_to(message, help_text)

    @bot.message_handler(commands=["analyze"])
    def analyze_data(message):
        try:
            df = fetch_data()
            
            if "BT" not in df.columns:
                bot.reply_to(message, "❌ Error: 'BT' column not found in data")
                return
            
            peak_val = df["BT"].max()
            status = "🚨 DANGER" if peak_val > THRESHOLD else "✅ STABLE"
            
            response = (
                f"📊 CLOUD REPORT\n"
                f"Peak: {peak_val:.2f} µT\n"
                f"Threshold: {THRESHOLD} µT\n"
                f"Status: {status}"
            )
            bot.reply_to(message, response)
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {type(e).__name__}: {str(e)}")

    @bot.message_handler(func=lambda m: True)
    def process_manual_input(message):
        # Ignore commands
        if message.text.startswith('/'):
            return
            
        try:
            val = float(message.text.strip())
            if val >= THRESHOLD:
                bot.send_message(
                    message.chat.id, 
                    f"🚨 ALERT: {val:.2f} µT exceeds threshold ({THRESHOLD} µT)!"
                )
            else:
                bot.reply_to(
                    message, 
                    f"✅ {val:.2f} µT - Below threshold ({THRESHOLD} µT)"
                )
        except ValueError:
            bot.reply_to(message, "❌ Please send a number or use /analyze")

@app.route("/")
def health_check():
    status = {
        "token_set": bool(TOKEN),
        "bot_initialized": bool(bot),
        "file_id_set": bool(FILE_ID),
        "threshold": THRESHOLD
    }
    return status, 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if not bot:
        abort(503, "Bot not initialized - check TG_TOKEN")
    
    try:
        json_data = request.get_json(force=True, silent=True)
        if not json_data:
            abort(400, "Invalid JSON")
            
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return "OK", 200
        
    except Exception as e:
        print(f"Webhook error: {e}")
        abort(500, "Processing failed")

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    app.run(host="0.0.0.0", port=port)
    
