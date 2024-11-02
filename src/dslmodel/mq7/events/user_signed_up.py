# events/user_signed_up.py

from pydantic import BaseModel, EmailStr
from loguru import logger


# Define Pydantic model for validation
class UserSignedUpData(BaseModel):
    fullName: str
    email: EmailStr
    age: int


# Event handler function
async def handle_event(sid: str, data: UserSignedUpData, sio):
    logger.info(f"Handling user sign-up for SID '{sid}' with data: {data.dict()}")

    # Here you can add any logic, such as saving the user to a database
    # For demonstration, emit a success acknowledgment back to the client
    await sio.emit("userSignedUp_ack", {"status": "success", "message": "User signed up successfully"}, room=sid)
