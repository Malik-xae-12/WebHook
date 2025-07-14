from flask import Flask, request, jsonify
import threading
import requests
import time
import os
 
app = Flask(__name__)

# Get port from environment variable (Render provides this) or default to 5000
port = int(os.environ.get('PORT', 5000))

# Sample transaction data (simulate a database)
transactions = [
    {"transaction_id": "TX001", "amount": 1000, "type": "credit", "status": "pending"},
    {"transaction_id": "TX002", "amount": 500, "type": "debit", "status": "completed"},
    {"transaction_id": "TX003", "amount": 2000, "type": "debit", "status": "pending"}
]
 
# --- 🔁 Webhook Endpoint (used in Webhook Activity) ---
def send_callback(callback_url, result):
    time.sleep(3)  # Simulate processing delay
    try:
        resp = requests.post(callback_url, json=result)
        print(f"Callback sent! Status code: {resp.status_code}")
    except Exception as e:
        print(f"Callback failed: {e}")
 
@app.route('/process_transaction', methods=['POST'])
def webhook_endpoint():
    data = request.get_json()
    print("Received data via webhook:", data)
 
    callback_url = data.get('callBackUri')
    if not callback_url:
        return jsonify({"error": "No callback URI found"}), 400
 
    result = {
        "transaction_id": data.get("transaction_id"),
        "status": "success",
        "message": "Transaction Approved"
    }
 
    threading.Thread(target=send_callback, args=(callback_url, result)).start()
 
    return jsonify({"status": "processing", "callbackUrl": callback_url}), 202
 
 
# --- 🌐 Web API Endpoint (used in Web Activity) ---
@app.route('/all_transactions', methods=['GET'])
def get_all_transactions():
    print("GET: All transaction data requested")
    return jsonify({
        "transactions": transactions,
        "status": "success"
    }), 200

# Health check endpoint (useful for Render)
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200
 
if __name__ == '__main__':
    # Bind to 0.0.0.0 to accept connections from any IP
    app.run(host='0.0.0.0', port=port, debug=False)
