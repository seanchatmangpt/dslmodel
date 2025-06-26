---
to: src/dslmodel/mixins/<%= fileName %>.py
---
"""
<%= name %> FSM Mixin - <%= description %>

This mixin provides finite state machine capabilities for <%= name.toLowerCase() %> operations
with <%= has_timeout ? 'timeout handling, ' : '' %><%= has_retry ? 'retry logic, ' : '' %><%= has_callbacks ? 'callbacks, ' : '' %><%= has_persistence ? 'and persistence' : '' %>.
"""

import time
import json
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
from datetime import datetime, timedelta
from pydantic import Field, BaseModel
from transitions import Machine
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def trigger(trigger_name: str):
    """Decorator for FSM trigger methods.
    
    Args:
        trigger_name: Name of the trigger to handle
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logger.info(f"Trigger '{trigger_name}' activated in {self.__class__.__name__}")
            return func(self, *args, **kwargs)
        wrapper._trigger_name = trigger_name
        return wrapper
    return decorator


class <%= className %>(BaseModel):
    """<%= description %>"""
    
    # State machine configuration
    state: str = Field(default="<%= initialState %>", description="Current state")
    states: List[str] = Field(
        default=<%= JSON.stringify(states) %>,
        description="Available states"
    )
    
    # State metadata
    state_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="History of state transitions"
    )
    last_transition: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last state transition"
    )
    transition_count: int = Field(
        default=0,
        description="Number of state transitions"
    )
<% if (has_timeout) { %>    
    # Timeout configuration
    state_timeouts: Dict[str, float] = Field(
        default_factory=lambda: {
<% states.forEach(function(state) { %>            "<%= state %>": 300.0,  # 5 minutes
<% }); %>        },
        description="Timeout duration for each state (seconds)"
    )
    timeout_handler: Optional[str] = Field(
        default="handle_timeout",
        description="Method name to call on timeout"
    )
<% } %>
<% if (has_retry) { %>    
    # Retry configuration
    retry_count: int = Field(default=0, description="Current retry count")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries (seconds)")
    failed_attempts: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="History of failed attempts"
    )
<% } %>
<% if (has_persistence) { %>    
    # Persistence configuration
    persistence_file: Optional[Path] = Field(
        default=None,
        description="Path to state persistence file"
    )
    auto_save: bool = Field(
        default=True,
        description="Automatically save state after transitions"
    )
<% } %>
    
    # Machine instance (not serialized)
    _machine: Optional[Machine] = None
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
    
    def __init__(self, **data):
        """Initialize the FSM mixin."""
        super().__init__(**data)
        self._setup_state_machine()
<% if (has_persistence) { %>        
        # Load persisted state if available
        if self.persistence_file and self.persistence_file.exists():
            self._load_state()
<% } %>
<% if (has_timeout) { %>        
        # Start timeout monitoring
        self._last_activity = time.time()
<% } %>
    
    def _setup_state_machine(self):
        """Configure the state machine."""
        # Define transitions
        transitions = [
            # Common transitions
            {"trigger": "initialize", "source": "*", "dest": "<%= initialState %>", "after": "_on_initialize"},
            {"trigger": "reset", "source": "*", "dest": "<%= initialState %>", "after": "_on_reset"},
            {"trigger": "error", "source": "*", "dest": "ERROR", "after": "_on_error"},
<% states.forEach(function(state, index) { %>            
            # <%= state %> transitions
<% if (index < states.length - 1) { %>            {
                "trigger": "to_<%= state.toLowerCase() %>",
                "source": "*",
                "dest": "<%= state %>",
                "conditions": ["_can_transition_to_<%= state.toLowerCase() %>"],
<% if (has_callbacks) { %>                "before": "_before_<%= state.toLowerCase() %>",
                "after": "_after_<%= state.toLowerCase() %>",<% } %>
            },<% } %>
<% }); %>        ]
        
        # Create machine
        self._machine = Machine(
            model=self,
            states=self.states,
            transitions=transitions,
            initial=self.state,
            auto_transitions=False,
            after_state_change=self._after_state_change
        )
    
    def _after_state_change(self):
        """Called after any state change."""
        # Update metadata
        self.last_transition = datetime.now()
        self.transition_count += 1
        
        # Record in history
        self.state_history.append({
            "from_state": self._machine.state if hasattr(self._machine, 'state') else None,
            "to_state": self.state,
            "timestamp": self.last_transition.isoformat(),
            "transition_number": self.transition_count
        })
        
        # Keep history limited
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
<% if (has_timeout) { %>        
        # Reset activity timer
        self._last_activity = time.time()
<% } %>
<% if (has_persistence && auto_save) { %>        
        # Save state if auto-save enabled
        if self.auto_save:
            self._save_state()
<% } %>
        
        logger.info(f"State changed to: {self.state}")
    
    # Condition methods
<% states.forEach(function(state) { %>    def _can_transition_to_<%= state.toLowerCase() %>(self) -> bool:
        """Check if transition to <%= state %> is allowed."""
        # TODO: Implement transition conditions
        return True
    
<% }); %>
    # Callback methods
    def _on_initialize(self):
        """Called when state machine is initialized."""
        logger.info("State machine initialized")
<% if (has_retry) { %>        self.retry_count = 0
        self.failed_attempts.clear()<% } %>
    
    def _on_reset(self):
        """Called when state machine is reset."""
        logger.info("State machine reset")
        self.state_history.clear()
        self.transition_count = 0
<% if (has_retry) { %>        self.retry_count = 0
        self.failed_attempts.clear()<% } %>
    
    def _on_error(self):
        """Called when entering error state."""
        logger.error(f"Entered error state from {self.state_history[-1]['from_state'] if self.state_history else 'unknown'}")
<% if (has_retry) { %>        
        # Record failed attempt
        self.failed_attempts.append({
            "timestamp": datetime.now().isoformat(),
            "previous_state": self.state_history[-1]['from_state'] if self.state_history else None,
            "retry_count": self.retry_count
        })
<% } %>
<% if (has_callbacks) { %>
    # State-specific callbacks
<% states.forEach(function(state) { %>    def _before_<%= state.toLowerCase() %>(self):
        """Called before entering <%= state %> state."""
        logger.debug(f"Preparing to enter <%= state %> state")
    
    def _after_<%= state.toLowerCase() %>(self):
        """Called after entering <%= state %> state."""
        logger.debug(f"Entered <%= state %> state")
    
<% }); %><% } %>
<% if (has_timeout) { %>    # Timeout handling
    def check_timeout(self) -> bool:
        """Check if current state has timed out.
        
        Returns:
            True if timed out, False otherwise
        """
        if self.state not in self.state_timeouts:
            return False
        
        timeout_duration = self.state_timeouts[self.state]
        elapsed = time.time() - self._last_activity
        
        return elapsed > timeout_duration
    
    def handle_timeout(self):
        """Handle state timeout."""
        logger.warning(f"State '{self.state}' timed out after {self.state_timeouts.get(self.state, 0)} seconds")
        
        # Transition to error state
        if hasattr(self, 'error'):
            self.error()
        else:
            self.state = "ERROR"
            self._after_state_change()
    
    def reset_timeout(self):
        """Reset the timeout timer."""
        self._last_activity = time.time()
<% } %>
<% if (has_retry) { %>    # Retry logic
    def retry_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with retry logic.
        
        Args:
            operation: Function to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Result of operation
            
        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                self.retry_count = attempt
                result = operation(*args, **kwargs)
                
                # Reset retry count on success
                self.retry_count = 0
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    # All retries exhausted
                    self.failed_attempts.append({
                        "timestamp": datetime.now().isoformat(),
                        "operation": operation.__name__,
                        "error": str(e),
                        "attempts": self.max_retries
                    })
                    
                    # Transition to error state
                    if hasattr(self, 'error'):
                        self.error()
        
        raise last_exception
<% } %>
<% if (has_persistence) { %>    # Persistence methods
    def _save_state(self) -> bool:
        """Save current state to file.
        
        Returns:
            Success status
        """
        if not self.persistence_file:
            return False
        
        try:
            state_data = {
                "state": self.state,
                "state_history": self.state_history,
                "last_transition": self.last_transition.isoformat() if self.last_transition else None,
                "transition_count": self.transition_count,
<% if (has_retry) { %>                "retry_count": self.retry_count,
                "failed_attempts": self.failed_attempts,<% } %>
                "saved_at": datetime.now().isoformat()
            }
            
            self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
            self.persistence_file.write_text(json.dumps(state_data, indent=2))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False
    
    def _load_state(self) -> bool:
        """Load state from file.
        
        Returns:
            Success status
        """
        if not self.persistence_file or not self.persistence_file.exists():
            return False
        
        try:
            state_data = json.loads(self.persistence_file.read_text())
            
            self.state = state_data.get("state", self.state)
            self.state_history = state_data.get("state_history", [])
            self.transition_count = state_data.get("transition_count", 0)
            
            if state_data.get("last_transition"):
                self.last_transition = datetime.fromisoformat(state_data["last_transition"])
<% if (has_retry) { %>            
            self.retry_count = state_data.get("retry_count", 0)
            self.failed_attempts = state_data.get("failed_attempts", [])<% } %>
            
            logger.info(f"Loaded state from {self.persistence_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return False
<% } %>
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information.
        
        Returns:
            Dictionary containing state information
        """
        info = {
            "current_state": self.state,
            "available_states": self.states,
            "transition_count": self.transition_count,
            "last_transition": self.last_transition.isoformat() if self.last_transition else None,
            "history_length": len(self.state_history)
        }
<% if (has_timeout) { %>        
        # Add timeout info
        if self.state in self.state_timeouts:
            elapsed = time.time() - self._last_activity
            remaining = self.state_timeouts[self.state] - elapsed
            info["timeout_remaining"] = max(0, remaining)
<% } %>
<% if (has_retry) { %>        
        # Add retry info
        info["retry_count"] = self.retry_count
        info["max_retries"] = self.max_retries
        info["failed_attempts"] = len(self.failed_attempts)
<% } %>
        
        return info
    
    def visualize_state_machine(self) -> str:
        """Generate a text representation of the state machine.
        
        Returns:
            ASCII representation of states and transitions
        """
        lines = ["State Machine Diagram:", "=" * 40]
        
        # Show states
        lines.append("States:")
        for state in self.states:
            marker = "→" if state == self.state else " "
            lines.append(f"  {marker} [{state}]")
        
        # Show recent transitions
        lines.append("\nRecent Transitions:")
        for transition in self.state_history[-5:]:
            lines.append(f"  {transition.get('from_state', '?')} → {transition.get('to_state', '?')}")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    class Example<%= name %>Model(BaseModel, <%= className %>):
        """Example model using <%= className %>."""
        name: str = Field(default="Example")
        
        def process(self):
            """Example process method."""
            print(f"Processing in state: {self.state}")
<% if (has_retry) { %>            
            # Example with retry
            def risky_operation():
                import random
                if random.random() < 0.7:  # 70% chance of failure
                    raise Exception("Random failure")
                return "Success!"
            
            try:
                result = self.retry_operation(risky_operation)
                print(f"Operation succeeded: {result}")
            except Exception as e:
                print(f"Operation failed after {self.max_retries} attempts")
<% } %>
    
    # Create instance
    model = Example<%= name %>Model()
    
    # Show initial state
    print(model.visualize_state_machine())
    print(f"\nState info: {model.get_state_info()}")
    
    # Perform transitions
    if hasattr(model, 'to_<%= states[1].toLowerCase() %>'):
        model.to_<%= states[1].toLowerCase() %>()
        print(f"\nTransitioned to: {model.state}")
    
    # Process
    model.process()
<% if (has_persistence) { %>    
    # Save state
    model.persistence_file = Path("example_<%= name.toLowerCase() %>_state.json")
    model._save_state()
    print(f"\nState saved to: {model.persistence_file}")
<% } %>