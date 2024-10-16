import pytest
from pydantic import Field, BaseModel
from dslmodel.mixins.jinja_dsl_mixin import JinjaDSLMixin


# Sample model class that inherits from JinjaDSLMixin
class MyModel(BaseModel, JinjaDSLMixin):
    field_with_template: str = Field(default="{{ 5 + 5 }}")


# Test case 1: Field with Jinja2 template should render
def test_render_template_default():
    data = {}
    result = MyModel.render_defaults(data)

    # The field_with_template should be rendered
    assert result["field_with_template"] == 10
