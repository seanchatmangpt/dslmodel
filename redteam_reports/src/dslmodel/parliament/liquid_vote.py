import subprocess, json, networkx as nx, pathlib
from dslmodel.utils.span import span
from dslmodel.generated.python.governance_federated_vote import governance_federated_vote_span

def _ls_remote(remote, pattern):
    out = subprocess.check_output(["git","ls-remote",remote,pattern])
    for ln in out.decode().splitlines():
        sha, ref = ln.split()
        yield sha, ref

@span("governance_federated_vote")
def tally(motion_id:str, remotes:list[str], quorum=0.6):
    votes, deleg = {}, nx.DiGraph()
    for r in remotes:
        for sha, ref in _ls_remote(r, f"refs/vote/{motion_id}/*"):
            _,_,repo,_ = ref.split("/",3)
            blob = subprocess.check_output(["git","fetch",r,sha,"--depth=1","--stdout"])
            v = json.loads(blob.decode()); votes[repo]=(v["vote"],v["weight"])
        for sha, ref in _ls_remote(r, "refs/delegate/*"):
            _,_,frm = ref.split("/",2)
            to = subprocess.check_output(["git","show",f"{sha}"]).decode().strip()
            deleg.add_edge(frm,to)
    # resolve delegation
    for repo in list(votes.keys()):
        if deleg.has_node(repo):
            tgt = next(nx.dfs_postorder_nodes(deleg, repo))
            votes[tgt] = votes.pop(repo)
    wt = sum(w for _,w in votes.values())
    yes= sum(w for v,w in votes.values() if v=="for")
    return yes/wt>=quorum