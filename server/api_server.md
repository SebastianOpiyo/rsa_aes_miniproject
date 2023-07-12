# API Server Documentation

# APIs Docs
* `/connect:` This API establishes a session. It takes no input and returns a JSON object with the success key set to True.
* `/disconnect:` This API ends a session. It takes no input and returns a JSON object with the success key set to True.
* `/login:` This API handles the login process. It takes a username and password as input and returns the client and server public keys.
* `/chat:` This API handles the chat messages. It takes a list of messages as input and returns the encrypted messages and their signatures.
* `/:` This API is the home page of the chat application. It renders the index.html template.

# Test the APIs using Postman
