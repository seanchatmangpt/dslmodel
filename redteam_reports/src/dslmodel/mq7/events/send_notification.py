# events/send_notification.py

from pydantic import BaseModel


# Define Pydantic model for validation
class SendNotificationData(BaseModel):
    userId: str
    message: str
    priority: str


# Event handler function
async def handle_event(sid: str, data: SendNotificationData, sio, logger):
    logger.info(f"Handling send notification for SID '{sid}' with data: {data.dict()}")

    # Logic to send notification, such as pushing to a message queue or notifying the user
    await sio.emit("sendNotification_ack", {"status": "success", "message": "Notification sent successfully"}, room=sid)
