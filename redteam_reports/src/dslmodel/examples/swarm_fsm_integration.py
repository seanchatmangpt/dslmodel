#!/usr/bin/env python3
"""
Swarm + FSM Integration Example
Demonstrates 80/20 swarm coordination with state machine management
"""

from enum import Enum, auto
from typing import List, Dict, Optional
from datetime import datetime

from dslmodel import DSLModel
from dslmodel.mixins import FSMMixin, trigger


class WorkState(Enum):
    """States for work items in the swarm"""
    PENDING = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    VALIDATING = auto()
    COMPLETED = auto()
    FAILED = auto()


class AgentState(Enum):
    """States for swarm agents"""
    IDLE = auto()
    CLAIMING = auto()
    WORKING = auto()
    REPORTING = auto()


class WorkItem(DSLModel):
    """Model for work items"""
    id: str
    description: str
    priority: str = "medium"
    team: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None


class Agent(DSLModel):
    """Model for swarm agents"""
    id: str
    name: str
    team: str = "default"
    capabilities: List[str] = []
    work_completed: int = 0


class SwarmWorkItem(FSMMixin):
    """FSM-managed work item"""
    
    def __init__(self, work_item: WorkItem):
        super().__init__()
        self.work_item = work_item
        self.setup_fsm(state_enum=WorkState, initial=WorkState.PENDING)
    
    @trigger(source=WorkState.PENDING, dest=WorkState.ASSIGNED)
    def assign_to_agent(self, agent_id: str):
        """Assign work to an agent"""
        self.work_item.assigned_to = agent_id
        print(f"📋 Work {self.work_item.id} assigned to {agent_id}")
    
    @trigger(source=WorkState.ASSIGNED, dest=WorkState.IN_PROGRESS)
    def start_work(self):
        """Agent starts working on the item"""
        print(f"🔨 Work {self.work_item.id} in progress")
    
    @trigger(source=WorkState.IN_PROGRESS, dest=WorkState.VALIDATING)
    def submit_for_validation(self):
        """Submit completed work for validation"""
        print(f"🔍 Work {self.work_item.id} submitted for validation")
    
    @trigger(source=WorkState.VALIDATING, dest=WorkState.COMPLETED)
    def validate_success(self):
        """Validation passed"""
        self.work_item.completed_at = datetime.now()
        print(f"✅ Work {self.work_item.id} completed successfully")
    
    @trigger(source=WorkState.VALIDATING, dest=WorkState.FAILED)
    def validate_failure(self):
        """Validation failed"""
        print(f"❌ Work {self.work_item.id} validation failed")
    
    @trigger(source=WorkState.FAILED, dest=WorkState.PENDING)
    def retry_work(self):
        """Return work to pending for retry"""
        self.work_item.assigned_to = None
        print(f"🔄 Work {self.work_item.id} returned to queue")


class SwarmAgent(FSMMixin):
    """FSM-managed swarm agent"""
    
    def __init__(self, agent: Agent):
        super().__init__()
        self.agent = agent
        self.current_work: Optional[SwarmWorkItem] = None
        self.setup_fsm(state_enum=AgentState, initial=AgentState.IDLE)
    
    @trigger(source=AgentState.IDLE, dest=AgentState.CLAIMING)
    def claim_work(self, work: SwarmWorkItem):
        """Claim a work item"""
        self.current_work = work
        print(f"🤖 Agent {self.agent.name} claiming work")
    
    @trigger(source=AgentState.CLAIMING, dest=AgentState.WORKING)
    def begin_work(self):
        """Start working on claimed item"""
        if self.current_work:
            self.current_work.start_work()
        print(f"💼 Agent {self.agent.name} working")
    
    @trigger(source=AgentState.WORKING, dest=AgentState.REPORTING)
    def complete_work(self):
        """Complete current work"""
        if self.current_work:
            self.current_work.submit_for_validation()
        print(f"📊 Agent {self.agent.name} reporting completion")
    
    @trigger(source=AgentState.REPORTING, dest=AgentState.IDLE)
    def return_to_idle(self):
        """Return to idle state"""
        self.agent.work_completed += 1
        self.current_work = None
        print(f"😴 Agent {self.agent.name} idle (completed: {self.agent.work_completed})")


class SwarmCoordinator:
    """
    Coordinates swarm operations using FSM-managed entities
    80/20 implementation focusing on core coordination
    """
    
    def __init__(self):
        self.agents: Dict[str, SwarmAgent] = {}
        self.work_queue: List[SwarmWorkItem] = []
        self.completed_work: List[SwarmWorkItem] = []
    
    def add_agent(self, name: str, team: str = "default") -> str:
        """Add a new agent to the swarm"""
        agent_id = f"agent_{int(datetime.now().timestamp() * 1000000)}"
        agent = Agent(id=agent_id, name=name, team=team)
        self.agents[agent_id] = SwarmAgent(agent)
        return agent_id
    
    def add_work(self, description: str, priority: str = "medium") -> str:
        """Add work to the queue"""
        work_id = f"work_{int(datetime.now().timestamp() * 1000000)}"
        work_item = WorkItem(id=work_id, description=description, priority=priority)
        self.work_queue.append(SwarmWorkItem(work_item))
        return work_id
    
    def process_cycle(self):
        """Process one coordination cycle"""
        print("\n🔄 Processing coordination cycle...")
        
        # Find idle agents
        idle_agents = [
            agent for agent in self.agents.values() 
            if agent.state == "IDLE"
        ]
        
        # Find pending work
        pending_work = [
            work for work in self.work_queue 
            if work.state == "PENDING"
        ]
        
        # Match agents to work
        for agent, work in zip(idle_agents, pending_work):
            # Agent claims work
            agent.forward("claim available work")
            
            # Assign work to agent
            work.assign_to_agent(agent.agent.id)
            
            # Agent begins work
            agent.forward("start working on assigned task")
            
            # Simulate work completion
            agent.forward("complete the assigned work")
            
            # Validate work
            import random
            if random.random() > 0.2:  # 80% success rate
                work.forward("validation passed")
                self.completed_work.append(work)
                self.work_queue.remove(work)
            else:
                work.forward("validation failed")
                work.forward("retry the work")
            
            # Agent returns to idle
            agent.forward("return to idle state")
    
    def get_status(self) -> Dict[str, any]:
        """Get swarm status"""
        return {
            "agents": {
                "total": len(self.agents),
                "idle": sum(1 for a in self.agents.values() if a.state == "IDLE"),
                "working": sum(1 for a in self.agents.values() if a.state == "WORKING")
            },
            "work": {
                "pending": sum(1 for w in self.work_queue if w.state == "PENDING"),
                "in_progress": sum(1 for w in self.work_queue if w.state == "IN_PROGRESS"),
                "completed": len(self.completed_work)
            }
        }


def demo():
    """Run swarm + FSM demo"""
    print("🚀 Swarm + FSM Integration Demo")
    print("=" * 50)
    
    # Initialize coordinator
    coordinator = SwarmCoordinator()
    
    # Add agents
    print("\n📥 Creating agents...")
    for i in range(3):
        agent_id = coordinator.add_agent(f"Agent_{i}", team="alpha")
        print(f"  → Created {agent_id}")
    
    # Add work items
    print("\n📋 Creating work items...")
    tasks = [
        "Implement user authentication",
        "Optimize database queries",
        "Generate telemetry reports",
        "Update API documentation",
        "Review security policies"
    ]
    
    for task in tasks:
        work_id = coordinator.add_work(task, priority="medium")
        print(f"  → Created work: {task}")
    
    # Run coordination cycles
    print("\n🔧 Running coordination cycles...")
    for cycle in range(3):
        print(f"\n--- Cycle {cycle + 1} ---")
        coordinator.process_cycle()
        
        status = coordinator.get_status()
        print(f"\n📊 Status after cycle {cycle + 1}:")
        print(f"  Agents: {status['agents']['idle']} idle, {status['agents']['working']} working")
        print(f"  Work: {status['work']['pending']} pending, {status['work']['completed']} completed")
    
    # Final report
    print("\n📈 Final Report:")
    for agent_id, agent in coordinator.agents.items():
        print(f"  {agent.agent.name}: {agent.agent.work_completed} tasks completed")
    
    print(f"\n✅ Total completed: {len(coordinator.completed_work)} tasks")


if __name__ == "__main__":
    from dslmodel import init_instant
    init_instant()
    demo()