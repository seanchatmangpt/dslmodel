import socketio
import asyncio
from pydantic import BaseModel, EmailStr, ValidationError
import logging

# Enable detailed Socket.IO logging for troubleshooting
sio = socketio.AsyncClient(logger=True, engineio_logger=True)

# Configure basic logging
logging.basicConfig(level=logging.INFO)


# Define Pydantic Models for each event's payload based on AsyncAPI

class UserSignedUpData(BaseModel):
    fullName: str
    email: EmailStr
    age: int


class UserUpdatedData(BaseModel):
    userId: str
    fullName: str
    email: EmailStr
    age: int


class UserDeletedData(BaseModel):
    userId: str


class SendNotificationData(BaseModel):
    userId: str
    message: str
    priority: str


# Connection event handlers

@sio.event
async def connect():
    logging.info("Successfully connected to the server.")

    # Emit a userSignedUp event as a test
    try:
        signup_data = UserSignedUpData(fullName="Alice", email="alice@example.com", age=30).dict()
        await sio.emit('userSignedUp', signup_data)
        logging.info("Emitted userSignedUp event.")
    except ValidationError as e:
        logging.error(f"Validation error for userSignedUp event: {e.json()}")

    # Emit a userUpdated event as a test
    try:
        update_data = UserUpdatedData(userId="123", fullName="Alice", email="alice_updated@example.com", age=31).dict()
        await sio.emit('userUpdated', update_data)
        logging.info("Emitted userUpdated event.")
    except ValidationError as e:
        logging.error(f"Validation error for userUpdated event: {e.json()}")

    # Emit a sendNotification event as a test
    try:
        notification_data = SendNotificationData(userId="123", message="Welcome to the system!", priority="high").dict()
        await sio.emit('sendNotification', notification_data)
        logging.info("Emitted sendNotification event.")
    except ValidationError as e:
        logging.error(f"Validation error for sendNotification event: {e.json()}")


@sio.event
async def connect_error(data):
    logging.error("Failed to connect to the server.")


@sio.event
async def disconnect():
    logging.info("Disconnected from server.")


# Handlers for specific events that the server might emit

@sio.event
async def userDeleted(data):
    try:
        validated_data = UserDeletedData(**data)
        logging.info(f"Received userDeleted event: {validated_data}")
    except ValidationError as e:
        logging.error(f"Validation error for received userDeleted event: {e.json()}")


@sio.event
async def userSignedUp_ack(data):
    logging.info(f"Received acknowledgment for userSignedUp: {data}")


@sio.event
async def userUpdated_ack(data):
    logging.info(f"Received acknowledgment for userUpdated: {data}")


@sio.event
async def sendNotification_ack(data):
    logging.info(f"Received acknowledgment for sendNotification: {data}")


@sio.event
async def error(data):
    logging.error(f"Error received from server: {data}")


# Main function to run the client
async def main():
    try:
        await sio.connect('http://localhost:8000')
        await sio.wait()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


# Run the client
if __name__ == "__main__":
    asyncio.run(main())
