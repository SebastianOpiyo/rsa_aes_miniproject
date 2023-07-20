import os
import flask
from flask_wtf.csrf import CSRFProtect
import rsa
import aes
from datetime import datetime


app = flask.Flask(__name__)

# Get secret key from environment variable or set a default
app.secret_key = os.environ.get('SECRET_KEY', 'JtZ*3zF2Q^7g7mGwYcDT#ue5*D8h%E7jD9m&BdsxVWiJihW9TzZ$P%Fne&EW#!4t')

# Cross Site Request Forgery (CSRF) settings
app.config["CSRF_ENABLED"] = True
app.config["CSRF_SESSION_KEY"] = app.secret_key

# Create a set to store the connected WebSocket clients
connected_clients = set()

@app.route("/api/")
def index():
    """
    This is the home endpoint of the application.
    Returns a welcome message.
    """
    message = "You are looking for a secure chat app? Well our RSA and AES secure chat app will do just fine for you."
    return flask.jsonify({"homecontent": message})

@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    """
    This endpoint handles the login process.
    It takes the username and password from the request JSON.
    It then generates new RSA keys for the client and server, and stores them in the session.
    """
    # Check if the request method is OPTIONS
    if flask.request.method == 'OPTIONS':
        # Create a default response for OPTIONS requests
        response = flask.current_app.make_default_options_response()

    # Get the username and password from the request JSON
    username = flask.request.json["username"]
    password = flask.request.json["password"]

    # Check if both the username and password are provided
    if not username or not password:
        return flask.jsonify({"error": "Please enter a username and password."})

    # Generate new RSA keys for the client and the server
    client_key = rsa.newkeys(512)
    server_key = rsa.newkeys(512)

    # Store the keys and username in the session
    flask.session["client_key"] = client_key[0].save_pkcs1().decode()
    flask.session["server_key"] = server_key[0].save_pkcs1().decode()
    flask.session["username"] = username

    # Return the public keys to the client
    return flask.jsonify({
        "client_key": client_key[0].save_pkcs1().decode(),
        "server_key": server_key[0].save_pkcs1().decode()
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    This endpoint handles the chat messages.
    It gets the client and server keys from the session and loads them.
    It then gets the JSON data from the request, and for each message in the data, 
    it encrypts the message text using AES with the client's public key and signs the ciphertext with the server's private key.
    It then broadcasts the encrypted and signed message to all connected clients.
    """
    # Get the username from the session
    username = flask.session.get("username")
    if not username:
        return flask.jsonify({"error": "User not logged in."})
    
    # Get the client and server keys from the session and load them
    client_key_data = flask.session["client_key"]
    server_key_data = flask.session["server_key"]
    client_key = rsa.PublicKey.load_pkcs1(client_key_data.encode())
    server_key = rsa.PublicKey.load_pkcs1(server_key_data.encode())

    try:
        # Get the JSON data from the request
        data = flask.request.get_json()

        if not isinstance(data, list):
            raise ValueError("Invalid JSON data. Expected a list.")

        messages = []
        for message in data:
            # Validate the message format
            if not isinstance(message, dict) or "text" not in message:
                raise ValueError("Invalid message format.")

            # Get the message text from the message
            message_text = message["text"]

            # Encrypt the message text using AES with the client's public key
            message_ciphertext = aes.encrypt(message_text.encode(), client_key)

            # Sign the ciphertext with the server's private key
            message_signature = rsa.sign(message_ciphertext, server_key)

            # Add the encrypted and signed message to the messages list
            messages.append({
                "sender": username,
                "text": message_text,
                "ciphertext": message_ciphertext.decode(),
                "signature": message_signature.decode(),
                "timestamp": datetime.utcnow().isoformat()
            })

        # Broadcast the message to all connected clients
        for client in connected_clients:
            client.send(flask.jsonify({"data": messages}).data)

        return flask.jsonify({"success": True})

    except ValueError as e:
        return flask.jsonify({"error": str(e)})

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

        # Start receiving messages from the client
        while True:
            message = ws.receive()
            if message:
                # Process and broadcast the received message to all connected clients
                data = [{"text": message}]
                chat()

    return flask.jsonify({"success": True})

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

if __name__ == "__main__":
    """
    This is the entry point of the application.
    It runs the Flask server with the application.
    """
    app.run(debug=False, host="0.0.0.0", port=8000)