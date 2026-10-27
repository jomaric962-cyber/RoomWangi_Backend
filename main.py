import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- FLASK API ENDPOINTS (DIRECT ACCESS) ---
@app.route('/verify', methods=['POST'])
def verify_key():
    # Laging success dahil wala nang key system
    return jsonify({"status": "success", "tier": "PREMIUM", "message": "Direct Access Granted"})

@app.route('/get_stats', methods=['GET'])
def get_stats():
    # Dito kukuha ng data ang Android Overlay app
    return jsonify({"status": "success", "data": "Stats API Active - Direct Mode"})

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 10000)) 
    app.run(host="0.0.0.0", port=port)