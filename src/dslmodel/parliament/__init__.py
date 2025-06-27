"""
Git-native Robert's Rules parliament.

Every motion = branch `motions/<id>`
Seconds & debate = git notes
Votes          = vote refs
"""

import subprocess, pathlib, json, uuid, datetime
from dslmodel.utils.git_auto import git_wrap
from dslmodel.utils.span import span
from dslmodel.generated.python.roberts_agenda_item import roberts_agenda_item_span
from dslmodel.generated.python.roberts_motion_second import roberts_motion_second_span
from dslmodel.generated.python.roberts_debate_cycle import roberts_debate_cycle_span
from dslmodel.generated.python.roberts_vote_tally import roberts_vote_tally_span

REPO = pathlib.Path(".").resolve()

@git_wrap("branch")
def _branch(repo, name, base="HEAD"): ...

@git_wrap("notes_add")
def _note(ref, target, message): ...

@git_wrap("push")        # vote refs push
def _push(repo_path, remote, refspec): ...

class Parliament:
    """High-level API used by agents & MergeOracle"""

    def new_motion(self, title: str, body: str) -> str:
        motion_id = f"M{uuid.uuid4().hex[:6]}"
        path      = REPO / f"motions/{motion_id}.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"# {title}\n\n{body}\n")
        subprocess.run(["git","add",path],check=True)
        _branch(repo=REPO, name=f"motions/{motion_id}")
        subprocess.run(["git","commit","-m",f"motion: {motion_id} {title}"],
                       check=True)
        return motion_id

    def second(self, motion_sha: str, speaker: str):
        _note(ref="second", target=motion_sha,
              message=json.dumps({"speaker":speaker,
                                  "ts":datetime.datetime.utcnow().isoformat()}))

    def debate(self, motion_sha: str, speaker:str, stance:str, argument:str):
        _note(ref="debate", target=motion_sha,
              message=json.dumps({"sp":speaker,"st":stance,"arg":argument}))

    def vote(self, motion_id: str, repo_name:str, val:str, weight:float=1.0):
        ref = f"refs/vote/{motion_id}/{repo_name}/{uuid.uuid4().hex}"
        blob = json.dumps({"vote":val, "weight":weight}).encode()
        subprocess.run(["git","hash-object","-w","--stdin"],input=blob)
        sha = subprocess.check_output(["git","hash-object","-w","--stdin"],
                                      input=blob).decode().strip()
        subprocess.run(["git","update-ref",ref,sha],check=True)
        _push(repo_path=REPO, remote="origin", refspec=ref)