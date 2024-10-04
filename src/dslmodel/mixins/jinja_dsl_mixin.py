from pydantic_core import PydanticUndefined

from dslmodel.template import render_native


class JinjaDSLMixin:

    model_fields = None

    @classmethod
    def render_defaults(cls, data: dict) -> dict:
        """
        Renders default values that are defined as Jinja2 templates.
        """
        for field_name, field_value in cls.model_fields.items():
            if field_name in data or field_value.default is None or field_value.default is PydanticUndefined:
                continue
            try:
                if field_value.default and "{{" in field_value.default:
                    # Render the template if it contains a Jinja2 expression
                    rendered_value = render_native(field_value.default)
                    # Only set the value if not already provided by user input
                    if field_name not in data:
                        data[field_name] = rendered_value
            except Exception as e:
                pass

        return data