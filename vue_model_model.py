from pydantic import Field, validator, root_validator, EmailStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel


class VueModel(DSLModel):
    """A Vue DSLModel for handling Vue-related data and operations."""
    id: str = Field(default=None, alias: "id", title="", description="A unique identifier for the record.")
    name: str = Field(default=None, alias: "name", title="", description="The full name of the person or entity.")
    email: EmailStr = Field(default=None, alias: "email", title="", description="The email address of the user.")
    password: str = Field(default=None, alias: "password", title="", description="A secret password for authentication purposes.")
    username: str = Field(default=None, alias: "username", title="", description="The username chosen by the user for identification purposes.")

