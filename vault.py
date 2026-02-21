from flask import Flask, request, session, redirect, Response
import cbor2 as cbor
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")  # set this in Render secrets!

# Dummy server and credentials for example purposes
class DummyServer:
    def authenticate_begin(self, credentials, user_verification):
        return {"challenge": "dummy-challenge"}, "dummy-state"

    def authenticate_complete(self, state, credential, data):
        return {"status": "ok"}

server = DummyServer()
credentials = {"example": "cred"}  # Replace with real creds in production

# ================= LOGIN =================
@app.route("/login/begin", methods=["GET"])
def login_begin():
    auth_data, state = server.authenticate_begin(
        credentials.values(),
        user_verification="required"
    )

    session["state"] = state
    return Response(cbor.dumps(auth_data), content_type="application/cbor")

@app.route("/login/complete", methods=["POST"])
def login_complete():
    data = cbor.loads(request.data)
    state = session["state"]

    credential_id = data.get("rawId", "example")  # Replace with real decoding if needed

    auth_data = server.authenticate_complete(
        state,
        credentials.get(credential_id),
        data
    )

    return redirect("/")

# ================= HOME =================
@app.route("/")
def home():
    return "🎉 Secret Vault is LIVE! 🎉"

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
