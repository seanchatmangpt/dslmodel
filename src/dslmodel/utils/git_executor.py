import subprocess
from dslmodel.utils import git_auto
import yaml
import pathlib

# Load registry to build mapping
registry_path = pathlib.Path(__file__).parent.parent.parent.parent / "etc" / "git_registry.yaml"
REG = yaml.safe_load(registry_path.read_text())

# Build a mapping {op_name: wrapper_function}
def _wrap_map():
    m = {}
    for op in REG:
        fn = lambda **kw: None               # placeholder
        fn.__name__ = op
        m[op] = git_auto.git_wrap(op)(fn)    # decorate
    return m

WRAPPERS = _wrap_map()

def run_plan(plan: list):
    """
    plan: list of {"op": str, "args": dict}
    Executes in order, returns list of subprocess.CompletedProcess.
    """
    results = []
    for step in plan:
        op, args = step["op"], step.get("args", {})
        if op not in WRAPPERS:
            raise ValueError(f"Unsupported op {op}")
        results.append(WRAPPERS[op](**args))
    return results