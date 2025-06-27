from pydantic import BaseModel
from loguru import logger


# Define Pydantic model for validation
class OnLightMeasuredPayload(BaseModel):
    id: int
    lumens: int
    sentAt: str


# Event handler function
async def handle_event(sid: str, data: OnLightMeasuredPayload, sio):
    logger.info(f"Handling onLightMeasured for SID '{sid}' with data: {data.model_dump()}")

    # Add your logic here, such as updating database records, etc.
    # Emit a success acknowledgment back to the client
    await sio.emit("onLightMeasured_ack", 
                   {"status": "success", 
                    "message": "onLightMeasured handled successfully"}, 
                   room=sid)
    