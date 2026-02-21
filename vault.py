import os
from flask import Flask, render_template, request, session, redirect, url_for

# --- Config ---
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")
PIN = os.environ.get("PIN", "1234")
FILE = os.environ.get("FILE", "secrets.txt")

# --- Routes ---

@app.route("/")
def home():
    if session.get("logged_in"):
        if os.path.exists(FILE):
            with open(FILE, "r") as f:
                notes = f.read()
        else:
            notes = ""
        return render_template("home.html", notes=notes)
    return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/pin-login", methods=["POST"])
def pin_login():
    pin = request.form.get("pin")
    if pin == PIN:
        session["logged_in"] = True
        return redirect(url_for("home"))
    return "Wrong PIN!", 401

@app.route("/add", methods=["POST"])
def add_note():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))
    note = request.form.get("note")
    with open(FILE, "a") as f:
        f.write(note + "\n")
    return redirect(url_for("home"))

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login_page"))

# --- WebAuthn placeholders ---
@app.route("/webauthn-challenge")
def webauthn_challenge():
    # Here you would return challenge options for WebAuthn
    return {}

@app.route("/verify-login", methods=["POST"])
def verify_login():
    # Here you would verify the WebAuthn credential
    # For now, just auto-login for testing
    session["logged_in"] = True
    return {}, 200

# --- Run ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
