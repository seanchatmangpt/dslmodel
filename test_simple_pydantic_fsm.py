"""Test FSM with pure Pydantic instead of DSLModel."""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from dslmodel.mixins.fsm_mixin import FSMMixin, trigger

class SimpleState(str, Enum):
    start = "start"
    middle = "middle"
    end = "end"

class SimpleTask(BaseModel, FSMMixin):
    model_config = ConfigDict(extra="allow")
    
    name: str
    state: SimpleState = Field(default=SimpleState.start)
    
    def __init__(self, **data):
        # Initialize Pydantic BaseModel first
        super().__init__(**data)
        # Then initialize FSMMixin
        FSMMixin.__init__(self)
        
    def model_post_init(self, __context):
        super().model_post_init(__context)
        print(f"State after init: {self.state}")
        self.setup_fsm(SimpleState, initial=SimpleState.start)
        # Ensure state is properly set after FSM setup
        print(f"State after FSM setup: {self.state}")
        if self.state is None:
            self.state = SimpleState.start
            print(f"Fixed state to: {self.state}")
        
    @trigger(source=SimpleState.start, dest=SimpleState.middle)
    def go_middle(self):
        return True
        
    @trigger(source=SimpleState.middle, dest=SimpleState.end)
    def go_end(self):
        return True

# Test with pure Pydantic
try:
    print("Testing with pure Pydantic BaseModel...")
    task = SimpleTask(name="test")
    print(f"✅ Created task with state: {task.state}")
    
    task.go_middle()
    print(f"✅ After go_middle: {task.state}")
    
    task.go_end()
    print(f"✅ After go_end: {task.state}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()