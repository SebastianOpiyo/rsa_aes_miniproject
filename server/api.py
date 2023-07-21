import flask
import rsa
import aes
from flask_wtf.csrf import CSRFProtect
from datetime import datetime


app = flask.Flask(__name__)

app.secret_key = "your_secret_key"

# Cross Site Request Forgery (CSRF)
app.config["CSRF_ENABLED"] = True
app.config["CSRF_SESSION_KEY"] = app.secret_key
# CSRFProtect(app)

# Store the connected WebSocket clients
connected_clients = set()

# Store the client public keys
client_public_keys = {}

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

    flask.session["client_key"] = client_key[0].save_pkcs1().decode()
    flask.session["server_key"] = server_key[0].save_pkcs1().decode()
    flask.session["username"] = username  # Set the username in the session

    # Share server public key and client public key with the cleint
    return flask.jsonify({
        "client_key": client_key[1].save_pkcs1().decode(),
        "server_key": server_key[0].save_pkcs1().decode()
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    This route handles the chat messages.
    """
    username = flask.session.get("username")
    if not username:
        return flask.jsonify({"error": "User not logged in."})
    
    client_key_data = flask.session["client_key"]
    server_key_data = flask.session["server_key"]

    client_key = rsa.PublicKey.load_pkcs1(client_key_data.encode())
    server_key = rsa.PublicKey.load_pkcs1(server_key_data.encode())

    try:
        data = flask.request.get_json()

        if not isinstance(data, list):
            raise ValueError("Invalid JSON data. Expected a list.")

        messages = []
        for message in data:
            if not isinstance(message, dict) or "text" not in message:
                raise ValueError("Invalid message format.")

            message_text = message["text"]
            message_ciphertext = aes.encrypt(message_text.encode(), client_key)
            message_signature = rsa.sign(message_ciphertext, server_key)

            messages.append({
                "sender": username,
                "text": message_text,
                "ciphertext": message_ciphertext.decode(),
                "signature": message_signature.decode(),
                "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat()
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
    This route establishes a WebSocket connection and adds the client to the set of connected clients.
    """
    # Create a WebSocket connection
    ws = flask.request.environ.get("wsgi.websocket")

    # Check if WebSocket connection is established
    if ws:
        connected_clients.add(ws)

        # Receive messages from the WebSocket client
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
    This route removes the WebSocket client from the set of connected clients.
    """
    ws = flask.request.environ.get("wsgi.websocket")
    if ws in connected_clients:
        connected_clients.remove(ws)
    return flask.jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)