# events/user_deleted.py

from pydantic import BaseModel
from loguru import logger


# Define Pydantic model for validation
class UserDeletedData(BaseModel):
    userId: str


# Event handler function
async def handle_event(sid: str, data: UserDeletedData, sio):
    logger.info(f"Handling user deletion for SID '{sid}' with data: {data.dict()}")

    # Here you can add logic for deleting the user from a database
    # Emit a success acknowledgment back to the client
    await sio.emit("userDeleted_ack", {"status": "success", "message": "User deleted successfully"}, room=sid)
