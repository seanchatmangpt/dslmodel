import json, sys
from dslmodel.dspy_programs.git_plan import GitPlanner
from dslmodel.utils.git_executor import run_plan
from dslmodel.utils.span import span
from dslmodel.generated.python.git_hook_run import git_hook_run_span  # optional audit

@span("git_hook_run")              # re-use hook span to audit the whole script
def main(user_goal_file: str):
    goal = open(user_goal_file).read().strip()
    plan  = GitPlanner()(user_goal=goal)   # LLM → plan list
    # Safety sanity: max 10 ops
    if len(plan) > 10:
        raise RuntimeError("Plan too long")
    result = run_plan(plan)                # execute via git_auto
    print(json.dumps({"goal": goal, "plan": plan,
                      "return_codes": [p.returncode for p in result]}))

if __name__ == "__main__":
    main(sys.argv[1])