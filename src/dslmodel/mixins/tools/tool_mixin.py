import inspect
from collections.abc import Callable
from typing import Any

from pydantic import Field

from dslmodel import DSLModel


class Tool(DSLModel):
    name: str
    description: str | None = None
    method: Callable = None
    attributes: dict = Field(default={}, description="Attributes to pass to the function")
    source: str = None  # New attribute to store source code


class ChosenTool(DSLModel):
    """Name of the def to call. YOU MUST CHOOSE FROM THE DEFS PROVIDED"""

    reasoning: str = Field("", description="Reasoning for choosing the def")
    def_name: str = Field(..., description="Name of the def to call")
    kwargs: dict = Field(default={}, description="Keyword arguments to pass to the function")


def function_to_dict(func: Callable) -> dict:
    output = {
        "function__name__": func.__name__,
        "docstring": func.__doc__,
        "keyword_arguments": {},
    }

    sig = inspect.signature(func)
    params = sig.parameters

    for name, param in params.items():
        # Check if the parameter has a type annotation; if not, default to str
        param_type = param.annotation if param.annotation is not inspect.Parameter.empty else str
        output["keyword_arguments"][name] = str(param)  # Store the name of the type

    # Remove the return type annotation if present
    if "return" in output["keyword_arguments"]:
        del output["keyword_arguments"]["return"]

    return output


class ToolMixin:
    """Mixin for tools that allows the model to choose from a list of available tools."""

    tools: list[Tool] = []
    ignore_list: list[str] = []

    def __init__(self):
        if "call" not in self.ignore_list:
            self.ignore_list.append("call")

        # gather the source code of each def not starting with __
        for name, obj in inspect.getmembers(self):
            try:
                if (
                    inspect.ismethod(obj)
                    and not name.startswith("__")
                    and name not in self.ignore_list
                ):
                    # Get the source code of the method
                    source_code = inspect.getsource(obj)
                    def_dict = function_to_dict(obj)
                    self.tools.append(
                        Tool(
                            name=name,
                            description=obj.__doc__,
                            method=obj,
                            source=source_code,
                            attributes=def_dict["keyword_arguments"],
                        )
                    )
            except Exception as e:
                print(e)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.call(*args, **kwds)

    def call(self, prompt: str, verbose: bool = False, **kwargs: Any) -> Any:
        """Process a call from a prompt."""
        import textwrap

        template = textwrap.dedent("""Choose a def to use: {{ prompt }}
        Here are the available defs:

        {% for tool in tools %} Def Name:
        {{ tool.name }}
        Description: {{ tool.description }}
        Attributes: {{ tool.attributes }}
        {% endfor %}

        Choose a def to use: {{ prompt }}""")

        chose = ChosenTool.from_template(template, prompt=prompt, tools=self.tools, verbose=verbose)
        result = getattr(self, chose.def_name)(**chose.kwargs)
        return result


def main():
    """Main function"""
    from dslmodel import init_instant

    init_instant()


if __name__ == "__main__":
    main()
