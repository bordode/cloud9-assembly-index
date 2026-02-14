# ... (Top of your script imports) ...

# 1. UPDATED CORE IDENTITY
bot = telebot.TeleBot(TOKEN)
client = Client(TWILIO_SID, TWILIO_TOKEN)
THRESHOLD = 85.0  # <--- NEW PROTECTIVE LEVEL

# ... (Flask Heartbeat section) ...

@bot.message_handler(func=lambda m: True)
def monitor_resonance(message):
    try:
        val = float(message.text)
        if val >= THRESHOLD:
            # TRIGGER THE BRIDGE
            bot.reply_to(message, f"🚨 BREACH DETECTED: {val} µT. Initiating Phone Bridge.")
            client.calls.create(
                twiml=f'<Response><Say>Resonance breach: {val} microteslas.</Say></Response>',
                to=TARGET_NUM, from_=TWILIO_SENDER
            )
        else:
            bot.reply_to(message, f"✅ {val} µT - Grid Secure.")
    except: pass

# ... (Ignition section at the bottom) ...
