mlface is a systemd service that does face recogition. It listens as 
a websocket on port 4785. A base64 encoded jpg is sent to '/' path.
returned is a json response (like Shinobi wants if we where to use it)
