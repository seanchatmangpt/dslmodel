import os
from pathlib import Path
from typing import Any

from jinja2 import FileSystemLoader

from dslmodel.template.environment import CustomEnvironment
from dslmodel.template.environment import CustomNativeEnvironment


def render(tmpl_str_or_path: str | Path, to: str = "", **kwargs) -> str:
    """Render a template from a string or a file with the given keyword arguments."""
    file_loader = FileSystemLoader(".")

    environment = CustomEnvironment(loader=file_loader)

    # Check if tmpl_str_or_path is a path to a file
    if os.path.exists(tmpl_str_or_path) and Path(tmpl_str_or_path).is_file():
        with open(tmpl_str_or_path) as file:
            template_content = file.read()
    else:
        template_content = str(tmpl_str_or_path)

    template = environment.from_string(template_content)

    rendered = template.render(**kwargs)

    if to:
        to_ = environment.from_string(to)
        rendered_to = to_.render(**kwargs)

        # Check if a directory needs to be created. First check if there is a directory in the path
        # check for a / or \ in the path
        if "/" in rendered_to or "\\" in rendered_to:
            if not os.path.exists(os.path.dirname(rendered_to)):
                os.makedirs(os.path.dirname(rendered_to))

        with open(rendered_to, "w") as file:
            file.write(rendered)

    return rendered


def render_native(tmpl_str_or_path: str | Path, to: str = "", **kwargs) -> Any:
    """
    Renders a template from a string or a file, returning the native Python type
    (e.g., str, int, list, dict, etc.) based on the template content.

    :param tmpl_str_or_path: Template string or path to a template file.
    :param to: Optional path to write the rendered output to.
    :param kwargs: Additional keyword arguments to pass into the template.
    :return: The rendered template as a native Python type (str, int, list, dict, etc.).
    """
    file_loader = FileSystemLoader(".")
    environment = CustomNativeEnvironment(loader=file_loader)

    # Check if tmpl_str_or_path is a file path
    if os.path.exists(tmpl_str_or_path) and Path(tmpl_str_or_path).is_file():
        with open(tmpl_str_or_path, 'r') as file:
            template_content = file.read()
    else:
        template_content = str(tmpl_str_or_path)

    # Render the template content as a native Python type
    template = environment.from_string(template_content)
    rendered = template.render(**kwargs)

    # If 'to' is specified, write the rendered output to a file
    if to:
        to_path = environment.from_string(to).render(**kwargs)

        # Ensure directories exist for the output path
        output_dir = os.path.dirname(to_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write the rendered content to the specified file
        with open(to_path, "w") as file:
            file.write(str(rendered))  # Ensure it's written as a string

    return rendered


def main():
    """Main function"""
    # Example Usage:
    # You can render any type of Python object based on your template content.
    template_str = "{{ fake_random_int(min=10, max=100) }}"
    native_rendered_value = render_native(template_str)
    print(type(native_rendered_value), native_rendered_value)  # Example output: <class 'int'> 42

    # Rendering a list template
    template_list = "['{{ fake_name() }}', '{{ fake_name() }}', '{{ fake_name() }}']"
    native_rendered_list = render_native(template_list)
    print(native_rendered_list)

if __name__ == '__main__':
    main()
