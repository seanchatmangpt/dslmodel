"""YAML-driven git command automation"""

import subprocess
import yaml
import pathlib
from functools import wraps
from dslmodel.utils.span import span

# Load git registry
registry_path = pathlib.Path(__file__).parent.parent.parent.parent / "etc" / "git_registry.yaml"
with open(registry_path) as f:
    GIT_REGISTRY = yaml.safe_load(f)

def git_wrap(cmd_name):
    """Decorator that wraps git commands with OTEL spans"""
    def decorator(func):
        @wraps(func)
        def wrapper(**kwargs):
            cmd_spec = GIT_REGISTRY[cmd_name]
            cmd = cmd_spec["cmd"].format(**kwargs)
            
            # Handle cwd_arg
            cwd = kwargs.get(cmd_spec.get("cwd_arg")) if cmd_spec.get("cwd_arg") else None
            
            with span(cmd_spec["span"]) as s:
                s.set_attribute("git.command", cmd)
                if cwd:
                    s.set_attribute("git.cwd", str(cwd))
                
                result = subprocess.run(cmd.split(), cwd=cwd, capture_output=True, text=True)
                
                s.set_attribute("git.exit_code", result.returncode)
                if result.returncode != 0:
                    s.set_attribute("git.error", result.stderr)
                
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
                return result.stdout
        return wrapper
    return decorator