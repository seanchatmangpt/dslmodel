from typing import Type, TypeVar

from pydantic import ConfigDict, BaseModel

from dslmodel.mixins import FileHandlerDSLMixin, JinjaDSLMixin, DSPyDSLMixin, ToFromDSLMixin


T = TypeVar("T", bound="DSLModel")


class DSLModel(BaseModel, FileHandlerDSLMixin, JinjaDSLMixin, DSPyDSLMixin, ToFromDSLMixin):
    """
    A base model class that provides core model functionalities and delegates
    file handling to the FileHandlerDSLMixin.
    """
    def __init__(self, **data):
        # Render any default template values using Jinja2 before instantiation
        data = self.render_defaults(data)
        super().__init__(**data)

    @classmethod
    def field_names(cls) -> list[str]:
        """
        Returns a list of field names defined in the DSLModel.

        Returns:
        - A list of strings representing the names of the fields.
        """
        names = list(cls.model_fields.keys())
        # Remove the trailing underscore from each field name in the names list
        names = [name[:-1] if name.endswith('_') else name for name in names]
        return names

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        populate_by_name=True
    )
