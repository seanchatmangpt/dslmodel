import os
import importlib
from typing import Callable, Any, get_type_hints
from pydantic import BaseModel, ValidationError
import socketio
import inspect

# Initialize Socket.IO server
sio = socketio.AsyncServer(async_mode='aiohttp')


# Step 1: Data Validation Function
def validate_data(func: Callable, data: Any) -> Any:
    type_hints = get_type_hints(func)
    model = type_hints.get('data', None)

    if model and issubclass(model, BaseModel):
        try:
            # Validate data using the Pydantic model
            return model(**data)
        except ValidationError as e:
            return e.errors()
    return data


# Step 2: Inspect Function Signature
def expects_sio_parameter(func: Callable) -> bool:
    signature = inspect.signature(func)
    return 'sio' in signature.parameters


# Step 3: Event Wrapper
def create_event_wrapper(event_name: str, func: Callable) -> Callable:
    async def wrapper(sid: str, data: Any, *args, **kwargs) -> Any:
        # Step 3.1: Validate data
        validated_data_or_error = validate_data(func, data)

        # If validation fails, emit an error and return early
        if isinstance(validated_data_or_error, list):
            await sio.emit("error", {"error": validated_data_or_error}, room=sid)
            return

        validated_data = validated_data_or_error

        # Step 3.2: Add `sio` to kwargs if required
        if expects_sio_parameter(func):
            kwargs['sio'] = sio

        # Step 3.3: Call the original function
        return await func(sid, validated_data, *args, **kwargs)

    # Register the wrapper function as an event handler with Socket.IO
    sio.on(event_name, wrapper)


# Step 4: Register Individual Event Handler
def register_event_handler(module_name: str, func: Callable) -> None:
    event_name = module_name  # Use the filename (module_name) as the event name
    create_event_wrapper(event_name, func)


# Step 5: Discover and Register Event Handlers from Filesystem
def register_events(event_directory: str = "events"):
    for filename in os.listdir(event_directory):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            module = importlib.import_module(f"{event_directory}.{module_name}")

            # Iterate over attributes in the module and register coroutines
            for attribute_name in dir(module):
                if not attribute_name.startswith("_"):
                    func = getattr(module, attribute_name)
                    if callable(func) and inspect.iscoroutinefunction(func):
                        register_event_handler(module_name, func)


# Register the event handlers
register_events()

# Main entry point for starting the server (assuming you have an AioHTTP web application)
if __name__ == "__main__":
    import aiohttp.web

    app = aiohttp.web.Application()
    sio.attach(app)
    aiohttp.web.run_app(app, port=5000)