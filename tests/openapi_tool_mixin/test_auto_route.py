# test_auto_route.py

"""
This test file demonstrates how to create a decorator that, when applied to any class,
automatically generates FastAPI routes for all of its methods. Each method becomes an API endpoint.

It includes pytest test functions to validate the behavior of the endpoints,
ensuring that the auto_route decorator works as intended.
"""

import inspect
from functools import wraps
from typing import Any, Callable, get_type_hints

from fastapi import FastAPI, APIRouter, HTTPException, Body
from fastapi.testclient import TestClient
from pydantic import BaseModel
import pytest

# Initialize the FastAPI application
app = FastAPI()

def auto_route(cls):
    """
    Decorator to automatically register all methods of a class as FastAPI routes.
    """
    # Create an APIRouter instance for grouping routes
    router = APIRouter()

    # Get all methods of the class
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith('_'):
            # Skip private methods and special methods
            continue

        # Extract the method signature
        sig = inspect.signature(method)

        # Extract type hints for parameters and return type
        type_hints = get_type_hints(method)

        # Build Pydantic models for request body and response if necessary
        InputModel = None
        OutputModel = None

        # Check if the method has parameters other than 'self'
        if len(sig.parameters) > 1:
            # Exclude 'self' parameter
            params = {k: v for k, v in sig.parameters.items() if k != 'self'}

            # Build a Pydantic model dynamically for input parameters
            InputModel = create_pydantic_model(f"{cls.__name__}_{name}_InputModel", params, type_hints)

        # Check if the method has a return type annotation
        if 'return' in type_hints:
            return_type = type_hints['return']

            # If the return type is not a simple type, create an OutputModel
            if not is_simple_type(return_type):
                OutputModel = return_type
            else:
                OutputModel = None  # Let FastAPI handle simple return types
        else:
            OutputModel = None

        # Define the route handler function
        route_function = make_route_function(cls, method, InputModel, OutputModel)

        # Determine the HTTP method (use POST if there's an input model, else GET)
        http_method = ['POST'] if InputModel else ['GET']

        # Add the route to the router
        router.add_api_route(
            f"/{name}",
            route_function,
            methods=http_method,
            response_model=OutputModel,
            summary=method.__doc__ or f"{name} method",
        )

    # Include the router in the FastAPI app
    app.include_router(router)

    return cls

def create_pydantic_model(model_name: str, params: dict, type_hints: dict):
    """
    Dynamically create a Pydantic model for input parameters.
    """
    annotations = {}
    defaults = {}
    for param_name, param in params.items():
        annotation = type_hints.get(param_name, Any)
        default = param.default if param.default is not inspect.Parameter.empty else ...
        annotations[param_name] = annotation
        defaults[param_name] = default

    return type(
        model_name,
        (BaseModel,),
        {'__annotations__': annotations, **defaults}
    )

def make_route_function(cls, method, InputModel, OutputModel):
    """
    Create a route function that wraps the class method.
    """
    async def route_function(*, body: InputModel = Body(...) if InputModel else None):
        try:
            # Create an instance of the class
            instance = cls()

            # Prepare arguments for the method
            if InputModel:
                kwargs = body.dict()
            else:
                kwargs = {}

            # Call the method
            result = method(instance, **kwargs)

            return result
        except Exception as e:
            # Return an HTTP 400 error with the exception message
            raise HTTPException(status_code=400, detail=str(e))

    return route_function

def is_simple_type(annotation):
    """
    Check if the annotation represents a simple type (str, int, float, bool).
    """
    return annotation in {str, int, float, bool}

# Example usage

@auto_route
class MyAPIClass:
    """
    Example class whose methods will be converted into API endpoints.
    """

    def greet(self, name: str) -> str:
        """Greet the user by name."""
        return f"Hello, {name}!"

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def echo(self, message: str = "Default message") -> dict:
        """Echo the provided message."""
        return {"message": message}

    def status(self) -> dict:
        """Get the status of the API."""
        return {"status": "Running"}

    def divide(self, numerator: float, denominator: float) -> float:
        """Divide two numbers."""
        if denominator == 0:
            raise ValueError("Denominator cannot be zero.")
        return numerator / denominator

# Create a TestClient instance for testing
client = TestClient(app)

# Pytest test functions

def test_status_endpoint():
    """
    Test the /status endpoint.
    """
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "Running"}

def test_greet_endpoint():
    """
    Test the /greet endpoint with a name parameter using POST.
    """
    # Send the name in the body as JSON
    response = client.post("/greet", json={"name": "Alice"})
    assert response.status_code == 200
    assert response.json() == "Hello, Alice!"


def test_add_endpoint():
    """
    Test the /add endpoint with valid input.
    """
    response = client.post("/add", json={"a": 5, "b": 7})
    assert response.status_code == 200
    assert response.json() == 12

def test_add_endpoint_invalid_input():
    """
    Test the /add endpoint with invalid input (missing parameter).
    """
    response = client.post("/add", json={"a": 5})
    assert response.status_code == 422  # Unprocessable Entity due to validation error

def test_echo_endpoint_with_message():
    """
    Test the /echo endpoint with a custom message.
    """
    response = client.post("/echo", json={"message": "Hello World"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_echo_endpoint_default_message():
    """
    Test the /echo endpoint without providing a message (uses default).
    """
    response = client.post("/echo", json={})
    assert response.status_code == 200
    assert response.json() == {"message": "Default message"}

def test_divide_endpoint_valid():
    """
    Test the /divide endpoint with valid input.
    """
    response = client.post("/divide", json={"numerator": 10, "denominator": 2})
    assert response.status_code == 200
    assert response.json() == 5.0

def test_divide_endpoint_divide_by_zero():
    """
    Test the /divide endpoint with division by zero.
    """
    response = client.post("/divide", json={"numerator": 10, "denominator": 0})
    assert response.status_code == 400
    assert response.json() == {"detail": "Denominator cannot be zero."}

def test_openapi_schema():
    """
    Test that the OpenAPI schema includes all endpoints and models.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})
    assert "/status" in paths
    assert "/greet" in paths
    assert "/add" in paths
    assert "/echo" in paths
    assert "/divide" in paths

def test_invalid_endpoint():
    """
    Test accessing an invalid endpoint.
    """
    response = client.get("/nonexistent")
    assert response.status_code == 404

def test_method_not_allowed():
    """
    Test accessing an endpoint with an unsupported HTTP method.
    """
    response = client.put("/status")
    assert response.status_code == 405  # Method Not Allowed

# Run the FastAPI app for manual testing (optional)
if __name__ == "__main__":
    import uvicorn

    # Run the app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
