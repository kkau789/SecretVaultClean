from flask import Flask, request, session, Response, redirect, render_template
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2 import cbor
from fido2.utils import websafe_encode, websafe_decode
import os

app = Flask(__name__)
app.secret_key = "super_random_secret_key_123456"

# ===== RP CONFIG (MUST MATCH YOUR DOMAIN) =====
rp = PublicKeyCredentialRpEntity(
    id="secretvaultclean.onrender.com",
    name="Secret Vault"
)

server = Fido2Server(rp)

# Simple in-memory storage (for demo)
users = {}
credentials = {}

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


# ================= REGISTER =================

@app.route("/register/begin", methods=["GET"])
def register_begin():
    user_id = os.urandom(16)

    registration_data, state = server.register_begin(
        {
            "id": user_id,
            "name": "user",
            "displayName": "Vault User",
        },
        credentials.values(),
        user_verification="required"
    )

    session["state"] = state
    session["user_id"] = websafe_encode(user_id)

    return Response(cbor.encode(registration_data), content_type="application/cbor")


@app.route("/register/complete", methods=["POST"])
def register_complete():
    data = cbor.decode(request.data)
    state = session["state"]

    auth_data = server.register_complete(state, data)

    credential_id = websafe_encode(auth_data.credential_id)
    credentials[credential_id] = auth_data.credential_data

    return "Registration successful"


# ================= LOGIN =================

@app.route("/login/begin", methods=["GET"])
def login_begin():
    auth_data, state = server.authenticate_begin(
        credentials.values(),
        user_verification="required"
    )

    session["state"] = state

    return Response(cbor.encode(auth_data), content_type="application/cbor")


@app.route("/login/complete", methods=["POST"])
def login_complete():
    data = cbor.decode(request.data)
    state = session["state"]

    credential_id = websafe_encode(websafe_decode(data["rawId"]))

    auth_data = server.authenticate_complete(
        state,
        credentials[credential_id],
        data
    )

    return redirect("/")


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)
