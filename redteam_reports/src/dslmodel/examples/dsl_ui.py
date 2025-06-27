from enum import Enum
from typing import List
from pydantic import BaseModel
from dslmodel import DSLModel, init_instant


# Define UI types
class UIType(str, Enum):
    div = "div"
    button = "button"
    header = "header"
    section = "section"
    field = "field"
    form = "form"


# Define attributes for UI elements
class Attribute(BaseModel):
    name: str
    value: str


# Define the UI element model
class UI(DSLModel):
    type: UIType
    label: str
    children: List["UI"]
    attributes: List[Attribute]


UI.model_rebuild()  # Required to enable recursive types


# Define the response model
class Response(BaseModel):
    ui: UI


# Main function to generate UI using DSLModel.from_prompt
def main():
    init_instant()
    ui = UI.from_prompt(
        prompt=(
            '[{"role": "system", "content": "You are a UI generator AI. Convert the user input into a UI."}, '
            '{"role": "user", "content": "Make a User Profile Form with fields: Name, Email, and Phone Number. Placeholders: Enter your name, Enter your email, Enter your phone number."}]'
        )
    )
    print(ui)


if __name__ == "__main__":
    main()
