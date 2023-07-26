# client.py - flask routing instance

from flask import Flask, render_template, request, session, flash, redirect, current_app, json
import requests
from datetime import datetime
from flask_socketio import SocketIO
import rsa
import aes
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/connect')
def connect():
    if 'username' not in session:
        return render_template('login.html')
    return flash("Connected successfully!")

@app.route('/disconnect')
def disconnect():
    session.pop('username', None)
    return flash('You have been disconnected.')

@app.route('/')
def index():
    flash("Click Login Button to Continue.")
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if request.method == 'OPTIONS':
            response = current_app.make_default_options_response()

        # Make a request to the login API
        response = requests.post('http://server:8000/api/login', json={'username': username, 'password': password})

        # If the request is successful, set the username and keys in the session
        if response.status_code == 200:
            data = response.json()
            session['username'] = username
            session['client_private_key'] = data["client_key"]
            session['server_public_key'] = data["server_key"]
            session['client_public_key'] = data["client_key"]  # Store the client public key in the session
            # Also store the server's public key in a variable for encryption
            global server_public_key
            server_public_key = rsa.PublicKey.load_pkcs1(data["server_key"].encode())
            # print(server_public_key)
            return redirect('/chat')
        # Else if the request is not successful, display an error message.
        else:
            error = "Invalid username or password."
            flash('Enter values in both username and password.')
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/chat')
def chat():
    if 'username' not in session or 'client_private_key' not in session or 'server_public_key' not in session:
        return redirect('/login')

    current_user = {
        'username': session['username'],
        'avatar': '#',  # Replace with the actual avatar path
        'is_online': True  # Set the online status based on your logic
    }

    return render_template('chat.html', current_user=current_user)


@socketio.on()
def handle_connect():
    print("Client connected")


@socketio.on('message')
def handle_message(data):
    message = data['messages']
    print("Received encrypted message:", message)

    # Decrypt the message using the client's private key
    decrypted_messages = decrypt_messages(data['messages'])
    print("Decrypted messages:", decrypted_messages)

    # Broadcast the decrypted message to all connected clients
    socketio.emit('send_message', {
        'sender': session['username'],
        'messages': decrypted_messages,
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")


def decrypt_messages(encrypted_messages):
    client_private_key_data = session['client_private_key']
    client_private_key = rsa.PrivateKey.load_pkcs1(client_private_key_data.encode())

    decrypted_messages = []
    for message in encrypted_messages:
        encrypted_session_key_bytes = base64.b64decode(message["encrypted_session_key"].encode())
        session_key = rsa.decrypt(encrypted_session_key_bytes, client_private_key)
        ciphertext = base64.b64decode(message["ciphertext"].encode())
        decrypted_message = aes.decrypt(ciphertext, session_key).decode()

        decrypted_messages.append({
            "sender": message["sender"],
            "text": decrypted_message,
            "timestamp": message["timestamp"]
        })

    return decrypted_messages


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
