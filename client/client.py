from flask import Flask, render_template, request, session, flash, redirect, current_app
from jinja2 import Template
from flask_wtf.csrf  import CSRFProtect
import requests
from datetime import datetime

app = Flask(__name__)

app.secret_key = "your_secret_key"

# CSRFProtect(app)
app.config["CSRF_ENABLED"] = True
app.config["CSRF_SESSION_KEY"] = app.secret_key


@app.route('/connect')
def connect():
    if 'username' not in session:
        return render_template('login.html')
    return flash("Connected successfuly!")

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

        # Make a request to the login api
        response = requests.post('http://localhost:8000/api/login', json={'username': username, 'password': password})

        # If the request is successful, set the username in the session
        if response.status_code == 200:
            session['username'] = username
            return redirect('/chat')
        # Else if the request is not successful, display an error message.
        else:
            error = "Invalid username or password."
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/chat')
def chat():
    if 'username' not in session:
        return render_template('login.html')
    
    # We make a request to the chat API
    response = requests.get('http://localhost:5000/api/chat', params={'username': session['username']})

    # Upon successful request, get the chat messages
    if response.status_code == 200:
        chat_messages = response.json()
        for message in chat_messages:
            message['sender'] = session['username']
            message['timestamp'] = datetime.utcnow()
    else:
        flash('Error: There are no messages or the backend services is down.')
        chat_messages = []
    return render_template('chat.html', chat_messages= chat_messages)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
