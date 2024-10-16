from pydantic import Field

from dslmodel import DSLModel


class Address(DSLModel):
    """A DSLModel for representing addresses."""

    street: str = Field(default=None, description="The street address of a location.")
    city: str = Field(default=None, description="The city where the user resides.")
    state: str = Field(default=None, description="The current state of the system or process.")
    zip: str = Field(default=None, description="A zip code for postal address purposes.")
