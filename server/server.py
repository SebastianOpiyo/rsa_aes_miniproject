import flask
import rsa
import aes
from jinja2 import Template
from flask_wtf import CsrfProtect


app = flask.Flask(__name__)

CsrfProtect(app)

@app.route("/")
def index():
    """
    This is the home page of the chat application.
    """
    return flask.render_template("index.html")

@app.route("/login")
def login():
    """
    This route handles the login process.
    """
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    if not username or not password:
        return flask.render_template("login.html", error="Please enter a username and password.")

    client_key = rsa.generate_key()
    server_key = rsa.generate_key()

    flask.session["client_key"] = client_key.export_public_key()
    flask.session["server_key"] = server_key.export_public_key()

    return flask.render_template("chat.html", username=username)

@app.route("/chat")
def chat():
    """
    This route handles the chat messages.
    """
    username = flask.session["username"]
    client_key = rsa.import_key(flask.session["client_key"])
    server_key = rsa.import_key(flask.session["server_key"])

    messages = []

    for message in flask.request.get_json():
        message_text = message["text"]
        message_ciphertext = aes.encrypt(message_text, client_key)
        message_signature = rsa.sign(message_ciphertext, server_key)

        messages.append({
            "text": message_text,
            "ciphertext": message_ciphertext,
            "signature": message_signature
        })

    return flask.jsonify(messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
