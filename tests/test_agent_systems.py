#!/usr/bin/env python3
"""Agent Systems Test Suite
Tests for SwarmAgent coordination, autonomous systems, agent management, and coordination.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import time

# Import agent components
from dslmodel.agents.swarm_agent import SwarmAgent
from dslmodel.agents.agent_coordinator import AgentCoordinator
from dslmodel.agents.worktree_manager import WorktreeManager
from dslmodel.agents.capability_manager import CapabilityManager
from dslmodel.agents.autonomous_engine import AutonomousEngine
from dslmodel.agents.ollama_integration import OllamaIntegration
from dslmodel.agents.disc_integration import DISCIntegration
from dslmodel.agents.parliament import GitParliament
from dslmodel.agents.workflow_agent import WorkflowAgent


class TestSwarmAgent:
    """Test SwarmAgent functionality"""
    
    def test_agent_creation(self):
        """Test SwarmAgent creation and initialization"""
        agent = SwarmAgent(
            name="test_agent",
            capabilities=["code_generation", "testing"],
            worktree_path="/tmp/test_worktree"
        )
        
        assert agent.name == "test_agent"
        assert "code_generation" in agent.capabilities
        assert agent.worktree_path == "/tmp/test_worktree"
        assert agent.status == "idle"
    
    def test_agent_capability_check(self):
        """Test agent capability checking"""
        agent = SwarmAgent(
            name="test_agent",
            capabilities=["code_generation", "testing", "deployment"],
            worktree_path="/tmp/test"
        )
        
        # Test capability checking
        assert agent.has_capability("code_generation") == True
        assert agent.has_capability("deployment") == True
        assert agent.has_capability("security_audit") == False
    
    def test_agent_work_assignment(self):
        """Test work assignment to agents"""
        agent = SwarmAgent(
            name="test_agent",
            capabilities=["code_generation"],
            worktree_path="/tmp/test"
        )
        
        work_item = {
            "id": "work_001",
            "type": "code_generation",
            "description": "Generate user model",
            "priority": "high"
        }
        
        result = agent.assign_work(work_item)
        
        assert result["assigned"] == True
        assert agent.current_work["id"] == "work_001"
        assert agent.status == "working"
    
    def test_agent_work_completion(self):
        """Test work completion by agents"""
        agent = SwarmAgent(
            name="test_agent",
            capabilities=["code_generation"],
            worktree_path="/tmp/test"
        )
        
        # Assign work first
        work_item = {"id": "work_001", "type": "code_generation"}
        agent.assign_work(work_item)
        
        # Complete work
        result = {
            "work_id": "work_001",
            "status": "completed",
            "output": "Generated user model successfully"
        }
        
        completion = agent.complete_work(result)
        
        assert completion["completed"] == True
        assert agent.status == "idle"
        assert agent.current_work is None
    
    def test_agent_telemetry_integration(self):
        """Test agent telemetry integration"""
        agent = SwarmAgent(
            name="test_agent",
            capabilities=["code_generation"],
            worktree_path="/tmp/test"
        )
        
        # Mock telemetry data
        telemetry_data = {
            "agent_id": agent.id,
            "operation": "work_assignment",
            "duration": 1.5,
            "success": True
        }
        
        result = agent.record_telemetry(telemetry_data)
        
        assert result["recorded"] == True
        assert len(agent.telemetry_history) > 0


class TestAgentCoordinator:
    """Test agent coordination functionality"""
    
    def test_coordinator_initialization(self):
        """Test agent coordinator initialization"""
        coordinator = AgentCoordinator()
        
        assert coordinator is not None
        assert hasattr(coordinator, 'register_agent')
        assert hasattr(coordinator, 'assign_work')
        assert hasattr(coordinator, 'get_agent_status')
    
    def test_agent_registration(self):
        """Test agent registration with coordinator"""
        coordinator = AgentCoordinator()
        
        agent = SwarmAgent(
            name="test_agent",
            capabilities=["code_generation"],
            worktree_path="/tmp/test"
        )
        
        result = coordinator.register_agent(agent)
        
        assert result["registered"] == True
        assert agent.name in coordinator.agents
        assert coordinator.get_agent_count() == 1
    
    def test_work_distribution(self):
        """Test work distribution among agents"""
        coordinator = AgentCoordinator()
        
        # Register multiple agents
        agents = [
            SwarmAgent(name="agent1", capabilities=["code_generation"], worktree_path="/tmp/1"),
            SwarmAgent(name="agent2", capabilities=["testing"], worktree_path="/tmp/2"),
            SwarmAgent(name="agent3", capabilities=["deployment"], worktree_path="/tmp/3")
        ]
        
        for agent in agents:
            coordinator.register_agent(agent)
        
        # Distribute work
        work_items = [
            {"id": "work1", "type": "code_generation", "priority": "high"},
            {"id": "work2", "type": "testing", "priority": "medium"},
            {"id": "work3", "type": "deployment", "priority": "low"}
        ]
        
        assignments = coordinator.distribute_work(work_items)
        
        assert len(assignments) == 3
        assert all(assignment["assigned"] for assignment in assignments)
    
    def test_agent_load_balancing(self):
        """Test agent load balancing"""
        coordinator = AgentCoordinator()
        
        # Register agents with different capabilities
        agents = [
            SwarmAgent(name="agent1", capabilities=["code_generation"], worktree_path="/tmp/1"),
            SwarmAgent(name="agent2", capabilities=["code_generation"], worktree_path="/tmp/2"),
            SwarmAgent(name="agent3", capabilities=["testing"], worktree_path="/tmp/3")
        ]
        
        for agent in agents:
            coordinator.register_agent(agent)
        
        # Assign multiple code generation tasks
        work_items = [
            {"id": f"work{i}", "type": "code_generation"} for i in range(5)
        ]
        
        assignments = coordinator.distribute_work(work_items)
        
        # Should distribute among available agents
        assigned_agents = set(assignment["agent_name"] for assignment in assignments)
        assert len(assigned_agents) >= 2  # Should use multiple agents
    
    def test_coordination_cycle(self):
        """Test coordination cycle execution"""
        coordinator = AgentCoordinator()
        
        # Register agents
        agents = [
            SwarmAgent(name="agent1", capabilities=["code_generation"], worktree_path="/tmp/1"),
            SwarmAgent(name="agent2", capabilities=["testing"], worktree_path="/tmp/2")
        ]
        
        for agent in agents:
            coordinator.register_agent(agent)
        
        # Run coordination cycle
        cycle_result = coordinator.run_coordination_cycle()
        
        assert cycle_result["cycle_completed"] == True
        assert "agents_checked" in cycle_result
        assert "work_processed" in cycle_result


class TestWorktreeManager:
    """Test worktree management functionality"""
    
    def test_worktree_creation(self):
        """Test worktree creation and management"""
        manager = WorktreeManager()
        
        worktree_info = {
            "name": "feature_branch",
            "branch": "feature/user-management",
            "base_branch": "main"
        }
        
        result = manager.create_worktree(worktree_info)
        
        assert result["created"] == True
        assert "path" in result
        assert result["name"] == "feature_branch"
    
    def test_worktree_listing(self):
        """Test worktree listing functionality"""
        manager = WorktreeManager()
        
        # Create some worktrees
        worktrees = [
            {"name": "feature1", "branch": "feature/feature1"},
            {"name": "feature2", "branch": "feature/feature2"}
        ]
        
        for worktree in worktrees:
            manager.create_worktree(worktree)
        
        # List worktrees
        listed = manager.list_worktrees()
        
        assert len(listed) >= 2
        assert any(wt["name"] == "feature1" for wt in listed)
        assert any(wt["name"] == "feature2" for wt in listed)
    
    def test_worktree_cleanup(self):
        """Test worktree cleanup functionality"""
        manager = WorktreeManager()
        
        # Create worktree
        worktree_info = {"name": "temp_feature", "branch": "feature/temp"}
        manager.create_worktree(worktree_info)
        
        # Clean up
        result = manager.cleanup_worktree("temp_feature")
        
        assert result["cleaned"] == True
    
    def test_worktree_isolation(self):
        """Test worktree isolation for agent work"""
        manager = WorktreeManager()
        
        # Create isolated worktree for agent
        agent_worktree = manager.create_isolated_worktree("agent_work")
        
        assert agent_worktree["isolated"] == True
        assert "agent_id" in agent_worktree
        assert "exclusive_access" in agent_worktree


class TestCapabilityManager:
    """Test capability management functionality"""
    
    def test_capability_registration(self):
        """Test capability registration"""
        manager = CapabilityManager()
        
        capability = {
            "name": "code_generation",
            "description": "Generate code from specifications",
            "requirements": ["python", "dspy"],
            "version": "1.0.0"
        }
        
        result = manager.register_capability(capability)
        
        assert result["registered"] == True
        assert "code_generation" in manager.capabilities
    
    def test_capability_matching(self):
        """Test capability matching for work items"""
        manager = CapabilityManager()
        
        # Register capabilities
        capabilities = [
            {"name": "code_generation", "description": "Generate code"},
            {"name": "testing", "description": "Run tests"},
            {"name": "deployment", "description": "Deploy applications"}
        ]
        
        for cap in capabilities:
            manager.register_capability(cap)
        
        # Test matching
        work_item = {"type": "code_generation", "priority": "high"}
        matches = manager.find_matching_capabilities(work_item)
        
        assert len(matches) == 1
        assert matches[0]["name"] == "code_generation"
    
    def test_capability_validation(self):
        """Test capability validation"""
        manager = CapabilityManager()
        
        # Test valid capability
        valid_capability = {
            "name": "valid_capability",
            "description": "Valid capability",
            "requirements": ["python"],
            "version": "1.0.0"
        }
        
        validation = manager.validate_capability(valid_capability)
        assert validation["valid"] == True
        
        # Test invalid capability
        invalid_capability = {
            "name": "",  # Empty name
            "description": "Invalid capability"
        }
        
        validation = manager.validate_capability(invalid_capability)
        assert validation["valid"] == False
    
    def test_capability_export(self):
        """Test capability export functionality"""
        manager = CapabilityManager()
        
        # Register capabilities
        capabilities = [
            {"name": "cap1", "description": "Capability 1"},
            {"name": "cap2", "description": "Capability 2"}
        ]
        
        for cap in capabilities:
            manager.register_capability(cap)
        
        # Export capabilities
        exported = manager.export_capabilities()
        
        assert len(exported) == 2
        assert "cap1" in [cap["name"] for cap in exported]
        assert "cap2" in [cap["name"] for cap in exported]


class TestAutonomousEngine:
    """Test autonomous decision engine"""
    
    def test_engine_initialization(self):
        """Test autonomous engine initialization"""
        engine = AutonomousEngine()
        
        assert engine is not None
        assert hasattr(engine, 'analyze_system')
        assert hasattr(engine, 'make_decisions')
        assert hasattr(engine, 'execute_actions')
    
    def test_system_analysis(self):
        """Test system analysis functionality"""
        engine = AutonomousEngine()
        
        # Mock system state
        system_state = {
            "agents": [
                {"name": "agent1", "status": "idle", "capabilities": ["code_generation"]},
                {"name": "agent2", "status": "working", "capabilities": ["testing"]}
            ],
            "work_queue": [
                {"id": "work1", "type": "code_generation", "priority": "high"}
            ],
            "telemetry": {
                "error_rate": 0.05,
                "response_time": 250
            }
        }
        
        analysis = engine.analyze_system(system_state)
        
        assert analysis["analyzed"] == True
        assert "insights" in analysis
        assert "recommendations" in analysis
    
    def test_decision_making(self):
        """Test autonomous decision making"""
        engine = AutonomousEngine()
        
        # Mock analysis results
        analysis = {
            "insights": ["agent1 is idle", "high priority work available"],
            "recommendations": ["assign work to agent1", "monitor error rate"]
        }
        
        decisions = engine.make_decisions(analysis)
        
        assert len(decisions) > 0
        assert all("action" in decision for decision in decisions)
        assert all("priority" in decision for decision in decisions)
    
    def test_action_execution(self):
        """Test autonomous action execution"""
        engine = AutonomousEngine()
        
        # Mock decisions
        decisions = [
            {
                "action": "assign_work",
                "target": "agent1",
                "work": {"id": "work1", "type": "code_generation"},
                "priority": "high"
            }
        ]
        
        results = engine.execute_actions(decisions)
        
        assert len(results) == 1
        assert results[0]["executed"] == True
        assert results[0]["action"] == "assign_work"
    
    def test_continuous_operation(self):
        """Test continuous autonomous operation"""
        engine = AutonomousEngine()
        
        # Mock continuous loop
        with patch.object(engine, 'analyze_system') as mock_analyze:
            mock_analyze.return_value = {"analyzed": True, "insights": []}
            
            with patch.object(engine, 'make_decisions') as mock_decide:
                mock_decide.return_value = []
                
                with patch.object(engine, 'execute_actions') as mock_execute:
                    mock_execute.return_value = []
                    
                    # Run continuous loop for a few cycles
                    results = engine.run_continuous(max_cycles=3)
                    
                    assert len(results) == 3
                    assert all(result["cycle_completed"] for result in results)


class TestOllamaIntegration:
    """Test Ollama integration functionality"""
    
    def test_ollama_connection(self):
        """Test Ollama connection and status checking"""
        integration = OllamaIntegration()
        
        # Test connection (mocked)
        with patch.object(integration, '_check_ollama_server') as mock_check:
            mock_check.return_value = {"status": "running", "models": ["llama2", "codellama"]}
            
            status = integration.check_connection()
            
            assert status["connected"] == True
            assert "llama2" in status["available_models"]
    
    def test_model_validation(self):
        """Test Ollama model validation"""
        integration = OllamaIntegration()
        
        # Test model validation
        model_info = {
            "name": "llama2",
            "version": "7b",
            "parameters": "7B"
        }
        
        validation = integration.validate_model(model_info)
        
        assert validation["valid"] == True
        assert "capabilities" in validation
    
    def test_prompt_execution(self):
        """Test prompt execution with Ollama"""
        integration = OllamaIntegration()
        
        # Mock prompt execution
        with patch.object(integration, '_execute_prompt') as mock_execute:
            mock_execute.return_value = {
                "response": "Generated code for user model",
                "model": "llama2",
                "duration": 1.5
            }
            
            prompt = "Generate a Python class for user management"
            result = integration.execute_prompt(prompt, model="llama2")
            
            assert result["response"] is not None
            assert result["model"] == "llama2"
            assert result["duration"] > 0
    
    def test_model_benchmarking(self):
        """Test Ollama model benchmarking"""
        integration = OllamaIntegration()
        
        # Mock benchmarking
        with patch.object(integration, '_benchmark_model') as mock_benchmark:
            mock_benchmark.return_value = {
                "model": "llama2",
                "avg_response_time": 1.2,
                "throughput": 10.5,
                "accuracy": 0.85
            }
            
            benchmark = integration.benchmark_model("llama2")
            
            assert benchmark["model"] == "llama2"
            assert benchmark["avg_response_time"] > 0
            assert benchmark["throughput"] > 0


class TestDISCIntegration:
    """Test DISC integration functionality"""
    
    def test_disc_initialization(self):
        """Test DISC integration initialization"""
        integration = DISCIntegration()
        
        assert integration is not None
        assert hasattr(integration, 'analyze_behavior')
        assert hasattr(integration, 'compensate_behavior')
    
    def test_behavior_analysis(self):
        """Test DISC behavior analysis"""
        integration = DISCIntegration()
        
        # Mock behavior data
        behavior_data = {
            "communication_style": "direct",
            "decision_making": "analytical",
            "work_preference": "structured",
            "stress_response": "task_focused"
        }
        
        analysis = integration.analyze_behavior(behavior_data)
        
        assert analysis["analyzed"] == True
        assert "profile" in analysis
        assert "strengths" in analysis
        assert "areas_for_improvement" in analysis
    
    def test_behavioral_compensation(self):
        """Test behavioral compensation strategies"""
        integration = DISCIntegration()
        
        # Mock behavioral gaps
        gaps = [
            {"type": "communication", "issue": "too_direct", "impact": "team_conflict"},
            {"type": "decision_making", "issue": "analysis_paralysis", "impact": "slow_progress"}
        ]
        
        compensation = integration.compensate_behavior(gaps)
        
        assert len(compensation) == 2
        assert all("strategy" in comp for comp in compensation)
        assert all("expected_outcome" in comp for comp in compensation)
    
    def test_team_dynamics_analysis(self):
        """Test team dynamics analysis"""
        integration = DISCIntegration()
        
        # Mock team data
        team_data = {
            "members": [
                {"name": "Alice", "profile": "D", "role": "leader"},
                {"name": "Bob", "profile": "I", "role": "developer"},
                {"name": "Charlie", "profile": "S", "role": "tester"}
            ]
        }
        
        dynamics = integration.analyze_team_dynamics(team_data)
        
        assert dynamics["analyzed"] == True
        assert "team_strengths" in dynamics
        assert "potential_conflicts" in dynamics
        assert "recommendations" in dynamics


class TestGitParliament:
    """Test Git Parliament functionality"""
    
    def test_parliament_initialization(self):
        """Test Git Parliament initialization"""
        parliament = GitParliament()
        
        assert parliament is not None
        assert hasattr(parliament, 'create_motion')
        assert hasattr(parliament, 'vote_on_motion')
        assert hasattr(parliament, 'tally_votes')
    
    def test_motion_creation(self):
        """Test parliamentary motion creation"""
        parliament = GitParliament()
        
        motion_data = {
            "title": "Add user authentication feature",
            "description": "Implement OAuth2 authentication for user management",
            "proposer": "agent1",
            "type": "feature_request"
        }
        
        motion = parliament.create_motion(motion_data)
        
        assert motion["created"] == True
        assert motion["motion_id"] is not None
        assert motion["status"] == "open"
    
    def test_voting_process(self):
        """Test voting process on motions"""
        parliament = GitParliament()
        
        # Create motion
        motion_data = {"title": "Test motion", "proposer": "agent1"}
        motion = parliament.create_motion(motion_data)
        
        # Cast votes
        votes = [
            {"voter": "agent1", "vote": "yes", "reason": "Supports feature"},
            {"voter": "agent2", "vote": "yes", "reason": "Good idea"},
            {"voter": "agent3", "vote": "no", "reason": "Security concerns"}
        ]
        
        for vote in votes:
            result = parliament.vote_on_motion(motion["motion_id"], vote)
            assert result["recorded"] == True
    
    def test_vote_tallying(self):
        """Test vote tallying and decision making"""
        parliament = GitParliament()
        
        # Create and vote on motion
        motion = parliament.create_motion({"title": "Test", "proposer": "agent1"})
        
        # Mock voting
        with patch.object(parliament, 'get_votes') as mock_votes:
            mock_votes.return_value = [
                {"vote": "yes"}, {"vote": "yes"}, {"vote": "no"}
            ]
            
            tally = parliament.tally_votes(motion["motion_id"])
            
            assert tally["total_votes"] == 3
            assert tally["yes_votes"] == 2
            assert tally["no_votes"] == 1
            assert tally["result"] == "passed"


class TestWorkflowAgent:
    """Test workflow agent functionality"""
    
    def test_workflow_agent_creation(self):
        """Test workflow agent creation"""
        agent = WorkflowAgent(
            name="workflow_agent",
            workflow_definitions=["user_management", "order_processing"]
        )
        
        assert agent.name == "workflow_agent"
        assert "user_management" in agent.workflow_definitions
        assert agent.status == "idle"
    
    def test_workflow_execution(self):
        """Test workflow execution by agent"""
        agent = WorkflowAgent(
            name="workflow_agent",
            workflow_definitions=["test_workflow"]
        )
        
        workflow_data = {
            "name": "test_workflow",
            "steps": [
                {"name": "step1", "action": "create_user"},
                {"name": "step2", "action": "send_welcome_email"}
            ]
        }
        
        result = agent.execute_workflow(workflow_data)
        
        assert result["executed"] == True
        assert result["workflow_name"] == "test_workflow"
        assert "execution_time" in result
    
    def test_workflow_monitoring(self):
        """Test workflow monitoring and status tracking"""
        agent = WorkflowAgent(
            name="workflow_agent",
            workflow_definitions=["monitored_workflow"]
        )
        
        # Start workflow
        workflow_data = {"name": "monitored_workflow", "steps": []}
        agent.execute_workflow(workflow_data)
        
        # Get status
        status = agent.get_workflow_status("monitored_workflow")
        
        assert status["workflow_name"] == "monitored_workflow"
        assert "status" in status
        assert "progress" in status


class TestAgentPerformance:
    """Test agent system performance"""
    
    def test_concurrent_agent_operations(self):
        """Test concurrent agent operations"""
        import threading
        
        coordinator = AgentCoordinator()
        results = []
        
        def agent_operation(agent_id):
            agent = SwarmAgent(
                name=f"agent_{agent_id}",
                capabilities=["code_generation"],
                worktree_path=f"/tmp/agent_{agent_id}"
            )
            
            coordinator.register_agent(agent)
            
            work_item = {"id": f"work_{agent_id}", "type": "code_generation"}
            result = coordinator.assign_work(work_item)
            results.append(result)
        
        # Run concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=agent_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all operations completed
        assert len(results) == 5
        assert all(result["assigned"] for result in results)
    
    def test_large_scale_agent_coordination(self):
        """Test large scale agent coordination"""
        coordinator = AgentCoordinator()
        
        # Create many agents
        agents = []
        for i in range(50):
            agent = SwarmAgent(
                name=f"agent_{i}",
                capabilities=["code_generation"],
                worktree_path=f"/tmp/agent_{i}"
            )
            agents.append(agent)
        
        # Register all agents
        import time
        start_time = time.time()
        
        for agent in agents:
            coordinator.register_agent(agent)
        
        end_time = time.time()
        
        # Should register 50 agents in reasonable time (< 5 seconds)
        assert (end_time - start_time) < 5.0
        assert coordinator.get_agent_count() == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 