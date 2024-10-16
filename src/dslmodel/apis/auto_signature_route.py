from fastapi import FastAPI, APIRouter, HTTPException, Body
from typing import Type, Dict, Any, Callable
import dspy

from dslmodel import init_instant


app = FastAPI()


def auto_signature_route(
    predictor_class: Callable = dspy.Predict
):
    """
    Decorator factory to generate a FastAPI route for a given dspy.Signature class.
    Allows specifying the predictor class, defaulting to dspy.Predict.
    """
    def decorator(signature_class: Type[dspy.Signature]):
        router = APIRouter()
        signature_name = signature_class.__name__.lower()

        # Create the provided predictor (defaulting to dspy.Predict)
        predictor = predictor_class(signature_class)

        @router.post(f"/{signature_name}/")
        async def signature_route(data: Dict[str, Any] = Body(...)):
            try:
                # Initialize dspy environment
                init_instant()

                # Use the predictor to run the signature with the provided inputs
                result = predictor(**data)

                # Convert the result to a dictionary if needed
                if hasattr(result, "items"):
                    result_dict = dict(result.items())
                else:
                    result_dict = result  # Handle already dict-like responses

                # Return the result as a dictionary
                return result_dict
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        # Register the router with the FastAPI app
        app.include_router(router)

        # Return the original class to maintain decorator behavior
        return signature_class

    return decorator


@auto_signature_route(predictor_class=dspy.ChainOfThought)
class GeneratePureJSX(dspy.Signature):
    """
    Generate clean JSX code based on the provided context and requirements,
    ensuring compatibility with react-live environments.
    """
    context: str = dspy.InputField(desc="A brief description of the desired component and its functionality.")
    requirements: str = dspy.InputField(desc="Specific requirements or features the JSX should include.")

    pure_jsx: str = dspy.OutputField(desc="Clean JSX code without {}, ready for react-live.")


# Start the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
