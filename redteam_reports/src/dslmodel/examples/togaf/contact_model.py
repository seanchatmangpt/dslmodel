from pydantic import Field

from dslmodel import DSLModel


class ContactModel(DSLModel):
    """Verbose contact model from the friend of a friend ontology with 20 fields"""

    business_layer: str = Field(
        default=None, title="", description="A layer that handles business logic and operations."
    )
    data_layer: str = Field(
        default=None, title="", description="A layer of data that stores information."
    )
    application_layer: str = Field(
        default=None, title="", description="A field used to specify the application layer."
    )
    technology_layer: str = Field(
        default=None, title="", description="The technology layer used in the system."
    )
    security_layer: str = Field(
        default=None,
        title="",
        description="A security layer to ensure data integrity and security.",
    )
    core_capabilities: str = Field(
        default=None,
        title="",
        description="Core capabilities of the system, including features and functionalities.",
    )
    governance: str = Field(
        default=None, title="", description="A description of the governance field."
    )
    compliance: str = Field(
        default=None, title="", description="A description of the compliance field."
    )
    modularity: str = Field(
        default=None,
        title="",
        description="A measure of how easily a system can be modified or extended without affecting other parts of the system.",
    )
    loose_coupling: str = Field(
        default=None,
        title="",
        description="A concept in software design that refers to the independence of components or modules from each other, making it easier to modify or replace them without affecting other parts of the system.",
    )
    replaceability: str = Field(
        default=None, title="", description="The ability to replace the field with a new value."
    )
