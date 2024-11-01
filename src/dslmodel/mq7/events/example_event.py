from pydantic import BaseModel
import socketio


# Example Pydantic model
class ExampleModel(BaseModel):
    username: str
    score: int


async def handle_event(sid: str, data: ExampleModel, sio: socketio.AsyncServer) -> None:
    print(f"Received data from {sid}: {data}")
    # Emit response to the client
    await sio.emit("response", {"message": "Data received successfully"}, room=sid)
