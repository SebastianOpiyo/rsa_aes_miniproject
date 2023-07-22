from flask import Flask, render_template, request, session, flash, redirect, current_app, json
import requests
from datetime import datetime
from flask_socketio import SocketIO
import rsa
import aes

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

# Function to encrypt the message with the server's public key
def encrypt_message(message):
    server_public_key_data = session['server_public_key']
    server_public_key = rsa.PublicKey.load_pkcs1(server_public_key_data.encode())
    session_key = aes.generate_key()
    ciphertext = aes.encrypt(message.encode(), session_key)
    encrypted_session_key = rsa.encrypt(session_key, server_public_key)
    encrypted_message = {
        "ciphertext": ciphertext,
        "encrypted_session_key": encrypted_session_key
    }
    return json.dumps(encrypted_message)

@socketio.on('connect')
def handle_connect():
    print("Client connected")


@socketio.on('message')
def handle_message(data):
    message = data['message']
    print("Received encrypted message:", message)

    # Decrypt the message using the client's private key
    decrypted_message = decrypt_message_with_client_key(message['ciphertext'], message['encrypted_session_key'])
    print("Decrypted message:", decrypted_message)

    # Broadcast the decrypted message to all connected clients
    socketio.emit('send_message', {
        'sender': session['username'],
        'text': decrypted_message,
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

def encrypt_messages_with_server_key(messages):
    encrypted_data = []
    for message in messages:
        encrypted_message = encrypt_message_with_server_key(message["text"])
        encrypted_data.append({"text": encrypted_message})
    return encrypted_data

def encrypt_message_with_server_key(message):
    server_public_key_data = session['server_public_key']
    server_public_key = rsa.PublicKey.load_pkcs1(server_public_key_data)
    session_key = aes.generate_key()
    ciphertext = aes.encrypt(message.encode(), session_key)
    encrypted_session_key = rsa.encrypt(session_key, server_public_key)
    encrypted_message = {
        "ciphertext": ciphertext,
        "encrypted_session_key": encrypted_session_key
    }
    return json.dumps(encrypted_message)

def decrypt_message_with_client_key(ciphertext, encrypted_session_key):
    client_private_key_data = session['client_private_key']
    client_private_key = rsa.PrivateKey.load_pkcs1(client_private_key_data.encode())
    session_key = rsa.decrypt(encrypted_session_key, client_private_key)
    decrypted_message = aes.decrypt(ciphertext.encode(), session_key)
    return decrypted_message.decode()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
