# mq6_v2.py

"""
mq6_v2 - An enhanced message queue abstraction layer for educational purposes.

This script sets up a FastAPI application integrated with Socket.IO to handle real-time messaging.
It includes comprehensive logging, error handling, and supports publishing messages via both HTTP endpoints and Socket.IO events.

Author: Your Name
Date: YYYY-MM-DD
"""

import asyncio
import importlib
import inspect
import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, get_type_hints
from uuid import uuid4

import socketio
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError, ConfigDict
from starlette.middleware.base import BaseHTTPMiddleware

from dslmodel.conditional_cors_middleware import ConditionalCORSMiddleware

from loguru import logger

# Initialize FastAPI application
app = FastAPI(
    title="mq6_v2 Message Queue",
    description="An enhanced message queue abstraction layer for educational purposes.",
    version="2.0.0",
)

# CORS middleware configuration
ALLOWED_ORIGINS = ["http://localhost:3000"]  # Ensure this is only listed once

# Add conditional CORS middleware to exclude '/socket.io' path
app.add_middleware(
    ConditionalCORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    exclude_paths=["/socket.io"],
)

# Initialize Socket.IO AsyncServer with CORS settings
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=ALLOWED_ORIGINS,  # Allow only the specified origins
    logger=logger,
    engineio_logger=logger,
)
socket_app = socketio.ASGIApp(sio)
app.mount("/socket.io", socket_app, name="socketio")

# Message handlers registry
TOPIC_REGISTRY: Dict[str, Callable[[Any], Any]] = {}
CHANNEL_REGISTRY: Dict[str, Callable[[Any], Any]] = {}


# Pydantic models
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    topic: Optional[str] = None
    channel: Optional[str] = None
    routing_key: str = "default-slug"
    content_type: str = "application/json"
    content: Any
    sender: str = "system"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    message_type: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    raw_data: Optional[Any] = None

    # Update for Pydantic v2
    model_config = ConfigDict(populate_by_name=True)

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


# Middleware for logging requests
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"Incoming request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.exception("Exception occurred during request processing.")
            raise e


app.add_middleware(LoggingMiddleware)


# Message creation function
def create_message(
        content: Any,
        topic: Optional[str] = None,
        channel: Optional[str] = None,
        routing_key: str = "default-slug",
        content_type: str = "application/json",
        sender: str = "system",
        message_type: Optional[str] = None,
        attributes: Dict[str, Any] = None,
        raw_data: Optional[Any] = None,
) -> Message:
    """
    Factory function to create a Message with sensible defaults.
    """
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


# Decorators for registering handlers
def channel(name: str):
    """
    Decorator to register a function to a specific channel.
    """

    def decorator(func: Callable[[Message], Any]):
        CHANNEL_REGISTRY[name] = func
        logger.debug(f"Registered channel handler: {name}")
        return func

    return decorator


def topic(name: str):
    """
    Decorator to register a function to a specific topic.
    """

    def decorator(func: Callable[[Message], Any]):
        TOPIC_REGISTRY[name] = func
        logger.debug(f"Registered topic handler: {name}")
        return func

    return decorator


# Message publishing function
async def publish_message(message: Message):
    """
    Broadcast a message to WebSocket clients based on topic or channel.
    """
    try:
        if message.topic and message.topic in TOPIC_REGISTRY:
            handler = TOPIC_REGISTRY[message.topic]
            logger.info(f"Handling message for topic '{message.topic}'.")
            await handler(message)
            await sio.emit(message.topic, message.dict(exclude_none=True))
            logger.info(f"Emitted message to topic '{message.topic}': {message.content}")
        elif message.channel and message.channel in CHANNEL_REGISTRY:
            handler = CHANNEL_REGISTRY[message.channel]
            logger.info(f"Handling message for channel '{message.channel}'.")
            await handler(message)
            await sio.emit(message.channel, message.dict(exclude_none=True))
            logger.info(f"Emitted message to channel '{message.channel}': {message.content}")
        else:
            error_msg = "Message must have a valid topic or channel to be published."
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception as e:
        logger.exception("Failed to publish message.")
        raise e


# HTTP endpoints
@app.get("/send_message")
async def send_example_message():
    """
    Example endpoint demonstrating message creation and publishing.
    """
    message = create_message(content="Hello from mq6_v2!", topic="health")
    await publish_message(message)
    return {"status": "Message sent"}


@app.post("/publish_message")
async def publish_message_endpoint(message_input: MessageInput):
    """
    Endpoint to create and publish a message dynamically.
    """
    try:
        if not message_input.topic and not message_input.channel:
            error_msg = "Message must have a topic or a channel."
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

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
    except ValidationError as ve:
        logger.error(f"ValidationError: {ve}")
        raise HTTPException(status_code=422, detail=ve.errors())
    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("An unexpected error occurred while publishing the message.")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """
    Handle new client connections.
    """
    logger.info(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    """
    Handle client disconnections.
    """
    logger.info(f"Client disconnected: {sid}")


@sio.event
async def publish(sid, data):
    """
    Handle 'publish' events emitted by clients.
    """
    logger.info(f"Received 'publish' from {sid}: {data}")
    try:
        message_input = MessageInput(**data)

        if not message_input.topic and not message_input.channel:
            error_msg = "Message must have a topic or a channel."
            logger.error(error_msg)
            await sio.emit("error", {"detail": error_msg}, to=sid)
            return

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
        await sio.emit("publish_ack", {"status": "Message published successfully."}, to=sid)
    except ValidationError as ve:
        logger.error(f"ValidationError: {ve}")
        await sio.emit("error", {"detail": "Invalid message format."}, to=sid)
    except Exception as e:
        logger.exception("Error in 'publish' handler.")
        await sio.emit("error", {"detail": "Internal Server Error."}, to=sid)


# Step 1: Data Validation Function
def validate_data(func: Callable, data: Any) -> Any:
    type_hints = get_type_hints(func)
    model = type_hints.get('data', None)

    if model and issubclass(model, BaseModel):
        try:
            # Validate data using the Pydantic model
            logger.debug(f"Validating data for function '{func.__name__}' with model '{model.__name__}'")
            return model(**data)
        except ValidationError as e:
            logger.error(f"Validation error for function '{func.__name__}': {e.errors()}")
            return e.errors()
    return data


# Step 2: Inspect Function Signature
def expects_sio_parameter(func: Callable) -> bool:
    signature = inspect.signature(func)
    expects_sio = 'sio' in signature.parameters
    logger.debug(f"Function '{func.__name__}' expects 'sio' parameter: {expects_sio}")
    return expects_sio


# Step 3: Event Wrapper
def create_event_wrapper(event_name: str, func: Callable) -> Callable:
    async def wrapper(sid: str, data: Any, *args, **kwargs) -> Any:
        logger.info(f"Handling event '{event_name}' from sid '{sid}' with data: {data}")

        # Step 3.1: Validate data
        validated_data_or_error = validate_data(func, data)

        # If validation fails, emit an error and return early
        if isinstance(validated_data_or_error, list):
            await sio.emit("error", {"error": validated_data_or_error}, room=sid)
            logger.error(f"Validation failed for event '{event_name}' with errors: {validated_data_or_error}")
            return

        validated_data = validated_data_or_error

        # Step 3.2: Add `sio` to kwargs if required
        if expects_sio_parameter(func):
            kwargs['sio'] = sio
            logger.debug(f"Adding 'sio' to kwargs for function '{func.__name__}'")

        # Step 3.3: Call the original function
        logger.debug(f"Calling function '{func.__name__}' for event '{event_name}'")
        return await func(sid, validated_data, *args, **kwargs)

    # Register the wrapper function as an event handler with Socket.IO
    sio.on(event_name, wrapper)
    logger.info(f"Registered event '{event_name}' with function '{func.__name__}'")


# Step 4: Register Individual Event Handler
def register_event_handler(module_name: str, func: Callable) -> None:
    event_name = module_name  # Use the filename (module_name) as the event name
    logger.debug(f"Registering event handler for module '{module_name}'")
    create_event_wrapper(event_name, func)


# Step 5: Discover and Register Event Handlers from Filesystem
def register_events(event_directory: str = "events"):
    logger.info(f"Registering events from directory '{event_directory}'")
    for filename in os.listdir(event_directory):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            logger.debug(f"Importing module '{module_name}' from directory '{event_directory}'")

            try:
                module = importlib.import_module(f"{event_directory}.{module_name}")
            except Exception as e:
                logger.error(f"Failed to import module '{module_name}': {str(e)}")
                continue

            # Specifically look for a function named 'handle_event' in the module
            if hasattr(module, 'handle_event'):
                handle_event_func = getattr(module, 'handle_event')
                if callable(handle_event_func) and inspect.iscoroutinefunction(handle_event_func):
                    logger.debug(f"Found 'handle_event' function in module '{module_name}'")
                    # Register the 'handle_event' function for the module
                    register_event_handler(module_name, handle_event_func)
                else:
                    logger.warning(f"'handle_event' in module '{module_name}' is not a coroutine function")
            else:
                logger.warning(f"No 'handle_event' function found in module '{module_name}'")


# Example handlers using decorators
@topic("health")
async def handle_health_message(message: Message):
    """
    Handler for 'health' topic messages.
    """
    logger.info(f"Handling health message: {message.content}")
    # Implement your business logic here


@channel("notification/email")
async def handle_email_notification(message: Message):
    """
    Handler for 'notification/email' channel messages.
    """
    logger.info(f"Handling email notification: {message.content}")
    # Implement your business logic here


# Main entry point
if __name__ == "__main__":
    # Register the event handlers
    register_events()

    uvicorn.run(
        "mq6_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False in production
        log_level="info",
    )
