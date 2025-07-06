from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import os
import json

app = Flask(__name__)

TRIBUTE_SECRET_KEY = os.environ.get("TRIBUTE_SECRET_KEY")
if not TRIBUTE_SECRET_KEY:
    raise RuntimeError("TRIBUTE_SECRET_KEY is not set")

FORWARDING_RULES_PATH = os.environ.get("FORWARDING_RULES_PATH", "/app/forwarding_rules.json")
forwarding_rules_cache = {}

def load_forwarding_rules():
    global forwarding_rules_cache
    try:
        with open(FORWARDING_RULES_PATH, "r", encoding="utf-8") as f:
            forwarding_rules_cache = json.load(f)
            app.logger.info("Forwarding rules loaded.")
    except Exception as e:
        app.logger.error(f"Failed to load forwarding rules: {e}")
        forwarding_rules_cache = {}

# Загружаем правила при старте
load_forwarding_rules()

def is_valid_signature(request):
    signature_header = request.headers.get("X-Tribute-Signature", "")
    if not signature_header.startswith("sha256="):
        return False

    provided_signature = signature_header.split("=", 1)[1]
    raw_body = request.get_data()
    computed_hmac = hmac.new(
        TRIBUTE_SECRET_KEY.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(provided_signature, computed_hmac)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    try:
        if not is_valid_signature(request):
            return jsonify({"error": "Invalid signature"}), 403

        data = request.get_json()
        if not data or 'payload' not in data:
            return jsonify({"error": "Missing payload"}), 400

        payload = data['payload']
        subscription_name = payload.get('subscription_name')
        if not subscription_name:
            return jsonify({"error": "Missing subscription_name in payload"}), 400

        destination_url = forwarding_rules_cache.get(subscription_name)
        if not destination_url:
            return jsonify({"error": f"No forwarding rule for subscription_name: {subscription_name}"}), 404

            # Копируем все заголовки кроме Host и Content-Length
        headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ('host', 'content-length')
            }

            # Получаем сырое тело запроса
        raw_body = request.get_data()

        response = requests.post(destination_url, data=raw_body, headers=headers)

        if response.status_code != 200:
            return jsonify({
                "error": "Forwarding failed",
                "destination": destination_url,
                "response": response.text
            }), 502

        return jsonify({"status": "forwarded", "destination": destination_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/routes', methods=['GET'])
def view_routes():
    return jsonify(forwarding_rules_cache), 200

@app.route('/reload-routes', methods=['POST'])
def reload_routes():
    load_forwarding_rules()
    return jsonify({"status": "reloaded", "rules": forwarding_rules_cache}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
