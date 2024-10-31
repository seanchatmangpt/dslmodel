from pydantic import BaseModel, Field
from types import FunctionType, CodeType
from typing import Type, Dict


# Step 1: Define the Pydantic model
class ExampleModel(BaseModel):
    name: str = Field(..., description="The name of the person.")
    age: int = Field(25, description="The age of the person.")
    active: bool = Field(True, description="Is the user active?")


# Step 2: Function to map Python types to Zod types
def get_zod_type(python_type) -> str:
    """
    Maps Python types to Zod types.
    """
    type_mapping = {
        str: 'string',
        int: 'number',
        float: 'number',
        bool: 'boolean',
        list: 'array',
        dict: 'object',
    }
    return type_mapping.get(python_type, 'any')


# Step 3: Extract field definitions from the Pydantic model
def extract_field_definitions(model: Type[BaseModel]) -> Dict[str, Dict]:
    fields = {}
    for field_name, field in model.__fields__.items():
        # Determine field type and default
        field_type = get_zod_type(field.outer_type_)
        default = field.default if field.default is not None else "undefined"
        optional = field.required is False

        fields[field_name] = {
            "type": field_type,
            "default": default,
            "optional": optional,
        }
    return fields


# Step 4: Build the Zod schema function dynamically using types.FunctionType
def build_zod_schema_function(model: Type[BaseModel]) -> FunctionType:
    """
    Builds a function to generate a Zod schema dynamically using FunctionType.
    """
    fields = extract_field_definitions(model)

    # Define a placeholder function body to be used as a code object
    def zod_schema_func():
        # Placeholder to match the function signature for CodeType
        pass

    # Convert the placeholder function's code object to a new code object
    code = zod_schema_func.__code__

    # Prepare the Zod schema generation logic as a string template
    schema_lines = [f"z.object({{"]
    for field_name, field_info in fields.items():
        field_line = f"{field_name}: z.{field_info['type']}()"
        if field_info["optional"]:
            field_line += ".optional()"
        if field_info["default"] != "undefined":
            field_line += f".default({field_info['default']!r})"
        schema_lines.append(f"    {field_line},")
    schema_lines.append("})")

    # Assemble the full schema generation code as a string
    schema_code = "\n".join(schema_lines)

    # Update the function's bytecode to return the generated Zod schema
    new_code = CodeType(
        code.co_argcount,  # Number of positional arguments
        code.co_posonlyargcount,  # Number of positional-only arguments
        code.co_kwonlyargcount,  # Number of keyword-only arguments
        code.co_nlocals,  # Number of local variables
        code.co_stacksize,  # Stack size
        code.co_flags,  # Flags
        compile(schema_code, "<string>", "exec").co_code,  # Compiled schema code
        code.co_consts,  # Constants
        code.co_names,  # Names
        code.co_varnames,  # Variable names
        code.co_filename,  # Filename
        model.__name__ + "Schema",  # Function name
        code.co_firstlineno,  # First line number
        code.co_lnotab,  # Line number table
        code.co_freevars,  # Free variables
        code.co_cellvars  # Cell variables
    )

    # Generate the dynamic function with the new code object
    zod_schema_function = FunctionType(new_code, globals(), model.__name__ + "Schema")

    return zod_schema_function


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()
    # Step 5: Example usage
    # Define a schema function based on the ExampleModel
    zod_schema_function = build_zod_schema_function(ExampleModel)
    print(zod_schema_function())


if __name__ == '__main__':
    main()
