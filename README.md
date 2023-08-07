# Secure Chat Application - Server and Client

This project consists of a secure chat application built using Python's Flask framework, and JavaScript for the client-side. The application uses RSA and AES encryption for secure communication between users.

## Server

### Introduction
The server-side application is built using Flask and uses RSA and AES for secure communication. It handles login, messaging, and WebSocket connection management.

### Key Modules
- `Flask`: A micro web framework written in Python.
- `rsa`: A Python RSA cryptography module.
- `aes`: A Python Advanced Encryption Standard (AES) cryptography module.
- `flask_wtf.csrf`: Cross-Site Request Forgery (CSRF) protection for Flask applications.

## System Design Diagram

```mermaid
sequenceDiagram
    participant User as User Interface
    participant Client as Client App
    participant Server as Server App
    Note over User,Client: User enters username and password
    User->>Client: Login
    Client->>Server: Send login details
    alt successful login
        Server-->>Client: Send back RSA keys
        Client-->>User: Show success message
    else unsuccessful login
        Server-->>Client: Send back error message
        Client-->>User: Show error message
    end
    Note over User,Client: User writes a message
    User->>Client: Submit message
    Client->>Server: Send message data
    alt successful message sent
        Server-->>Client: Message delivered
        Client->>User: Update chat interface
    else unsuccessful message sent
        Server-->>Client: Send back error message
        Client-->>User: Show error message
    end
    Note over User,Client: User decides to logout/disconnect
    User->>Client: Disconnect
    Client->>Server: Send disconnect request
    Server-->>Client: Acknowledge disconnect
    Client-->>User: Show disconnection success message
``````

### Routes
The server application has five main routes:

1. `/api/` : Home endpoint of the application returning a welcome message.
2. `/api/login` : Handles the login process with a POST request containing a username and password in JSON format.
3. `/api/chat` : Handles chat messages by receiving a JSON object containing the message to be sent, encrypting it using AES with the client's public key, signing the ciphertext with the server's private key, and broadcasting the message to all connected clients.
4. `/api/connect` : Establishes a WebSocket connection and adds the client to the set of connected clients. It then starts receiving messages from the client and forwards them to the `/api/chat` endpoint.
5. `/api/disconnect` : Removes a WebSocket client from the set of connected clients.

The server is run on a server by calling the `run()` method of the Flask application object.

## Client

### Introduction
The client-side of the application is built using JavaScript. It provides the user interface for the chat application and handles login, messaging, and WebSocket connection management.

### Key Features
- `Login`: The login function handles the user authentication process. It sends a request to the `/api/login` endpoint with the username and password provided by the user.
- `Chat`: The chat function handles sending and receiving messages. It sends a POST request to the `/api/chat` endpoint when the user submits a message, and it listens for incoming messages from the server.
- `WebSocket Connection`: The connect function establishes a WebSocket connection with the server, while the disconnect function closes the WebSocket connection.

The application also uses Jinja2 templating to display information such as the current user's username and the list of chat messages. The status of the user (online/offline) is also updated dynamically based on the WebSocket connection status.

## Installation and Usage
Both server and client applications can be dockerized using Docker. Docker allows you to package an application with all its dependencies into a standardized unit for software development. Dockerfiles and a docker-compose file are provided for this purpose.

To build and run the applications, use the following command in the terminal:

```bash
docker-compose up --build
```

This will start the server at `http://localhost:8000` and the client at `http://localhost:5000`. You can then navigate to `http://localhost:5000` in your web browser to use the chat application.
