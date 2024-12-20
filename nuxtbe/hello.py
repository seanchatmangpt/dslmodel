from pydantic import BaseModel, ValidationError
from typing import Optional

from dslmodel import DSLModel


# Define the Pydantic model with two fields
class GreetingModel(DSLModel):
  name: str
  greeting: Optional[str] = "Hello"


# Function that uses the GreetingModel with explicit conversion
def greet(model: dict) -> str:
  try:
    # Convert the incoming dict to a GreetingModel instance
    greeting_model = GreetingModel(**model)
    return f"{greeting_model.greeting}, {greeting_model.name}!"
  except ValidationError as e:
    # Handle validation errors and return them as strings
    return f"Validation Error: {e}"


def main():
  """Main function"""
  from dslmodel import init_lm, init_instant, init_text
  init_text()

  GreetingModel.from_prompt("David Thomas")


if __name__ == '__main__':
  main()
