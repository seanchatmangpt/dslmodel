# openapi_tool_mixin.py

from fastapi import FastAPI, APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Type, Any, Dict
from .tool_mixin import ToolMixin, Tool
import inspect


class OpenAPIToolMixin(ToolMixin):
    """
    Inherits from ToolMixin and registers tool methods as FastAPI routes.
    """

    def __init__(self):
        super().__init__()

    def register_routes(self, app: FastAPI):
        """
        Registers tool methods as FastAPI routes, ensuring that request and response models
        are correctly associated to include them in the OpenAPI schema.
        """
        router = APIRouter()

        for tool in self.tools:
            route_path = f"/{tool.name}"
            method = tool.method
            sig = inspect.signature(method)

            # Extract 'input' type annotation
            input_model = None
            for name, param in sig.parameters.items():
                if name == 'input':
                    input_model = param.annotation
                    break

            # Determine output model
            output_model = sig.return_annotation if sig.return_annotation != inspect.Signature.empty else None

            # Define the route handler using a helper function to avoid closure issues
            def make_tool_endpoint(tool: Tool, input_model: Type[BaseModel], output_model: Type[Any]):
                async def tool_endpoint(body: input_model = Body(...), tool=tool, input_model=input_model,
                                        output_model=output_model):
                    try:
                        result = tool.method(body)
                        if isinstance(result, BaseModel):
                            return result
                        return {"result": result}
                    except Exception as e:
                        raise HTTPException(status_code=400, detail=str(e))

                tool_endpoint.__name__ = f"{tool.name}_endpoint"
                return tool_endpoint

            # Create the endpoint with default arguments to capture the current tool and models
            endpoint = make_tool_endpoint(tool, input_model, output_model)

            # Add the route to the router
            router.add_api_route(
                route_path,
                endpoint,
                methods=["POST"],
                response_model=output_model if output_model and inspect.isclass(output_model) and issubclass(
                    output_model, BaseModel) else None,
                summary=tool.description,
                tags=["tools"],
            )

        # Register the router with the app
        app.include_router(router)
