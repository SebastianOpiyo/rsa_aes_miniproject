# api.py - API file
import flask
import rsa
import aes
from datetime import datetime, timezone
from flask import json

app = flask.Flask(__name__)

app.secret_key = "your_secret_key"

# Store the connected WebSocket clients
connected_clients = set()

# Store the client public keys
client_public_keys = {}

# Store the server private key
server_private_key = None

@app.route("/api/")
def index():
    """
    This is the home page of the chat application.
    """
    message = "You are looking for a secure chat app? Well our RSA and AES secure chat app will do just fine for you."
    return flask.jsonify({"homecontent": message})

@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    """
    This route handles the login process.
    """

    if flask.request.method == 'OPTIONS':
        response = flask.current_app.make_default_options_response()

    username = flask.request.json["username"]
    password = flask.request.json["password"]

    if not username or not password:
        return flask.jsonify({"error": "Please enter a username and password."})

    client_key = rsa.newkeys(512)
    server_key = rsa.newkeys(512)

    flask.session["client_key"] = client_key[1].save_pkcs1().decode()
    flask.session["server_key"] = server_key[0].save_pkcs1().decode()
    flask.session["username"] = username  # Set the username in the session
    print(flask.session)

    # Share server public key and client public key with the client
    return flask.jsonify({
        "server_key": server_key[0].save_pkcs1().decode(),
        "client_key": client_key[1].save_pkcs1().decode()
    })


@app.route("/api/chat", methods=["GET", "POST"])
def chat():
    """
    This route handles the chat messages.
    """
    username = flask.session.get("username")
    if not username:
        return flask.jsonify({"error": "User not logged in."})

    # Parse the JSON data from the request
    data = flask.request.json

    if not data or "messages" not in data:
        return flask.jsonify({"error": "Invalid data."})

    messages = data["messages"]

    # Validate the data
    if not isinstance(messages, list):
        return flask.jsonify({"error": "Invalid data format."})

    for message in messages:
        if "sender" not in message or "text" not in message or "timestamp" not in message:
            return flask.jsonify({"error": "Invalid message format."})

    # Add the sender username to each message
    for message in messages:
        message["sender"] = username

    # Add a timestamp to each message
    for message in messages:
        message["timestamp"] = datetime.now(timezone.utc).astimezone().isoformat()

    # Broadcast the messages to all connected clients
    broadcast(messages)

    return flask.jsonify({"status": "Message sent successfully!"})


@app.route("/api/connected_clients")
def get_connected_clients():
    """
    Get the list of currently connected clients.
    """
    return flask.jsonify(list(connected_clients))


@app.route("/api/public_key", methods=["POST"])
def receive_public_key():
    """
    Receive and store the public key of the connected client.
    """
    data = flask.request.json
    if "username" in data and "public_key" in data:
        username = data["username"]
        public_key = data["public_key"]
        client_public_keys[username] = public_key
        return flask.jsonify({"status": "Public key received successfully!"})
    else:
        return flask.jsonify({"error": "Invalid data format."})


@app.route("/api/encrypt_message", methods=["POST"])
def encrypt_message():
    """
    Encrypt a message using the public key of the recipient.
    """
    data = flask.request.json
    if "recipient" in data and "message" in data:
        recipient = data["recipient"]
        message = data["message"]

        if recipient not in client_public_keys:
            return flask.jsonify({"error": "Recipient public key not found."})

        # Load the recipient's public key
        public_key = rsa.PublicKey.load_pkcs1(client_public_keys[recipient].encode())

        # Encrypt the message using the recipient's public key
        encrypted_message = aes.encrypt(message.encode(), public_key)

        return flask.jsonify({"encrypted_message": encrypted_message.decode()})
    else:
        return flask.jsonify({"error": "Invalid data format."})


def broadcast(messages):
    """
    Broadcast messages to all connected clients.
    """
    for client in connected_clients:
        client.send(json.dumps(messages))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
