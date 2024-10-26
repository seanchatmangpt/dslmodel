# models/code_block_model.py
from dslmodel import DSLModel
from pydantic import Field
from typing import Optional


class CodeBlock(DSLModel):
    """Represents a code block during an interview."""
    language: str = Field("markdown", description="Programming language of the code block.")
    code: str = Field(..., description="The source code content to be displayed. At least 3 lines of code.")
    filename: Optional[str] = Field("markdown", description="Optional filename for the code block.")
