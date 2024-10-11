from pydantic import Field

from dslmodel import DSLModel


class FieldTemplateSpecificationModel(DSLModel):
    field_name: str = Field(
        ...,
        description="The name of the field in the model. No prefixes, suffixes, or abbreviations.",
    )
    field_type: str = Field(
        "str",
        description="The data type of the field, e.g., 'str', 'int', 'EmailStr', or 'datetime'. No dict or classes.",
    )
    default_value: str | int | None = Field(
        "None",
        description="The default value for the field if not provided.",
    )
    description: str = Field(
        ...,
        description="A detailed description of the field's purpose and usage. (5 characters min)",
        min_length=5,
    )


class ConfigTemplateSpecificationModel(DSLModel):
    title: str = Field(
        ...,
        description="The title for the DSLModel configuration.",
    )
    description: str = Field(
        ...,
        description="A detailed description of the DSLModel configuration's purpose and usage.",
    )
    allow_population_by_field_name: bool = Field(
        True,
        description="Whether to allow populating a model using field names.",
    )
    underscore_attrs_are_private: bool = Field(
        False,
        description="Whether to treat underscore-prefixed attributes as private (no validation).",
    )
    alias_generator: str = Field(
        ...,
        description="The alias generator to use for field aliasing.",
    )


class ValidatorTemplateSpecificationModel(DSLModel):
    validator_name: str = Field(
        ...,
        title="Validator Name",
        description="The name of the validator.",
    )
    description: str = Field(
        ...,
        title="Description",
        description="A detailed description of the validator's purpose and usage.",
    )
    parameters: list[str] = Field(
        [],
        title="Parameters",
        description="A list of parameter names accepted by the validator.",
    )


class DSLModelClassTemplateSpecificationModel(DSLModel):
    class_name: str = Field(
        ...,
        description="The class name of the DSLModel model.",
    )
    description: str = Field(
        ...,
        description="A detailed description of the DSLModel's purpose and usage.",
    )


class UserModel(DSLModel):
    """A detailed description of the UserModel's purpose and usage."""

    username: str = Field(
        default=None, description="A username is a unique identifier for a user in a system."
    )
    email: str = Field(default=None, description="A field to store email addresses.")
