from flask import Flask, render_template, request, session, flash, redirect, current_app, json 
import requests
import os
from datetime import datetime
from flask_socketio import SocketIO

# Set up the Flask application and SocketIO
app = Flask(__name__)

# Get secret key from environment variable or set a default
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'Fhm%xhi&Au2rTBp@X$MNsV^PR&t$C*c4M!bU&%6wiYw7s4fNC$@L8zfH%k&nN7Lz')

socketio = SocketIO(app)

@app.route('/connect')
def connect():
    """
    This endpoint is used to manage WebSocket connections. 
    It checks if a username is in the session, if not it renders the login page. 
    Otherwise, it flashes a "Connected successfully!" message.
    """
    if 'username' not in session:
        return render_template('login.html')
    return flash("Connected successfully!")

@app.route('/disconnect')
def disconnect():
    """
    This endpoint disconnects the WebSocket connection by removing the username from the session.
    It then flashes a "You have been disconnected." message.
    """
    session.pop('username', None)
    return flash('You have been disconnected.')

@app.route('/')
def index():
    """
    This is the root endpoint. It flashes a "Click Login Button to Continue." message 
    and then renders the index page.
    """
    flash("Click Login Button to Continue.")
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This endpoint handles the login process. It first checks if the request method is POST.
    If it is, it takes the username and password from the form and makes a request to the login API.
    If the request is successful, it sets the username in the session and redirects the user to the chat page.
    If the request is unsuccessful, it flashes an "Enter values in both username and password." error message.
    If the request method is not POST, it renders the login page.
    """
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
            flash('Enter values in both username and password.')
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """
    This endpoint manages chat interactions. It first checks if a username is in the session,
    if not it redirects to the login page.
    If the request method is POST, it gets the JSON data from the request.
    It checks if the data is a list, if not it flashes an "Invalid message format" error message.
    It then makes a request to the chat API and gets the chat messages if the request is successful.
    It then renders the chat page with the current user and messages.
    If the request method is GET, it makes a request to the chat API to retrieve the chat messages
    and then renders the chat page with the current user and messages.
    """
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
        response = requests.post('http://server:8000/api/chat', data=json.dumps(data), headers=headers)

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
    """
    This is a SocketIO event handler for 'message' events. 
    It gets the message from the data and the username from the session.
    If both are present, it sends the message.
    """
    message = data['message']
    username = session.get('username')
    if username and message:
        send_message(username, message)

def send_message(sender, message):
    """
    This function emits a 'message' event with the sender and message as data.
    """
    socketio.emit('message', {'sender': sender, 'message': message})

if __name__ == '__main__':
    """
    This is the entry point of the application.
    It runs the Flask server with the application.
    """
    socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
