kfrom flask import Flask, request, session, redirect, Response
import os
import cbor  # make sure cbor2 is installed
# from your_server_module import server, credentials, websafe_encode, websafe_decode

app = Flask(__name__)
app.secret_key = os.urandom(24)  # random secret key for session

# =============== ROOT ===============
@app.route("/")
def home():
    return """
    <h2>Secret Vault</h2>
    <p>Go to <a href='/login/begin'>Login</a> to start authentication.</p>
    """

# =============== LOGIN ===============
@app.route("/login/begin", methods=["GET"])
def login_begin():
    # Example placeholders for server.auth
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

# =============== RUN ===============
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
