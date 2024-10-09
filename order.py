from pydantic import Field, validator, root_validator, EmailStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel

class Order(DSLModel):
    """A DSLModel representing an order."""
    id: int = Field(default=None, description="Unique identifier for the field")
    pet_id: str = Field(default=None, description="A unique identifier for the pet.")
    quantity: int = Field(default=0, description="The quantity of items.")
    ship_date: datetime = Field(default=None, description="The date when the item is expected to be shipped.")
    status: str = Field(default=None, description="Indicates the current status of the entity.")
    complete: bool = Field(default=False, description="Indicates whether the field is complete or not.")

    