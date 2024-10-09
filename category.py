from pydantic import Field, validator, root_validator, EmailStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel

class Category(DSLModel):
    """I need a DSLModel called Category with the following fields: id: integer = Field(..., description=""), name: string = Field(..., description="")"""
    id: int = Field(default=None, description="Unique identifier for the field")
    name: str = Field(default=None, description="A field to store the name of an entity.")

    