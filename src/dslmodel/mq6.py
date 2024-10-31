# mq6.py

import asyncio
from datetime import datetime, UTC
from uuid import uuid4
from typing import Optional, Any, Dict, Callable
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import socketio
from starlette.middleware.base import BaseHTTPMiddleware

# Initialize FastAPI and Socket.IO
app = FastAPI()

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify only the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Logging middleware to debug CORS
class CORSDebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        print(f"Handling request path: {request.url.path}, method: {request.method}")
        if request.method == "OPTIONS":
            print(f"OPTIONS request for {request.url.path} - CORS pre-flight check")
        response = await call_next(request)
        return response


app.add_middleware(CORSDebugMiddleware)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=["http://localhost:3000"])
socket_app = socketio.ASGIApp(socketio_server=sio)

app.mount("/socket.io", socket_app)

# Registry for topic and channel event handlers
TOPIC_REGISTRY: Dict[str, Callable] = {}
CHANNEL_REGISTRY: Dict[str, Callable] = {}


# Pydantic v2 Message model with factory function for creation
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    topic: Optional[str] = None
    channel: Optional[str] = None
    routing_key: str = "default-slug"
    content_type: str = "application/json"
    content: Any
    sender: str = "system"
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    message_type: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    raw_data: Optional[Any] = None

    class Config:
        populate_by_name = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.raw_data is None:
            self.raw_data = self.content


class MessageInput(BaseModel):
    """Model for incoming JSON payload in the POST request."""
    content: Any
    topic: Optional[str] = None
    channel: Optional[str] = None
    routing_key: str = "default-slug"
    content_type: str = "application/json"
    sender: str = "system"
    message_type: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


def create_message(
        content: Any,
        topic: Optional[str] = None,
        channel: Optional[str] = None,
        routing_key: str = "default-slug",
        content_type: str = "application/json",
        sender: str = "system",
        message_type: Optional[str] = None,
        attributes: dict = None,
        raw_data: Optional[Any] = None,
) -> Message:
    """Factory function to create a Message with sensible defaults."""
    return Message(
        content=content,
        topic=topic,
        channel=channel,
        routing_key=routing_key,
        content_type=content_type,
        sender=sender,
        message_type=message_type,
        attributes=attributes or {},
        raw_data=raw_data,
    )


# Decorators to register functions for specific channels and topics
def channel(name: str):
    """Decorator to register a function to a specific channel."""

    def decorator(func: Callable):
        CHANNEL_REGISTRY[name] = func

        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def topic(name: str):
    """Decorator to register a function to a specific topic."""

    def decorator(func: Callable):
        TOPIC_REGISTRY[name] = func

        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Publish messages to topics or channels based on registry
async def publish_message(message: Message):
    """Broadcast a message to WebSocket clients based on topic or channel."""
    if message.topic and message.topic in TOPIC_REGISTRY:
        handler = TOPIC_REGISTRY[message.topic]
        await handler(message)  # Call the registered function for the topic
        await sio.emit(message.topic, message.dict(by_alias=True))

    elif message.channel and message.channel in CHANNEL_REGISTRY:
        handler = CHANNEL_REGISTRY[message.channel]
        await handler(message)  # Call the registered function for the channel
        await sio.emit(message.channel, message.dict(by_alias=True))
    else:
        raise ValueError("Message must have either a valid topic or a valid channel to be published.")


# Example endpoint demonstrating message creation and publishing
@app.get("/send_message")
async def send_example_message():
    # Create a message with a specified topic
    message = create_message(content="Hello from mq6!", topic="health")
    await publish_message(message)
    return {"status": "Message sent"}


# POST endpoint for dynamic message creation and publishing
@app.post("/publish_message")
async def publish_message_endpoint(message_input: MessageInput):
    """Endpoint to create and publish a message dynamically."""
    if not message_input.topic and not message_input.channel:
        raise HTTPException(status_code=400, detail="Message must have a topic or a channel.")

    message = create_message(
        content=message_input.content,
        topic=message_input.topic,
        channel=message_input.channel,
        routing_key=message_input.routing_key,
        content_type=message_input.content_type,
        sender=message_input.sender,
        message_type=message_input.message_type,
        attributes=message_input.attributes,
    )
    await publish_message(message)
    return JSONResponse(content={"status": "Message published successfully"})


# Event handlers for client connection and disconnection
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


# Example usage of @topic and @channel decorators
@topic("health")
async def handle_health_message(message: Message):
    print(f"Handling health message: {message.content}")


@channel("notification/email")
async def handle_email_notification(message: Message):
    print(f"Handling email notification: {message.content}")


# Run the application with Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
