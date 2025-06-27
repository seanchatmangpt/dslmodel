# client.py

"""
client.py - Demonstrates interaction with the mq6_v2.py server using Socket.IO and HTTP.

This script connects to the Socket.IO server, publishes messages to specific topics,
and interacts with HTTP endpoints to publish messages to channels.

Author: Your Name
Date: YYYY-MM-DD
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx
import socketio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("client")

# Server configuration
SOCKET_IO_URL = "http://localhost:8000/socket.io"
HTTP_ENDPOINT_URL = "http://localhost:8000/publish_message"

# Initialize the asynchronous Socket.IO client with logging enabled
sio = socketio.AsyncClient(logger=True, engineio_logger=True)


async def connect_socketio():
    """
    Connect to the Socket.IO server.
    """

    # Define event handlers
    @sio.event
    async def connect():
        logger.info("Successfully connected to the Socket.IO server.")

    @sio.event
    async def connect_error(data):
        logger.error(f"Connection failed: {data}")

    @sio.event
    async def disconnect():
        logger.info("Disconnected from the Socket.IO server.")

    @sio.event
    async def publish_ack(data):
        logger.info(f"Publish Acknowledgment received: {data}")

    @sio.event
    async def error(data):
        logger.error(f"Error received from server: {data}")

    try:
        # Connect to the server
        await sio.connect(
            SOCKET_IO_URL,
            transports=["websocket"],
            namespaces=["/"],
        )
    except Exception as e:
        logger.exception("An error occurred while connecting to the Socket.IO server.")


async def publish_via_socketio(topic: str, content: Any):
    """
    Publish a message to a specific topic via Socket.IO.

    Parameters:
    - topic: The topic name to publish the message to.
    - content: The content of the message.
    """
    message = {
        "content": content,
        "topic": topic,
    }

    try:
        logger.info(f"Publishing message to topic '{topic}' via Socket.IO: {content}")
        await sio.emit("publish", message)
    except Exception as e:
        logger.exception("An error occurred while emitting the 'publish' event.")


async def publish_via_http(content: Any, topic: Optional[str] = None, channel: Optional[str] = None):
    """
    Publish a message via the HTTP POST endpoint.

    Parameters:
    - content: The content of the message.
    - topic: (Optional) The topic name to publish the message to.
    - channel: (Optional) The channel name to publish the message to.
    """
    payload: Dict[str, Any] = {
        "content": content,
    }

    if topic:
        payload["topic"] = topic
    if channel:
        payload["channel"] = channel

    headers = {
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            if channel:
                target = f"channel '{channel}'"
            elif topic:
                target = f"topic '{topic}'"
            else:
                target = "unknown target"

            logger.info(f"Publishing message via HTTP to {target}: {content}")
            response = await client.post(HTTP_ENDPOINT_URL, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"HTTP Response: {response.json()}")
        except httpx.HTTPStatusError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - Response: {http_err.response.text}")
        except Exception as e:
            logger.exception("An unexpected error occurred while publishing via HTTP.")


async def main():
    """
    Main function to orchestrate the client operations.
    """
    # Connect to the Socket.IO server
    await connect_socketio()

    # Wait briefly to ensure connection is established
    await asyncio.sleep(1)

    # Publish a message via Socket.IO to the 'health' topic
    await publish_via_socketio(topic="health", content="Health check via Socket.IO")

    # Publish a message via HTTP to the 'notification/email' channel
    await publish_via_http(content="Email notification via HTTP", channel="notification/email")

    # Optionally, wait to receive acknowledgments or other events
    await asyncio.sleep(2)

    # Disconnect from the Socket.IO server
    await sio.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
