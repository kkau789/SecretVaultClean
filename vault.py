from flask import Flask, request, redirect

app = Flask(__name__)

FILE = "secrets.txt"
PIN = "1234"

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        pin = request.form.get("pin")
        if pin == PIN:
            return redirect("/vault")
        else:
            return "Wrong PIN"

    return '''
        <h2>Enter PIN</h2>
        <form method="post">
            <input type="password" name="pin">
            <button type="submit">Login</button>
        </form>
    '''

@app.route("/vault", methods=["GET", "POST"])
def vault():
    if request.method == "POST":
        note = request.form.get("note")
        with open(FILE, "a") as f:
            f.write(note + "\\n")

    secrets = ""
    try:
        with open(FILE, "r") as f:
            secrets = f.read()
    except:
        pass

    return f'''
        <h2>Secret Vault</h2>
        <form method="post">
            <input name="note">
            <button type="submit">Add Note</button>
        </form>
        <pre>{secrets}</pre>
    '''
