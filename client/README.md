# Flask Chat Client Application

The client application for the Flask Chat is a simple, intuitive, and responsive real-time chat application. It's designed with user-friendliness in mind, ensuring that you have the best chat experience.

## Key Features

- **User Authentication**: The application includes a secure login system.
- **Real-Time Communication**: Leveraging WebSocket technology for instantaneous message delivery and display.
- **Connection Status**: It provides connection status information - indicating whether you're connected or disconnected from the chat.

## Architecture

The application follows a Model-View-Controller (MVC) structure:

- **View**: These are the templates (HTML files) that create the user interface.
- **Controller**: This is represented by the routes in the Flask application. They handle the requests and responses to and from the client.
- **Model**: This is the data related to the application. In this case, it's mostly the user information stored in sessions.

## Dependencies

- Flask: A Python micro web framework used to create web applications.
- Flask-SocketIO: Provides Flask applications access to low latency bi-directional communications between the clients and the server.
- Requests: Used to send HTTP requests to the server.

## Endpoints

- **'/'**: The root endpoint that renders the landing page.
- **'/connect'**: Manages WebSocket connections.
- **'/disconnect'**: Disconnects WebSocket connections.
- **'/login'**: Manages the login process.
- **'/chat'**: The main endpoint that manages chat interactions.

## User Flow

1. The user lands on the homepage and clicks on the login button to continue.
2. The login page is displayed, where the user enters their username and password.
3. If the login is successful, the user is redirected to the chat page.
4. If the user is already logged in, they can go directly to the chat page.
5. On the chat page, the user can send and receive real-time messages.
6. The user's connection status is also displayed.

## Getting Started

Ensure you have Docker installed and navigate to the client directory. Build and run the Docker container by executing the following commands:

```
docker build -t flask-chat-client .
docker run -p 5000:5000 flask-chat-client
```

This will start the client, and you can access it by visiting `http://localhost:5000` in your web browser.
