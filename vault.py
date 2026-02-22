from flask import Flask, request, render_template, jsonify
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from fido2.utils import websafe_encode, websafe_decode
import os

app = Flask(__name__)

# IMPORTANT: Replace with your real Render domain
RP_ID = "secretvaultclean.onrender.com"
RP_NAME = "Secret Vault"

rp = PublicKeyCredentialRpEntity(RP_ID, RP_NAME)
server = Fido2Server(rp)

# Simple in-memory storage (for testing)
users = {}
credentials = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register/begin")
def register_begin():
    username = "user"

    user = PublicKeyCredentialUserEntity(
        id=os.urandom(16),
        name=username,
        display_name=username,
    )

    registration_data, state = server.register_begin(
        user,
        credentials.get(username, []),
        user_verification="required",
    )

    users[username] = {"state": state}
    return jsonify(registration_data)

@app.route("/register/complete", methods=["POST"])
def register_complete():
    username = "user"
    data = request.json
    state = users[username]["state"]

    auth_data = server.register_complete(state, data)

    credentials.setdefault(username, []).append(auth_data.credential_data)
    return jsonify({"status": "ok"})

@app.route("/login/begin")
def login_begin():
    username = "user"

    auth_data, state = server.authenticate_begin(
        credentials.get(username, []),
        user_verification="required",
    )

    users[username] = {"state": state}
    return jsonify(auth_data)

@app.route("/login/complete", methods=["POST"])
def login_complete():
    username = "user"
    data = request.json
    state = users[username]["state"]

    server.authenticate_complete(
        state,
        credentials.get(username, []),
        data,
    )

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run()
