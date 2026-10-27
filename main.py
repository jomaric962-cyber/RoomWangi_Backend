import os
import json
import random
import string
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = "8659816135:AAFx_xvixCvDurRkwGaCyAapm_wgmUyGs9Q"
ADMIN_CHAT_ID = 8515760823
DATABASE_FILE = "database.json"

app = Flask(__name__)

# Initialize database
def load_db():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    return {"keys": {}, "devices": {}}

def save_db(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- KEY SYSTEM LOGIC ---
def generate_key(tier):
    prefix = "MAR"
    random_str = ''.join(random.choices(string.ascii_uppercase, k=6))
    key = f"{prefix}{random_str}"
    return key

# --- API ENDPOINTS ---
@app.route('/verify', methods=['POST'])
def verify_key():
    data = request.json
    user_key = data.get("key")
    device_id = data.get("device_id")
    
    db = load_db()
    if user_key in db["keys"]:
        # Device Binding
        if db["keys"][user_key]["device"] == None:
            db["keys"][user_key]["device"] = device_id
            save_db(db)
        
        if db["keys"][user_key]["device"] != device_id:
            return jsonify({"status": "error", "message": "Device not authorized"}), 403
            
        return jsonify({"status": "success", "tier": db["keys"][user_key]["tier"]})
    return jsonify({"status": "error", "message": "Invalid Key"}), 401

@app.route('/get_stats', methods=['GET'])
def get_stats():
    # Mocking the Stats API for now
    # In real implementation, this would scrape data from game servers
    player_id = request.args.get("id")
    return jsonify({
        "ign": "SamplePlayer",
        "rank": "Mythic",
        "wr": "65%",
        "party": "TRIO",
        "last_match": "Victory"
    })

# --- TELEGRAM BOT ---
async def start(update: Update, context):
    await update.message.reply_text("Welcome to Room Wangi Admin! Use /gen <tier> to create keys.")

async def gen_key(update: Update, context):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return
    
    try: 
        tier = context.args[0].upper() # e.g., DAY7, PERM
        key = generate_key(tier)
        
        db = load_db()
        db["keys"][key] = {"tier": tier, "device": None}
        save_db(db)
        
        await update.message.reply_text(f"✅ Key Generated!\nKey: {key}\nTier: {tier}")
    except:
        await update.message.reply_text("Usage: /gen DAY7 or /gen PERM")

# --- SERVER START ---
if __name__ == "__main__":
    # For Render, we use Gunicorn, but for local testing, we use app.run
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))