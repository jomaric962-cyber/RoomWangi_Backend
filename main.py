import os
import json
import random
import string
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler
from threading import Thread

# --- CONFIG ---
BOT_TOKEN = "8659816135:AAFx_xvixCvDurRkwGaCyAapm_wgmUyGs9Q"
ADMIN_CHAT_ID = 8659816135
DATABASE_FILE = "database.json"

app = Flask(__name__)

def load_db():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r") as f: return json.load(f)
        except: return {"keys": {}, "devices": {}}
    return {"keys": {}, "devices": {}}

def save_db(data):
    with open(DATABASE_FILE, "w") as f: json.dump(data, f, indent=4)

def generate_key(tier):
    return f"MAR{''.join(random.choices(string.ascii_uppercase, k=6))}"

@app.route('/verify', methods=['POST'])
def verify_key():
    data = request.json
    user_key = data.get("key")
    device_id = data.get("device_id")
    db = load_db()
    if user_key in db["keys"]:
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

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

# --- BOT ---
async def start(update: Update, context):
    await update.message.reply_text("Admin Active! /gen <tier>")

async def gen_key_cmd(update: Update, context):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ Not Admin")
        return
    try:
        tier = context.args[0].upper()
        key = generate_key(tier)
        db = load_db()
        db["keys"][key] = {"tier": tier, "device": None}
        save_db(db)
        await update.message.reply_text(f"✅ Key: {key}\nTier: {tier}")
    except:
        await update.message.reply_text("❌ Use: /gen PERM")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen_key_cmd))
    app_bot.run_polling()

if __name__ == "__main__":
    bot_thread  = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)