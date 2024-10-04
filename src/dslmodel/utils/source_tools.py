import inspect
from typing import Any, Set, get_args, get_origin, List, Union, Literal, Optional
from enum import Enum


def collect_class_sources(cls: Any, collected_sources: Set[str]) -> None:
    """
    Recursively collect source code for the given class and all related classes
    (based on fields' type annotations) that inherit from DSLModel, including Enums.
    """
    # Skip if we've already processed this class by its name
    if cls.__name__ in collected_sources:
        return

    # Collect the source code for the class itself
    try:
        source_code = inspect.getsource(cls)
        collected_sources.add(source_code)  # Add the source code as a string, not the class object
    except (TypeError, OSError) as e:
        source_code = str(cls.schema())
        collected_sources.add(source_code)  # Add the source code as a string, not the class object

    # Now process the fields of the class
    if hasattr(cls, 'model_fields'):  # Pydantic v2
        fields = cls.model_fields
    elif hasattr(cls, '__fields__'):  # Pydantic v1
        fields = cls.__fields__
    else:
        print(f"{cls.__name__} does not appear to be a Pydantic model.")
        return

    # Recursively check if any field annotations are also DSLModel classes
    for field_name, field in fields.items():
        field_type = field.annotation

        # Handle cases where the field is a complex type (List, Optional, Union, Enum, etc.)
        handle_complex_type(field_type, collected_sources)


def handle_complex_type(field_type: Any, collected_sources: Set[str]) -> None:
    """
    Handles complex types like List, Union, Optional, Literal, Enum, etc., and recursively collects
    source code for any referenced classes that inherit from DSLModel or are Enums.
    """
    origin_type = get_origin(field_type)  # Get the origin (e.g., List, Union, Literal)
    args = get_args(field_type)  # Get the inner types (e.g., for Union or List)

    # If it's a List, Union, or Optional, process its inner types recursively
    if origin_type in (list, List, Union, Optional):
        for arg in args:
            if arg is not type(None):  # Skip 'NoneType' from Optional or Union
                if hasattr(arg, '__bases__'):
                    from dslmodel import DSLModel
                    if issubclass(arg, DSLModel):
                        collect_class_sources(arg, collected_sources)
                    elif issubclass(arg, Enum):
                        collect_enum_sources(arg, collected_sources)

    # If it's a Literal, we don't need to process further
    elif origin_type is Literal:
        pass

    # If it's directly a DSLModel or Enum, collect its source
    elif hasattr(field_type, '__bases__'):
        from dslmodel import DSLModel
        if issubclass(field_type, DSLModel):
            collect_class_sources(field_type, collected_sources)
        elif issubclass(field_type, Enum):
            collect_enum_sources(field_type, collected_sources)


def collect_enum_sources(enum_cls: Enum, collected_sources: Set[str]) -> None:
    """
    Collects the source code for an Enum class.
    """
    # Skip if we've already processed this enum by its name
    if enum_cls.__name__ in collected_sources:
        return

    try:
        source_code = inspect.getsource(enum_cls)
        collected_sources.add(source_code)
    except (TypeError, OSError) as e:
        print(f"Unable to retrieve source for {enum_cls.__name__}: {str(e)}")


def collect_all_sources_as_string(cls: Any) -> str:
    """
    Collects the source code for the class and all related DSLModel classes, including Enums,
    and returns them as a single string.
    """
    collected_sources = set()

    # Collect sources starting from the given class
    collect_class_sources(cls, collected_sources)

    # Join all collected source codes into a single string
    return "\n\n".join(collected_sources)


def main():
    """Main function"""
    # from dslmodel.utils.dspy_tools import init_lm
    # init_lm()

    # Now, let's collect the sources from the GherkinDocument class:
    # all_sources_string = collect_all_sources_as_string(create_dynamic_dslmodel_class())

    # Print the result
    # print(all_sources_string)


if __name__ == '__main__':
    main()
