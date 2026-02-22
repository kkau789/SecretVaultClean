kimport os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Your biometric API key (the one Samsung gave you)
BIOMETRIC_API_KEY = "YOUR_API_KEY_HERE"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register-fingerprint", methods=["POST"])
def register_fingerprint():
    data = request.json
    if data.get("apiKey") != BIOMETRIC_API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    # Pseudo-code for Knox SDK call
    # result = knox.register_fingerprint(user_id)
    result = {"status": "success", "message": "Fingerprint popup should appear now"}
    return jsonify(result)

@app.route("/login-fingerprint", methods=["POST"])
def login_fingerprint():
    data = request.json
    if data.get("apiKey") != BIOMETRIC_API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    # Pseudo-code for Knox SDK call
    # result = knox.verify_fingerprint(user_id)
    result = {"status": "success", "message": "Fingerprint verified"}
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
