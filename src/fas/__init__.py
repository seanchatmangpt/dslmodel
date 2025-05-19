from typing import Any, Dict, Optional
from loguru import logger

class MockSocketIO:
    def __init__(self):
        self.handlers = {}
        self.rooms = {}

    def on(self, event: str, handler: callable) -> None:
        """Register an event handler."""
        self.handlers[event] = handler
        logger.debug(f"Registered handler for event '{event}'")

    async def emit(self, event: str, data: Any, room: Optional[str] = None) -> None:
        """Emit an event to a room."""
        logger.debug(f"Emitting event '{event}' to room '{room}' with data: {data}")
        if room in self.rooms:
            for sid in self.rooms[room]:
                if event in self.handlers:
                    await self.handlers[event](sid, data)

    def enter_room(self, sid: str, room: str) -> None:
        """Add a client to a room."""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(sid)
        logger.debug(f"Client '{sid}' entered room '{room}'")

    def leave_room(self, sid: str, room: str) -> None:
        """Remove a client from a room."""
        if room in self.rooms and sid in self.rooms[room]:
            self.rooms[room].remove(sid)
            logger.debug(f"Client '{sid}' left room '{room}'")

# Create a singleton instance
sio = MockSocketIO() 