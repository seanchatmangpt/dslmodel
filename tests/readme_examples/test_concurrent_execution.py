from dslmodel import DSLModel, init_lm
from dslmodel.utils.model_tools import run_dsls
from pydantic import Field

def test_concurrent_execution():
    class Participant(DSLModel):
        name: str = Field(...)
        role: str = Field(...)

    tasks = [(Participant, "Create a person with a name and job role") for _ in range(3)]
    init_lm()
    results = run_dsls(tasks, max_workers=3)
    assert len(results) == 3
    for result in results:
        assert isinstance(result, Participant) 