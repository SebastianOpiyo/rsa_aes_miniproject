# To be used in production sever
from client import app, socketio

if __name__ == '__main__':
    socketio.run(app)