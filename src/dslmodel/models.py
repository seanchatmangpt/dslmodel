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

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        populate_by_name=True
    )
