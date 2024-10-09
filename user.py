from pydantic import Field, validator, root_validator, EmailStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel

class User(DSLModel):
    """A DSLModel representing a user with various attributes."""
    id: int = Field(default=None, description="Unique identifier for the field")
    username: str = Field(default=None, description="A unique identifier for the user.")
    first_name: str = Field(default=None, description="The first name of the individual.")
    last_name: str = Field(default=None, description="The surname of a person.")
    email: EmailStr = Field(default=None, description="The email address of the user.")
    password: str = Field(default=None, description="A secure password for authentication purposes.")
    phone: str = Field(default=None, description="A phone number for contact purposes")
    user_status: str = Field(default=active, description="The current status of the user.")

    