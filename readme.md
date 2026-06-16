# Chat App
- This is a real-time chat system using Django + WebSockets.

* The Problem: Normal HTTP requests are one-way (you ask, server responds). Chat needs two-way, instant communication.
* The Solution: WebSockets — a persistent connection where server and client can both send messages anytime.

### ASGI SERVER
In order to handle the websocket requests we need to use asgi server. The asgi server checks if the request is HTTP or websocket and handles both the requests accordingly.

```
Client (Browser)
        ↓
   Makes a connection
        ↓
ASGI Server (Daphne / Uvicorn)        ← actual software running on your machine
        ↓
   asgi.py (your app's entry point)
        ↓
ProtocolTypeRouter  ← "what kind of connection is this?"
   ↙                        ↘
HTTP                      WebSocket
(normal request)          (persistent connection)
  ↓                              ↓
Django                    AuthMiddlewareStack  ← is user logged in?
handles it                       ↓
normally               URLRouter  ← which URL? /ws/chat/5/ ?
(views, templates)               ↓
                         ChatConsumer  ← your code runs here
                         (connect, receive, disconnect)
```

### Web Socket Routing
Just like Django's normal ```urls.py``` we use ```routing.py``` for routing websockets urls and send it to `consumers.py`.
```
Normal Django:
URL match → views.py

Django Channels (WebSocket):
URL match → consumers.py
```
- consumers.py is to WebSockets what views.py is to HTTP. ONLY difference is 
* A view handles one request and returns a response, done.
* A consumer stays open and handles multiple events — connect, receive, disconnect — over time.

### CONSUMERS
Consumers is like view for HTTP where we handle the websocket requests.
Here we make function to connect, disconnect, etc

