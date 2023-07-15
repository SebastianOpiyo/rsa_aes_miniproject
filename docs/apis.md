# API Summary
`/`
- This is the home page of the chat application. It simply renders the index.html template.

`/login`
- This route handles the login process. It takes a username and password as JSON parameters and returns a JSON object with the client and server public keys.

`/chat`
- This route handles the chat messages. It takes a list of chat messages as JSON parameters and returns a JSON object with the encrypted messages and their signatures.

`/connect`
- This route establishes a session. It simply returns a JSON object with the success flag set to True.

`/disconnect`
- This route ends a session. It clears the session and returns a JSON object with the success flag set to True.


### API Summary table.

| API | Parameters | Return value |
|---|---|---|
| `/` | None | None |
| `/login` | `username` (string), `password` (string) | `client_key` (string), `server_key` (string) |
| `/chat` | `messages` (list of objects) | `messages` (list of objects) |
| `/connect` | None | `{"success": True}` |
| `/disconnect` | None | `{"success": True}` |

The `messages` object in the `/chat` and `/disconnect` responses is a list of objects with the following properties:

* `text`: The text of the message.
* `ciphertext`: The encrypted message.
* `signature`: The signature of the encrypted message.
