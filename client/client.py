from flask import Flask, render_template, request, session, flash
from jinja2 import Template
from flask_wtf.csrf  import CSRFProtect
import requests

app = Flask(__name__)

app.secret_key = "your_secret_key"

CSRFProtect(app)

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

        # Make a request to the login api
        response = requests.post('http://localhost:8000/login', json={'username': username, 'password': password})

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
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
