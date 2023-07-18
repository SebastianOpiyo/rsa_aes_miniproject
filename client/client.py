# Client Routes
from flask import Flask, render_template, request, session, flash, redirect, current_app, json 
import requests
from datetime import datetime
from flask_socketio import SocketIO


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

        # If the request is successful, set the username in the session
        if response.status_code == 200:
            session['username'] = username
            return redirect('/chat')
        # Else if the request is not successful, display an error message.
        else:
            error = "Invalid username or password."
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        data = request.get_json(force=True)
        if not isinstance(data, list):
            flash('Invalid message format')
            return redirect('/chat')

        # Set the headers with 'application/json' content type
        headers = {'Content-Type': 'application/json'}

        # We make a request to the chat API
        response = requests.post('http://server:8000/api/chat', data=data, headers=headers)

        # Upon successful request, get the chat messages
        if response.status_code == 200:
            data = response.json().get("data", [])
            for message in data:
                message['sender'] = session['username']
                message['timestamp'] = datetime.strptime(message['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
        else:
            flash('Error: Failed to send message.')
            data = []

        current_user = {
            'username': session['username'],
            'avatar': '#',  # Replace with the actual avatar path
            'is_online': True  # Set the online status based on your logic
        }

        return render_template('chat.html', current_user=current_user, messages=data)

    # Handle GET request
    if request.method == 'GET':
        # We make a request to the chat API to retrieve the chat messages
        response = requests.get('http://server:8000/api/chat')

        # Upon successful request, get the chat messages
        if response.status_code == 200:
            data = response.json().get("data", [])
            for message in data:
                message['timestamp'] = datetime.strptime(message['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
        else:
            flash('Error: Failed to retrieve chat messages.')
            data = []

        current_user = {
            'username': session['username'],
            'avatar': '#',  # Replace with the actual avatar path
            'is_online': True  # Set the online status based on your logic
        }

        return render_template('chat.html', current_user=current_user, messages=data)

    return redirect('/chat')


@socketio.on('message')
def handle_message(data):
    message = data['message']
    username = session.get('username')
    if username and message:
        send_message(username, message)

def send_message(sender, message):
    socketio.emit('message', {'sender': sender, 'message': message}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
