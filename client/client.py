from flask import Flask, render_template, request, session
from jinja2 import Template
from flask_wtf.csrf  import CSRFProtect

app = Flask(__name__)

app.secret_key = "your_secret_key"

CSRFProtect(app)

@app.route('/connect')
def connect():
    if 'username' not in session:
        return render_template('login.html')
    return 'You are connected!'

@app.route('/disconnect')
def disconnect():
    session.pop('username', None)
    return 'You have been disconnected.'

@app.route('/')
def index():
    # if 'username' not in session:
    #     return render_template('login.html')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect('/')
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return render_template('login.html')
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
