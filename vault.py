import os
import json
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from fido2.utils import websafe_encode, websafe_decode
from fido2 import cbor

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")

RP_ID = "secretvaultclean.onrender.com"
rp = PublicKeyCredentialRpEntity(name="SecretVault", id=RP_ID)
server = Fido2Server(rp)

CREDENTIAL_FILE = "credential.json"
NOTE_FILE = "secrets.txt"

# ----------------------
# Home
# ----------------------

@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    notes = ""
    if os.path.exists(NOTE_FILE):
        with open(NOTE_FILE, "r") as f:
            notes = f.read()

    return render_template("home.html", notes=notes)

@app.route("/login")
def login():
    return render_template("login.html")

# ----------------------
# Registration
# ----------------------

@app.route("/register/begin", methods=["GET"])
def register_begin():
    user = PublicKeyCredentialUserEntity(
        id=b"vault-user",
        name="vaultuser",
        display_name="Vault User"
    )

    registration_data, state = server.register_begin(
        user,
        credentials=[]
    )

    session["state"] = state
    return cbor.dumps(registration_data)

@app.route("/register/complete", methods=["POST"])
def register_complete():
    data = cbor.loads(request.get_data())
    auth_data = server.register_complete(session["state"], data)

    with open(CREDENTIAL_FILE, "w") as f:
        json.dump({
            "credential_id": websafe_encode(auth_data.credential_id).decode(),
            "public_key": websafe_encode(auth_data.credential_public_key).decode()
        }, f)

    return jsonify({"status": "registered"})

# ----------------------
# Authentication
# ----------------------

@app.route("/login/begin", methods=["GET"])
def login_begin():
    if not os.path.exists(CREDENTIAL_FILE):
        return jsonify({"error": "No credential registered"}), 400

    with open(CREDENTIAL_FILE, "r") as f:
        stored = json.load(f)

    credential_id = websafe_decode(stored["credential_id"])

    auth_data, state = server.authenticate_begin([{
        "type": "public-key",
        "id": credential_id
    }])

    session["state"] = state
    return cbor.dumps(auth_data)

@app.route("/login/complete", methods=["POST"])
def login_complete():
    data = cbor.loads(request.get_data())

    with open(CREDENTIAL_FILE, "r") as f:
        stored = json.load(f)

    credential_id = websafe_decode(stored["credential_id"])
    public_key = websafe_decode(stored["public_key"])

    server.authenticate_complete(
        session["state"],
        [{
            "type": "public-key",
            "id": credential_id,
            "publicKey": public_key
        }],
        data
    )

    session["logged_in"] = True
    return jsonify({"status": "ok"})

# ----------------------
# Notes
# ----------------------

@app.route("/add", methods=["POST"])
def add_note():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    note = request.form.get("note")
    with open(NOTE_FILE, "a") as f:
        f.write(note + "\n")

    return redirect(url_for("home"))

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

# ----------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
