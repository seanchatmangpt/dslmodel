"""
Simple FSM Demo to test basic functionality

This demonstrates the simplest possible FSM with DSLModel integration.
"""
from enum import Enum
from loguru import logger

from dslmodel import DSLModel
from dslmodel.mixins import FSMMixin, trigger


class SimpleState(str, Enum):
    """Simple workflow states."""
    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"


class SimpleFSM(DSLModel, FSMMixin):
    """Minimal FSM example."""
    
    name: str
    state: str = SimpleState.IDLE.value  # Store as string value
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Setup FSM - this will override self.state with the initial value
        self.setup_fsm(
            state_enum=SimpleState,
            initial=SimpleState.IDLE.value
        )
        
        logger.info(f"Initialized {self.name}, state: {self.state}")
    
    def setup_transitions(self):
        """Define transitions manually."""
        self.add_transition(
            trigger="start",
            source=SimpleState.IDLE.value,
            dest=SimpleState.RUNNING.value,
            after="on_start"
        )
        
        self.add_transition(
            trigger="finish",
            source=SimpleState.RUNNING.value,
            dest=SimpleState.DONE.value,
            after="on_finish"
        )
    
    def on_start(self):
        logger.info(f"{self.name} started running")
    
    def on_finish(self):
        logger.info(f"{self.name} finished")
    
    def run_demo(self):
        """Run through the state machine."""
        logger.info(f"Initial state: {self.state}")
        logger.info(f"Available triggers: {self.possible_triggers()}")
        
        # Start
        self.start()
        logger.info(f"After start - state: {self.state}")
        logger.info(f"Available triggers: {self.possible_triggers()}")
        
        # Finish
        self.finish()
        logger.info(f"After finish - state: {self.state}")
        logger.info(f"Available triggers: {self.possible_triggers()}")


def main():
    """Run simple FSM demo."""
    fsm = SimpleFSM(name="test-fsm")
    fsm.run_demo()
    
    # Test FSM with OTEL integration
    logger.info("\n=== Testing with OTEL Attributes ===")
    from dslmodel.otel.models.dslmodel_attributes import DslmodelAttributes
    
    # Create OTEL attributes based on FSM state
    otel_attrs = DslmodelAttributes(
        workflow_name=fsm.name,
        workflow_status="completed" if fsm.state == SimpleState.DONE.value else "started"
    )
    
    logger.info(f"OTEL namespace: {otel_attrs.otel_namespace()}")
    logger.info(f"OTEL attributes: {otel_attrs.model_dump()}")
    

if __name__ == "__main__":
    main()