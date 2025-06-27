"""
Task Coordination System
========================

Provides task creation, queuing, and coordination capabilities
for multi-agent systems. Integrates with OTEL for tracking.
"""

import json
import datetime
import threading
import queue
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from .span import span
except ImportError:
    def span(name):
        def decorator(func):
            return func
        return decorator

try:
    from .log_tools import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

@dataclass
class Task:
    """Represents a coordinated task."""
    id: str
    agent: str
    args: List[Any]
    priority: int = 50
    status: str = "pending"
    created_at: str = None
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()

class TaskCoordinator:
    """Central task coordination system."""
    
    def __init__(self, persist_path: Optional[Path] = None):
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.PriorityQueue()
        self.persist_path = persist_path or Path("task_coordination.json")
        self._lock = threading.Lock()
        self._load_state()
    
    def _load_state(self):
        """Load persisted task state."""
        if self.persist_path.exists():
            try:
                with open(self.persist_path) as f:
                    data = json.load(f)
                    for task_data in data.get("tasks", []):
                        task = Task(**task_data)
                        self.tasks[task.id] = task
                        if task.status == "pending":
                            self.task_queue.put((100 - task.priority, task.id))
            except Exception as e:
                logger.warning(f"Failed to load task state: {e}")
    
    def _save_state(self):
        """Persist task state."""
        try:
            data = {"tasks": [asdict(task) for task in self.tasks.values()]}
            with open(self.persist_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save task state: {e}")
    
    @span("task_create")
    def create_task(self, agent: str, args: List[Any], priority: int = 50) -> str:
        """Create a new coordinated task."""
        task_id = f"task_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.tasks)}"
        
        task = Task(
            id=task_id,
            agent=agent,
            args=args,
            priority=priority
        )
        
        with self._lock:
            self.tasks[task_id] = task
            self.task_queue.put((100 - priority, task_id))  # Higher priority = lower number
            self._save_state()
        
        logger.info(f"Created task {task_id} for agent {agent} with priority {priority}")
        return task_id
    
    @span("task_get_next")
    def get_next_task(self) -> Optional[Task]:
        """Get the next highest priority task."""
        try:
            _, task_id = self.task_queue.get_nowait()
            with self._lock:
                task = self.tasks.get(task_id)
                if task and task.status == "pending":
                    task.status = "running"
                    self._save_state()
                    return task
        except queue.Empty:
            pass
        return None
    
    @span("task_complete")
    def complete_task(self, task_id: str, result: Any = None, error: Optional[str] = None):
        """Mark a task as completed."""
        with self._lock:
            task = self.tasks.get(task_id)
            if task:
                task.status = "completed" if error is None else "failed"
                task.completed_at = datetime.datetime.now().isoformat()
                task.result = result
                task.error = error
                self._save_state()
                logger.info(f"Task {task_id} completed with status {task.status}")
    
    @span("task_list")
    def list_tasks(self, status_filter: Optional[str] = None) -> List[Task]:
        """List tasks, optionally filtered by status."""
        with self._lock:
            tasks = list(self.tasks.values())
            if status_filter:
                tasks = [t for t in tasks if t.status == status_filter]
            return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    @span("task_get_status")
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        with self._lock:
            task = self.tasks.get(task_id)
            return asdict(task) if task else None

# Global coordinator instance
_coordinator = None

def get_coordinator() -> TaskCoordinator:
    """Get or create the global task coordinator."""
    global _coordinator
    if _coordinator is None:
        _coordinator = TaskCoordinator()
    return _coordinator

@span("create_task")
def create_task(agent: str, args: List[Any], priority: int = 50) -> str:
    """Create a coordinated task (convenience function)."""
    coordinator = get_coordinator()
    return coordinator.create_task(agent, args, priority)

@span("get_next_task")
def get_next_task() -> Optional[Task]:
    """Get the next task to execute (convenience function)."""
    coordinator = get_coordinator()
    return coordinator.get_next_task()

@span("complete_task")
def complete_task(task_id: str, result: Any = None, error: Optional[str] = None):
    """Complete a task (convenience function)."""
    coordinator = get_coordinator()
    coordinator.complete_task(task_id, result, error)

@span("list_tasks")
def list_tasks(status_filter: Optional[str] = None) -> List[Task]:
    """List tasks (convenience function)."""
    coordinator = get_coordinator()
    return coordinator.list_tasks(status_filter)

# Agent integration helpers
@span("execute_agent_task")
def execute_agent_task(task: Task) -> Any:
    """Execute a task for a specific agent."""
    try:
        # This is where you'd route to specific agent implementations
        # For now, we'll just log the task execution
        logger.info(f"Executing task {task.id} for agent {task.agent} with args {task.args}")
        
        # Simulate task execution
        result = {"status": "executed", "agent": task.agent, "args": task.args}
        complete_task(task.id, result)
        return result
        
    except Exception as e:
        logger.error(f"Task {task.id} failed: {e}")
        complete_task(task.id, error=str(e))
        raise

@span("process_task_queue")
def process_task_queue(max_tasks: int = 10) -> List[str]:
    """Process pending tasks from the queue."""
    processed = []
    
    for _ in range(max_tasks):
        task = get_next_task()
        if not task:
            break
            
        try:
            execute_agent_task(task)
            processed.append(task.id)
        except Exception as e:
            logger.error(f"Failed to process task {task.id}: {e}")
    
    return processed