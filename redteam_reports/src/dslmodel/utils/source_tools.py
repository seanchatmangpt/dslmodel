import inspect
from enum import Enum
from textwrap import dedent
from typing import Any, Literal, Optional, Union, get_args, get_origin


def collect_class_sources(cls: Any, collected_sources: dict[str, str]) -> None:
    """
    Recursively collect source code for the given class and all related classes
    (based on fields' type annotations) including Enums. This implementation is generic
    and doesn't depend on DSLModel.
    """
    if cls.__name__ in collected_sources:
        return  # Skip already processed classes

    try:
        # Attempt to get the source code of the class
        source_code = inspect.getsource(cls)
    except (TypeError, OSError):
        # Fallback: use schema representation if source code is unavailable
        source_code = f"# Unable to retrieve source for {cls.__name__}\n{cls.__name__} schema unavailable."

    collected_sources[cls.__name__] = source_code

    # Process fields for classes with attributes like `model_fields` or `__fields__`
    fields = getattr(cls, "model_fields", None) or getattr(cls, "__fields__", None)
    if not fields:
        return  # Skip non-Pydantic-like classes

    for field in fields.values():
        field_type = field.annotation
        handle_complex_type(field_type, collected_sources)


def handle_complex_type(field_type: Any, collected_sources: dict[str, str]) -> None:
    """
    Handles complex types like List, Union, Optional, Literal, Enum, etc., and recursively collects
    source code for any referenced classes or Enums.
    """
    origin_type = get_origin(field_type)  # Get the origin type, e.g., list, Union
    args = get_args(field_type)  # Get inner types, e.g., for Union or List

    if origin_type in {list, Union, Optional}:  # Handle iterable and optional types
        for arg in args:
            if arg is not type(None):  # Skip NoneType
                process_field_type(arg, collected_sources)
    elif origin_type is Literal:  # Literal types don't require further processing
        pass
    else:
        # Directly process field types
        process_field_type(field_type, collected_sources)


def process_field_type(field_type: Any, collected_sources: dict[str, str]) -> None:
    """
    Processes a field type, collecting its source if it's a class or Enum.
    """
    if hasattr(field_type, "__bases__"):
        # Check if the field is an Enum
        if issubclass(field_type, Enum):
            collect_enum_sources(field_type, collected_sources)
        else:
            # Collect sources for the referenced class
            collect_class_sources(field_type, collected_sources)


def collect_enum_sources(enum_cls: Enum, collected_sources: dict[str, str]) -> None:
    """
    Collects the source code for an Enum class.
    """
    if enum_cls.__name__ in collected_sources:
        return  # Skip already processed Enums

    try:
        source_code = inspect.getsource(enum_cls)
    except (TypeError, OSError):
        source_code = f"# Unable to retrieve source for Enum {enum_cls.__name__}\n"

    collected_sources[enum_cls.__name__] = source_code


def collect_all_sources_as_string(cls: Any) -> str:
    """
    Collects the source code for the class and all related classes or Enums,
    and returns them as a single string.
    """
    collected_sources = {}
    collect_class_sources(cls, collected_sources)
    return dedent("\n\n".join(collected_sources.values()))


# Example Usage
if __name__ == "__main__":
    # Example Enum and Classes
    class ExampleEnum(Enum):
        OPTION_A = "A"
        OPTION_B = "B"


    class SubModel:
        value: str


    class ExampleModel:
        name: str
        options: Optional[list[ExampleEnum]]
        sub_model: SubModel


    # Collect and print all related sources
    result = collect_all_sources_as_string(ExampleModel)
    print(result)
