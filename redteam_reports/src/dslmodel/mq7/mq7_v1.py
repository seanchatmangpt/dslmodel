import socketio
from fastapi import FastAPI
from loguru import logger

# Initialize FastAPI application
app = FastAPI(
    title="mq7_v2 Message Queue",
    description="A message queue abstraction layer with Socket.IO and FastAPI.",
    version="1.0.0",
)

sio = socketio.AsyncServer(async_mode='asgi', logger=True, engineio_logger=True, cors_allowed_origins=[
    'http://localhost:3000',
    'https://admin.socket.io',
])

# Create ASGI app for Socket.IO and wrap FastAPI app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)  # Configure Loguru Logger

logger.add("logs/debug.log", rotation="1 MB", level="DEBUG", retention="10 days")
