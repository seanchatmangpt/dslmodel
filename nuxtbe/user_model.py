
from pydantic import BaseModel, ValidationError
from typing import List

class User(BaseModel):
    name: str
    age: int
    hobbies: List[str]

    def greet(self):
        return f"Hello, {self.name}!"
