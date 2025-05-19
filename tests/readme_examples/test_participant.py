from dslmodel import DSLModel
from pydantic import Field

def test_participant_fields():
    class Participant(DSLModel):
        name: str = Field("John Doe")
        role: str = Field("Engineer")
    p = Participant()
    assert p.name == "John Doe"
    assert p.role == "Engineer" 