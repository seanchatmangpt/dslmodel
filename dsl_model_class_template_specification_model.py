from pydantic import Field, validator, root_validator, EmailStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel


class DSLModelClassTemplateSpecificationModel(DSLModel):
    """A model for specifying the template of a DSLModel class, including its class name and description."""
    problem: str = Field(default=None, alias: "Problem", title="", description="A field to describe a problem or issue.")
    hypothesis: str = Field(default=None, alias: "Hypothesis", title="", description="A useful description for the Hypothesis field.")
    evidence: str = Field(default=None, alias: "Evidence", title="", description="A description of the evidence provided to support a claim or argument.")
    conclusion: str = Field(default=None, alias: "Conclusion", title="", description="A conclusion or summary of the main points.")

