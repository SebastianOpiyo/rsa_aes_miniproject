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
    
    client_public_key_data = flask.session.get("client_public_key")
    if not client_public_key_data:
        return flask.jsonify({"error": "Client public key not found in session."})

    client_public_key = rsa.PublicKey.load_pkcs1(client_public_key_data.encode())
    client_public_keys[username] = client_public_key

    if flask.request.method == "POST":
        try:
            data = flask.request.get_json()

            if not isinstance(data, list):
                raise ValueError("Invalid JSON data. Expected a list.")

            messages = []
            for message in data:
                if not isinstance(message, dict) or "text" not in message:
                    raise ValueError("Invalid message format.")

                message_text = message["text"]

                # Encrypt the messages with the client's public key
                encrypted_messages = encrypt_messages(username, message_text)
                messages.extend(encrypted_messages)

            # Broadcast the encrypted message to all connected clients
            for client in connected_clients:
                if client.username in client_public_keys:
                    # Encrypt the messages with the client's public key before sending
                    encrypted_messages = encrypt_messages(client.username, messages)
                    client.send(flask.jsonify({"data": encrypted_messages}).data)

            return flask.jsonify({"success": True})

        except ValueError as e:
            return flask.jsonify({"error": str(e)})
        
    elif flask.request.method == "GET":
        # Handle the GET request
        return flask.jsonify({"info": "Chat is active."})
    else:
        return flask.jsonify({"error": "Method not allowed."}), 405
    

@app.route("/api/connect", methods=["POST"])
def connect():
    """
    This endpoint establishes a WebSocket connection and adds the client to the set of connected clients.
    It then starts receiving messages from the client, and for each received message, 
    it calls the chat function to process and broadcast the message to all connected clients.
    """
    # Get the WebSocket connection from the request
    ws = flask.request.environ.get("wsgi.websocket")

    # Check if a WebSocket connection is established
    if ws:
        # Add the client to the set of connected clients
        connected_clients.add(ws)
        ws.username = flask.session.get("username")  # Store the username in the WebSocket object

        # Start receiving messages from the client
        while True:
            data = ws.receive()
            if data:
                # Process and broadcast the received message to all connected clients
                # messages = json.loads(data)["messages"]
                # handle_received_messages(ws.username, messages)  # Process and broadcast the received messages
                username = data["username"]
                ws.username = username # Store the username in the WebSocket object
                print(f"WebSocket connection established for user: {username}")
    return flask.jsonify({"success": True})


def handle_received_messages(sender_username, messages):
    # Encrypt the message with the senders username
    encrypted_messages = encrypt_messages(sender_username, messages)

    # Broadcast the encrypted messages to all connected clients
    for client in connected_clients:
        if client.username in client_public_keys:
            client.send(flask.jsonify({"data": encrypted_messages}).data)


@app.route("/api/disconnect", methods=["POST"])
def disconnect():
    """
    This endpoint removes the WebSocket client from the set of connected clients.
    """
    # Get the WebSocket connection from the request
    ws = flask.request.environ.get("wsgi.websocket")

    # Remove the client from the set of connected clients
    if ws in connected_clients:
        connected_clients.remove(ws)
    return flask.jsonify({"success": True})

def encrypt_messages(username, messages):
    encrypted_messages = []
    client_public_key = client_public_keys.get(username)
    if not client_public_key:
        raise ValueError("Client public key not found for username: " + username)

    for message in messages:
        session_key = aes.generate_key()
        message_ciphertext = aes.encrypt(message["text"].encode(), session_key)
        message_signature = rsa.sign(message_ciphertext, server_private_key)

        # Encrypt the session key using the client's public key
        encrypted_session_key = rsa.encrypt(session_key, client_public_key)

        encrypted_messages.append({
            "sender": message["sender"],
            "text": message["text"],
            "ciphertext": message_ciphertext.decode(),
            "signature": message_signature.decode(),
            "encrypted_session_key": encrypted_session_key.decode(),
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        })

    return encrypted_messages



if __name__ == "__main__":
    server_private_key = rsa.newkeys(512)[1]
    app.run(debug=True, host="0.0.0.0", port=8000)
