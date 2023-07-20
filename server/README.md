# Secure Chat Server Application

## Introduction
This is a secure chat server application built using Flask, an extensible web microframework for building web applications with Python. The server integrates RSA and AES for secure communication.

## Modules
The application mainly uses four modules:
- `Flask`: A micro web framework written in Python.
- `rsa`: A Python RSA cryptography module.
- `aes`: A Python Advanced Encryption Standard (AES) cryptography module.
- `flask_wtf.csrf`: Cross-Site Request Forgery (CSRF) protection for Flask applications.

## Main Application Object
An instance of the Flask class is the main application object. It's serving as the central object. 
```python
app = flask.Flask(__name__)
```
A secret key is configured for the Flask application to ensure the integrity of the cookies used in the session.

## CSRF Protection
The server uses CSRF protection, a security feature that helps protect against particular types of unwanted harmful activities, specifically the unauthorized commands that are transmitted from a user that the web application trusts.
```python
app.config["CSRF_ENABLED"] = True
app.config["CSRF_SESSION_KEY"] = app.secret_key
```
## WebSocket Clients
All connected WebSocket clients are stored in a set called `connected_clients`.

## Routes
The application has multiple routes, each with a specific role:

1. `/api/` : Serves as the home endpoint of the application and returns a welcome message.

2. `/api/login` : Handles the login process by accepting a POST request containing a username and password in JSON format.

3. `/api/chat` : Handles the chat messages. It receives a JSON object containing the message to be sent, encrypts it using AES with the client's public key, signs the ciphertext with the server's private key, and then broadcasts the message to all connected clients.

4. `/api/connect` : Establishes a WebSocket connection and adds the client to the set of connected clients. It then starts receiving messages from the client and forwards them to the `/api/chat` endpoint.

5. `/api/disconnect` : Removes a WebSocket client from the set of connected clients.

## Running the Server
The application is run on a server by calling the `run()` method of the Flask application object.
```python
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
```
In this case, the server is running in non-debug mode, listening on all IP addresses `0.0.0.0` and on port `8000`.
