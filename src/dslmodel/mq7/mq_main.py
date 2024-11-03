# import os
# import importlib
# from typing import Callable, Any, get_type_hints
# from pydantic import BaseModel, ValidationError
# import socketio
# import inspect
# from loguru import logger
# import inflection  # Import inflection for converting snake_case to camelCase
#
# # Initialize Socket.IO server
# sio = socketio.AsyncServer(async_mode='aiohttp', logger=True, engineio_logger=True, cors_allowed_origins=[
#     'http://localhost:3000',
#     'https://admin.socket.io',
# ])
#
# # Configure Loguru Logger
# logger.add("logs/debug.log", rotation="1 MB", level="DEBUG", retention="10 days")
#
#
# # Step 1: Data Validation Function
#
#
# def validate_data(func: Callable, data: Any) -> Any:
#     type_hints = get_type_hints(func)
#     model = type_hints.get('data', None)
#
#     if model and issubclass(model, BaseModel):
#         try:
#             # Validate data using the Pydantic model
#             logger.debug(f"Validating data for function '{func.__name__}' with model '{model.__name__}'")
#             return model(**data)
#         except ValidationError as e:
#             logger.error(f"Validation error for function '{func.__name__}': {e.errors()}")
#             return e.errors()
#     return data
#
#
# # Step 2: Inspect Function Signature
# def expects_sio_parameter(func: Callable) -> bool:
#     signature = inspect.signature(func)
#     expects_sio = 'sio' in signature.parameters
#     logger.debug(f"Function '{func.__name__}' expects 'sio' parameter: {expects_sio}")
#     return expects_sio
#
#
# # Step 3: Event Wrapper
# def create_event_wrapper(event_name: str, func: Callable) -> Callable:
#     async def wrapper(sid: str, data: Any, *args, **kwargs) -> Any:
#         logger.info(f"Handling event '{event_name}' from sid '{sid}' with data: {data}")
#
#         # Step 3.1: Validate data
#         validated_data_or_error = validate_data(func, data)
#
#         # If validation fails, emit an error and return early
#         if isinstance(validated_data_or_error, list):
#             await sio.emit("error", {"error": validated_data_or_error}, room=sid)
#             logger.error(f"Validation failed for event '{event_name}' with errors: {validated_data_or_error}")
#             return
#
#         validated_data = validated_data_or_error
#
#         # Step 3.2: Add `sio` to kwargs if required
#         if expects_sio_parameter(func):
#             kwargs['sio'] = sio
#             logger.debug(f"Adding 'sio' to kwargs for function '{func.__name__}'")
#
#         # Step 3.3: Call the original function
#         logger.debug(f"Calling function '{func.__name__}' for event '{event_name}'")
#         return await func(sid, validated_data, *args, **kwargs)
#
#     # Register the wrapper function as an event handler with Socket.IO
#     sio.on(event_name, wrapper)
#     logger.info(f"Registered event '{event_name}' with function '{func.__name__}'")
#
#
# # Step 4: Register Individual Event Handler
# def register_event_handler(module_name: str, func: Callable) -> None:
#     # Convert the snake_case module name to camelCase for the event name
#     event_name = inflection.camelize(module_name, uppercase_first_letter=False)
#     logger.debug(f"Registering event handler for module '{module_name}' as event '{event_name}'")
#     create_event_wrapper(event_name, func)
#
#
# # Step 5: Discover and Register Event Handlers from Filesystem
# def register_events(event_directory: str = "events"):
#     logger.info(f"Registering events from directory '{event_directory}'")
#     for filename in os.listdir(event_directory):
#         if filename.endswith(".py"):
#             module_name = filename[:-3]  # Remove the ".py" extension
#             logger.debug(f"Importing module '{module_name}' from directory '{event_directory}'")
#
#             try:
#                 # Dynamically import the module
#                 module = importlib.import_module(f"{event_directory}.{module_name}")
#             except Exception as e:
#                 logger.error(f"Failed to import module '{module_name}': {str(e)}")
#                 continue
#
#             # Look for a function named 'handle_event' in the module
#             if hasattr(module, 'handle_event'):
#                 handle_event_func = getattr(module, 'handle_event')
#                 if callable(handle_event_func) and inspect.iscoroutinefunction(handle_event_func):
#                     logger.debug(f"Found 'handle_event' function in module '{module_name}'")
#                     # Register the 'handle_event' function for the module with converted event name
#                     register_event_handler(module_name, handle_event_func)
#                 else:
#                     logger.warning(f"'handle_event' in module '{module_name}' is not a coroutine function")
#             else:
#                 logger.warning(f"No 'handle_event' function found in module '{module_name}'")
#
#
# # Register the event handlers
# register_events()
#
# # Main entry point for starting the server (assuming you have an AioHTTP web application)
# if __name__ == "__main__":
#     import aiohttp.web
#
#     logger.info("Starting the AioHTTP server on port 4000")
#     app = aiohttp.web.Application()
#     sio.attach(app)
#     aiohttp.web.run_app(app, port=8000)
