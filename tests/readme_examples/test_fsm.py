from enum import Enum, auto
from dslmodel.mixins import FSMMixin, trigger

def test_fsm_transitions():
    class SalesState(Enum):
        INITIALIZING = auto()
        RESEARCHING = auto()
        OUTREACHING = auto()
        CLOSING = auto()
        COMPLETING = auto()

    class ChallengerSalesAgent(FSMMixin):
        def __init__(self):
            super().__init__()
            self.setup_fsm(state_enum=SalesState, initial=SalesState.INITIALIZING)

        @trigger(source=SalesState.INITIALIZING, dest=SalesState.RESEARCHING)
        def start_research(self):
            pass

        @trigger(source=SalesState.RESEARCHING, dest=SalesState.OUTREACHING)
        def conduct_outreach(self):
            pass

        @trigger(source=SalesState.OUTREACHING, dest=SalesState.CLOSING)
        def close_deal(self):
            pass

        @trigger(source=SalesState.CLOSING, dest=SalesState.COMPLETING)
        def complete_sale(self):
            pass

    agent = ChallengerSalesAgent()
    assert agent.state_enum_value == SalesState.INITIALIZING
    agent.start_research()
    assert agent.state_enum_value == SalesState.RESEARCHING
    agent.conduct_outreach()
    assert agent.state_enum_value == SalesState.OUTREACHING
    agent.close_deal()
    assert agent.state_enum_value == SalesState.CLOSING
    agent.complete_sale()
    assert agent.state_enum_value == SalesState.COMPLETING 