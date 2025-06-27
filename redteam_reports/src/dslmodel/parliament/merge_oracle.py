import subprocess, json, pathlib
from dslmodel.utils.span import span
from dslmodel.parliament.liquid_vote import tally
from dslmodel.generated.python.merge_oracle import merge_oracle_span

@span("merge_oracle")
def decide(motion_id:str):
    accepted = tally(motion_id, ["origin"])
    repo = pathlib.Path(".").resolve()
    if accepted:
        subprocess.run(["git","merge","--no-ff",f"motions/{motion_id}"],
                       check=True)
    else:
        subprocess.run(["git","branch","-D",f"motions/{motion_id}"],check=True)
    merge_oracle_span.span().set_attribute("merge.outcome",
                                           "accepted" if accepted else "rejected")