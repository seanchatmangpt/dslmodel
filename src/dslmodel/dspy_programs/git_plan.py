import dspy, yaml, pathlib, json
from dslmodel.runtime.weaver_prompt import WeaverPrompt

# Load valid command names from git_registry.yaml --------------------
registry_path = pathlib.Path(__file__).parent.parent.parent.parent / "etc" / "git_registry.yaml"
OPS = list(yaml.safe_load(registry_path.read_text()).keys())
OPS_EXAMPLE = ", ".join(OPS[:6]) + ", …"

class GitPlanner(dspy.Program):
    """
    Input  : user_goal (free-text)
    Output : JSON list  [ {"op": "<cmd>", "args": {...}}, ... ]
    """

    prompt = WeaverPrompt("git_planner")     # template below

    def forward(self, user_goal: str) -> list:
        raw = self.prompt.forward(goal=user_goal,
                                  commands=OPS_EXAMPLE,
                                  strict_cmds="|".join(OPS))
        return json.loads(raw)