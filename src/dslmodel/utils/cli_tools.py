from importlib import import_module
from pathlib import Path

import os


def source_dir(path):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), path)


def load_commands(app, cmd_dir):
    cmd_dir = Path(cmd_dir) if isinstance(cmd_dir, str) else cmd_dir

    try:
        package_path = cmd_dir.resolve()
        module_base = ".".join(package_path.parts[-2:])
    except IndexError:
        raise ValueError(f"The path '{cmd_dir}' does not appear to be within an importable package structure.")

    for filepath in cmd_dir.glob("*_cmd.py"):
        module_name = f"{module_base}.{filepath.stem}"
        module = import_module(module_name)
        if hasattr(module, "app"):
            app.add_typer(module.app, name=filepath.stem[:-4], help=module.__doc__)
