import socketio
import asyncio
from pydantic import BaseModel


# Pydantic Model for Happy Path Scenario
class EventData(BaseModel):
    message: str
    count: int
    username: str
    score: int


# Initialize Socket.IO Client
sio = socketio.AsyncClient()


# Define event handlers for client-side events
@sio.event
async def connect():
    print("Successfully connected to the server!")
    # Emit a happy path event when connected
    data = EventData(message="Hello from client!", count=42, username="test_user", score=100).dict()
    await sio.emit('example_event', data)


@sio.event
async def connect_error(data):
    print("Failed to connect to the server.")


@sio.event
async def disconnect():
    print("Disconnected from server.")


@sio.event
async def response(data):
    print(f"Received response for 'example_event': {data}")


@sio.event
async def error(data):
    print(f"Error received: {data}")


# Main function to run the client
async def main():
    try:
        await sio.connect('http://localhost:4000')
        await sio.wait()
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Run the client
if __name__ == "__main__":
    asyncio.run(main())
