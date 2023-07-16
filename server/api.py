import flask
import rsa
import aes
from jinja2 import Template
from flask_wtf.csrf import CSRFProtect
#from time import datetime
from datetime import datetime


app = flask.Flask(__name__)

app.secret_key = "your_secret_key"

CSRFProtect(app)

@app.route("/")
def index():
    """
    This is the home page of the chat application.
    """
    message = "You are looking for a secure chat app? Well our RSA and AES secure chat app will do\
    just fine fo you."
    return flask.jsonify({"homecontent":message})

@app.route("/login", methods=["POST"])
def login():
    """
    This route handles the login process.
    """
    username = flask.request.json["username"]
    password = flask.request.json["password"]

    if not username or not password:
        return flask.jsonify({"error": "Please enter a username and password."})

    client_key = rsa.generate_key()
    server_key = rsa.generate_key()

    flask.session["client_key"] = client_key.export_public_key()
    flask.session["server_key"] = server_key.export_public_key()

    return flask.jsonify({
        "client_key": client_key.export_public_key(),
        "server_key": server_key.export_public_key()
    })

@app.route("/chat", methods=["POST"])
def chat():
    """
    This route handles the chat messages.
    """
    username = flask.session["username"]
    client_key = rsa.import_key(flask.session["client_key"])
    server_key = rsa.import_key(flask.session["server_key"])

    messages = []

    for message in flask.request.json:
        message_text = message["text"]
        message_ciphertext = aes.encrypt(message_text, client_key)
        message_signature = rsa.sign(message_ciphertext, server_key)

        messages.append({
            "sender": username,
            "text": message_text,
            "ciphertext": message_ciphertext,
            "signature": message_signature,
            "timestamp": datetime.utcnow()
        })

    return flask.jsonify(messages)


@app.route("/connect", methods=["POST"])
def connect():
    """
    This route establishes a session.
    """
    return flask.jsonify({"success": True})

@app.route("/disconnect", methods=["POST"])
def disconnect():
    """
    This route ends a session.
    """
    flask.session.clear()
    return flask.jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
