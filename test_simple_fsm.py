"""Simple test to debug FSM + DSLModel integration."""

from enum import Enum
from pydantic import Field
from dslmodel.dsl_models import DSLModel
from dslmodel.mixins.fsm_mixin import FSMMixin, trigger

class SimpleState(str, Enum):
    start = "start"
    middle = "middle"
    end = "end"

class SimpleTask(DSLModel, FSMMixin):
    name: str
    state: SimpleState = Field(default=SimpleState.start)
    
    def model_post_init(self, __context):
        super().model_post_init(__context)
        FSMMixin.__init__(self)
        print(f"State after init: {self.state}")
        self.setup_fsm(SimpleState, initial=SimpleState.start)
        
    @trigger(source=SimpleState.start, dest=SimpleState.middle)
    def go_middle(self):
        return True
        
    @trigger(source=SimpleState.middle, dest=SimpleState.end)
    def go_end(self):
        return True

# Test
try:
    # Explicit state initialization
    task = SimpleTask(name="test", state=SimpleState.start)
    print(f"✅ Created task with state: {task.state}")
    
    task.go_middle()
    print(f"✅ After go_middle: {task.state}")
    
    task.go_end()
    print(f"✅ After go_end: {task.state}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()