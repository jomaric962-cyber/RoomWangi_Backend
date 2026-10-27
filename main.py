import os
import json
import random
import string
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler
from threading import Thread

# --- CONFIGURATION ---
# Using the token and ID provided in previous steps
BOT_TOKEN = "8659816135:AAFx_xvixCvDurRkwGaCyAapm_wgmUyGs9Q"
ADMIN_CHAT_ID = 8659816135
DATABASE_FILE = "database.json"

app = Flask(__name__)

# --- DATABASE LOGIC ---
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

def generate_key(tier):
    # Format: MAR + 6 random uppercase letters
    prefix = "MAR"
    random_str = ''.join(random.choices(string.ascii_uppercase, k=6))
    return f"{prefix}{random_str}"

# --- FLASK API ENDPOINTS ---
@app.route('/verify', methods=['POST'])
def verify_key():
    data = request.json
    user_key = data.get("key")
    device_id = data.get("device_id")
    db = load_db()
    
    if user_key in db["keys"]:
        # Bind device if it's the first time using the key
        if db["keys"][user_key].get("device") is None:
            db["keys"][user_key]["device"] = device_id
            save_db(db)
        
        # Check if the current device matches the bound device
        if db["keys"][user_key]["device"] != device_id:
            return jsonify({"status": "error", "message": "Device not authorized"}), 403
            
        return jsonify({"status": "success", "tier": db["keys"][user_key]["tier"]})
    
    return jsonify({"status": "error", "message": "Invalid Key"}), 401

@app.route('/get_stats', methods=['GET'])
def get_stats():
    return jsonify({"status": "success", "data": "Stats API Active"})

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

# --- TELEGRAM BOT LOGIC ---
async def start_cmd(update: Update, context):
    await update.message.reply_text("Room Wangi Admin Active!\nUse /gen <tier> (e.g., /gen PERM)")

async def gen_key_cmd(update: Update, context):
    # Security check: Only allow the ADMIN_CHAT_ID to generate keys
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ Not authorized as Admin.")
        return
    
    try:
        tier = context.args[0].upper()
        key = generate_key(tier)
        db = load_db()
        db["keys"][key] = {"tier": tier, "device": None}
        save_db(db)
        await update.message.reply_text(f"✅ Key Generated:\n`{key}`\nTier: {tier}", parse_mode="Markdown")
    except (IndexError, Exception):
        await update.message.reply_text("❌ Error! Use: `/gen PERM` or `/gen DAY7`", parse_mode="Markdown")

def run_bot():
    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Initialize the Application
    app_bot = Application.builder().token(BOT_TOKEN).build ()
    app_bot.add_handler(CommandHandler("start", start_cmd))
    app_bot.add_handler(CommandHandler("gen", gen_key_cmd))
    
    # Start polling
    app_bot.run_polling()

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    # 1. Start the Telegram Bot in a background thread
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # 2. Start the Flask Server on the port provided by Render
    port = int(os.environ.get("PORT", 10000)) 
    app.run(host="0.0.0.0", port=port)