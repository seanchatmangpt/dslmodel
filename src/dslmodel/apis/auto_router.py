from fastapi import FastAPI, APIRouter, HTTPException, Body
from typing import Type, Dict, Any
from dslmodel import DSLModel, init_lm
import inspect

app = FastAPI()  # Initialize FastAPI


def auto_router(model_class: Type[DSLModel]):
    """
    Decorator to automatically register REST API routes for a DSLModel class.
    """
    router = APIRouter()
    model_name = model_class.__name__.lower()

    # Create endpoint to generate a model instance from prompt
    @router.post(f"/{model_name}/")
    async def create_model_instance(data: Dict[str, Any] = Body(...)):
        init_lm()  # Initialize the language model
        try:
            instance = model_class.from_prompt(**data)
            return instance.model_dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Create endpoint to return the model's JSON schema
    @router.get(f"/{model_name}/schema")
    async def get_model_schema():
        try:
            return model_class.model_json_schema()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Register the router with the FastAPI app
    app.include_router(router)

    # Return the original class to maintain decorator behavior
    return model_class


from pydantic import Field


@auto_router
class Participant(DSLModel):
    name: str = Field(..., description="Name of the participant.")
    role: str = Field(..., description="Role of the participant.")


import uvicorn
import threading
from dslmodel import init_lm, init_instant, init_text


def main():
    """Main function to initialize the app and start the server."""
    # Initialize the necessary DSL model components
    init_instant()

    # Define a function to run the FastAPI app
    def run_app():
        uvicorn.run(app, host="0.0.0.0", port=8000)

    # Start the FastAPI server in a separate thread
    thread = threading.Thread(target=run_app, daemon=True)
    thread.start()

    # Keep the main thread alive to prevent immediate exit
    print("Server is running... Press Ctrl+C to exit.")
    try:
        thread.join()  # Wait for the server thread to finish
    except KeyboardInterrupt:
        print("Shutting down the server...")


if __name__ == '__main__':
    main()
