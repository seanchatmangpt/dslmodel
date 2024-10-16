from pydantic import Field

from dslmodel import DSLModel


class Customer(DSLModel):
    """A model representing a customer."""

    id: int = Field(default=None, description="Unique identifier for the field")
    username: str = Field(default=None, description="A unique identifier for the user.")
    address: str = Field(default=None, description="The physical address of the location.")
