from dslmodel import DSLModel, init_lm
from pydantic import Field
from dspy.utils.dummies import DummyLM
import dspy

def test_meeting_from_prompt():
    class Participant(DSLModel):
        name: str = Field("Alice")
        role: str = Field("Manager")

    class Meeting(DSLModel):
        name: str = Field(...)
        participants: list[Participant] = Field(...)

    # Mock the LM to return a Meeting with two participants
    lm = DummyLM([
        {"root_model_kwargs_dict": "{'name': 'Team sync', 'participants': [ {'name': 'Alice', 'role': 'Manager'}, {'name': 'Alice', 'role': 'Manager'} ]}"}
    ])
    dspy.settings.configure(lm=lm)

    participants = [Participant() for _ in range(2)]
    meeting = Meeting.from_prompt("Team sync", participants=participants)
    assert isinstance(meeting, Meeting)
    assert len(meeting.participants) == 2 