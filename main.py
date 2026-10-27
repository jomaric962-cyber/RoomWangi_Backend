import os
import json
import random
import string
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from threading import Thread

# --- CONFIGURATION ---
# Ang iyong Bot Token mula kay BotFather
BOT_TOKEN = "8659816135:AAFx_xvixCvDurRkwGaCyAapm_wgmUyGs9Q"
DATABASE_FILE = "database.json"

app = Flask(__name__)

# Database helpers
def load_db():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r") as f:
                return json.load(f)
        except:
            return {"keys": {}, "devices": {}}
    return {"keys": {}, "devices": {}}

def save_db(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- KEY SYSTEM ---
def generate_key(tier):
    prefix = "MAR"
    random_str = ''.join(random.choices(string.ascii_uppercase, k=6))
    return f"{prefix}{random_str}"

# --- API ENDPOINTS (Para sa Android App) ---
@app.route('/verify', methods=['POST'])
def verify_key():
    data = request.json
    user_key = data.get("key")
    device_id = data.get("device_id")
    db = load_db()
    
    if user_key in db["keys"]:
        # Bind device if first time using the key
        if db["keys"][user_key].get("device") is None:
            db["keys"][user_key]["device"] = device_id
            save_db(db)
            
        if db["keys"][user_key]["device"] != device_id:
            return jsonify({"status": "error", "message": "Device not authorized"}), 403
            
        return jsonify({"status": "success", "tier": db["keys"][user_key]["tier"]})
    
    return jsonify({"status": "error", "message": "Invalid Key"}), 401

@app.route('/get_stats', methods=['GET'])
def get_stats():
    return jsonify({"status": "success", "data": "Stats API Active"})

# --- TELEGRAM BOT LOGIC ---
async def start(update: Update, context):
    await update.message.reply_text("Room Wangi Admin Active!\nUse /gen <tier> (Example: /gen PERM)")

async def gen_key(update: Update, context):
    try:
        tier = context.args[0].upper()
        key = generate_key(tier)
        db = load_db()
        db["keys"][key] = {"tier": tier, "device": None}
        save_db(db)
        await update.message.reply_text(f"✅ Key Generated!\nKey: {key}\nTier: {tier}")
    except (IndexError, Exception):
        await update.message.reply_text("❌ Error! Use: /gen DAY7 or /gen PERM")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen_key))
    app_bot.run_polling()

# --- START SERVER ---
if __name__ == "__main__":
    # Bot runs in a background thread
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Flask server runs in the main thread
    port = int(os.environ.get('PORT', 8080))
    app.run(host=' 

    # NOTE: Gunicorn handles the server on Render, 
    # so this block is mostly for local testing.
    # On Render, gunicorn main:app ignores the __main__ block.