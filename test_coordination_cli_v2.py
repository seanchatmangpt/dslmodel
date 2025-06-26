#!/usr/bin/env python3
"""
Test suite for Agent Coordination CLI v2.0
Testing 80/20 implementation with core functionality
"""

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from coordination_cli_v2 import (
    app, 
    generate_agent_id, 
    generate_work_id,
    atomic_json_update,
    Priority,
    WorkStatus
)

runner = CliRunner()

@pytest.fixture
def temp_coordination_dir():
    """Create a temporary coordination directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override the coordination directory
        test_dir = Path(tmpdir) / "test_coordination"
        test_dir.mkdir()
        
        with patch('coordination_cli_v2.COORDINATION_DIR', test_dir):
            with patch('coordination_cli_v2.WORK_CLAIMS_FILE', test_dir / "work_claims.json"):
                with patch('coordination_cli_v2.AGENT_STATUS_FILE', test_dir / "agent_status.json"):
                    with patch('coordination_cli_v2.COORDINATION_LOG_FILE', test_dir / "coordination_log.json"):
                        with patch('coordination_cli_v2.FAST_CLAIMS_FILE', test_dir / "work_claims_fast.jsonl"):
                            yield test_dir

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_generate_agent_id(self):
        """Test agent ID generation with nanosecond precision"""
        id1 = generate_agent_id()
        time.sleep(0.001)  # Sleep 1ms to ensure different timestamp
        id2 = generate_agent_id()
        
        assert id1.startswith("agent_")
        assert id2.startswith("agent_")
        assert id1 != id2  # Should be unique
        assert len(id1) > 15  # Should have nanosecond precision
        
    def test_generate_work_id(self):
        """Test work ID generation with nanosecond precision"""
        id1 = generate_work_id()
        time.sleep(0.001)
        id2 = generate_work_id()
        
        assert id1.startswith("work_")
        assert id2.startswith("work_")
        assert id1 != id2
        assert len(id1) > 14
        
    def test_atomic_json_update(self, temp_coordination_dir):
        """Test atomic JSON file updates with locking"""
        test_file = temp_coordination_dir / "test_atomic.json"
        
        # Test creating new file
        def add_item(data):
            data.append({"id": 1, "value": "test"})
            return data
            
        assert atomic_json_update(test_file, add_item)
        
        with open(test_file, 'r') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["value"] == "test"
        
        # Test updating existing file
        def update_item(data):
            data[0]["value"] = "updated"
            return data
            
        assert atomic_json_update(test_file, update_item)
        
        with open(test_file, 'r') as f:
            data = json.load(f)
        assert data[0]["value"] == "updated"

class TestClaimCommand:
    """Test the claim command"""
    
    def test_claim_basic(self, temp_coordination_dir):
        """Test basic work claiming"""
        result = runner.invoke(app, ["claim", "feature", "Test feature", "--fast=false"])
        assert result.exit_code == 0
        assert "SUCCESS" in result.stdout
        assert "work_" in result.stdout
        
        # Check file was created
        claims_file = temp_coordination_dir / "work_claims.json"
        assert claims_file.exists()
        
        with open(claims_file, 'r') as f:
            claims = json.load(f)
        assert len(claims) == 1
        assert claims[0]["work_type"] == "feature"
        assert claims[0]["description"] == "Test feature"
        assert claims[0]["priority"] == "medium"
        assert claims[0]["status"] == "active"
        
    def test_claim_with_priority(self, temp_coordination_dir):
        """Test claiming with custom priority"""
        result = runner.invoke(app, [
            "claim", "bug", "Critical bug", 
            "--priority", "critical",
            "--team", "backend",
            "--fast=false"
        ])
        assert result.exit_code == 0
        
        claims_file = temp_coordination_dir / "work_claims.json"
        with open(claims_file, 'r') as f:
            claims = json.load(f)
        assert claims[0]["priority"] == "critical"
        assert claims[0]["team"] == "backend"
        
    def test_claim_fast_path(self, temp_coordination_dir):
        """Test fast-path claiming (JSONL append)"""
        result = runner.invoke(app, ["claim", "task", "Fast task"])
        assert result.exit_code == 0
        assert "Fast-path" in result.stdout
        
        # Check JSONL file
        fast_file = temp_coordination_dir / "work_claims_fast.jsonl"
        assert fast_file.exists()
        
        with open(fast_file, 'r') as f:
            line = f.readline()
            claim = json.loads(line)
        assert claim["work_type"] == "task"
        assert claim["description"] == "Fast task"
        
    def test_claim_multiple(self, temp_coordination_dir):
        """Test claiming multiple work items"""
        # Claim 3 items
        for i in range(3):
            result = runner.invoke(app, [
                "claim", f"task{i}", f"Task {i}", "--fast=false"
            ])
            assert result.exit_code == 0
            
        claims_file = temp_coordination_dir / "work_claims.json"
        with open(claims_file, 'r') as f:
            claims = json.load(f)
        assert len(claims) == 3

class TestProgressCommand:
    """Test the progress command"""
    
    def test_progress_update(self, temp_coordination_dir):
        """Test updating work progress"""
        # First claim work
        result = runner.invoke(app, ["claim", "feature", "Test", "--fast=false"])
        assert result.exit_code == 0
        
        # Extract work ID from output
        output_lines = result.stdout.split('\n')
        work_id_line = [line for line in output_lines if "work_" in line][0]
        work_id = work_id_line.split("work_")[1].split()[0]
        
        # Update progress
        result = runner.invoke(app, ["progress", work_id, "75"])
        assert result.exit_code == 0
        assert "75%" in result.stdout
        
        # Verify update
        claims_file = temp_coordination_dir / "work_claims.json"
        with open(claims_file, 'r') as f:
            claims = json.load(f)
        assert claims[0]["progress"] == 75
        assert claims[0]["status"] == "in_progress"
        
    def test_progress_with_env_var(self, temp_coordination_dir):
        """Test progress update using environment variable"""
        # Claim work
        result = runner.invoke(app, ["claim", "bug", "Fix bug", "--fast=false"])
        
        # Extract work ID
        output_lines = result.stdout.split('\n')
        work_id_line = [line for line in output_lines if "work_" in line][0]
        work_id = work_id_line.split("work_")[1].split()[0]
        
        # Set environment variable
        with patch.dict(os.environ, {"CURRENT_WORK_ITEM": work_id}):
            result = runner.invoke(app, ["progress", "50"])
            assert result.exit_code == 0
            assert "50%" in result.stdout
            
    def test_progress_no_work_id(self):
        """Test progress without work ID"""
        result = runner.invoke(app, ["progress", "50"])
        assert result.exit_code == 1
        assert "No work item ID" in result.stdout

class TestCompleteCommand:
    """Test the complete command"""
    
    def test_complete_work(self, temp_coordination_dir):
        """Test completing work"""
        # Claim work
        result = runner.invoke(app, ["claim", "feature", "Test", "--fast=false"])
        
        # Extract work ID
        output_lines = result.stdout.split('\n')
        work_id_line = [line for line in output_lines if "work_" in line][0]
        work_id = work_id_line.split("work_")[1].split()[0]
        
        # Complete work
        result = runner.invoke(app, [
            "complete", work_id, 
            "--result", "success",
            "--velocity", "8"
        ])
        assert result.exit_code == 0
        assert "Completed" in result.stdout
        assert "8 points" in result.stdout
        
        # Verify completion
        claims_file = temp_coordination_dir / "work_claims.json"
        with open(claims_file, 'r') as f:
            claims = json.load(f)
        assert claims[0]["status"] == "completed"
        assert claims[0]["result"] == "success"
        assert claims[0]["velocity_points"] == 8
        
        # Check log file
        log_file = temp_coordination_dir / "coordination_log.json"
        assert log_file.exists()
        with open(log_file, 'r') as f:
            logs = json.load(f)
        assert len(logs) == 1
        assert logs[0]["velocity_points"] == 8

class TestDashboardCommand:
    """Test the dashboard command"""
    
    def test_dashboard_empty(self, temp_coordination_dir):
        """Test dashboard with no work items"""
        result = runner.invoke(app, ["dashboard", "--fast=false"])
        assert result.exit_code == 0
        assert "COORDINATION DASHBOARD" in result.stdout
        
    def test_dashboard_with_items(self, temp_coordination_dir):
        """Test dashboard with work items"""
        # Create some work items
        for i in range(3):
            runner.invoke(app, ["claim", f"task{i}", f"Task {i}", "--fast=false"])
            
        # Complete one item
        claims_file = temp_coordination_dir / "work_claims.json"
        with open(claims_file, 'r') as f:
            claims = json.load(f)
        work_id = claims[0]["work_item_id"]
        
        runner.invoke(app, ["complete", work_id, "--velocity", "5"])
        
        # Show dashboard
        result = runner.invoke(app, ["dashboard", "--fast=false"])
        assert result.exit_code == 0
        assert "Active: 2" in result.stdout
        assert "Completed: 1" in result.stdout
        assert "Total Velocity: 5 points" in result.stdout
        
    def test_dashboard_fast_path(self, temp_coordination_dir):
        """Test fast-path dashboard"""
        # Create fast-path items
        for i in range(2):
            runner.invoke(app, ["claim", f"fast{i}", f"Fast {i}"])
            
        result = runner.invoke(app, ["dashboard"])
        assert result.exit_code == 0
        assert "Fast-path active items: 2" in result.stdout

class TestListWorkCommand:
    """Test the list-work command"""
    
    def test_list_work_empty(self, temp_coordination_dir):
        """Test listing with no work"""
        result = runner.invoke(app, ["list-work"])
        assert result.exit_code == 0
        assert "No work items found" in result.stdout
        
    def test_list_work_with_filters(self, temp_coordination_dir):
        """Test listing with filters"""
        # Create items with different teams and statuses
        runner.invoke(app, ["claim", "task1", "Frontend task", 
                          "--team", "frontend", "--fast=false"])
        runner.invoke(app, ["claim", "task2", "Backend task", 
                          "--team", "backend", "--fast=false"])
        
        # Update one to in-progress
        runner.invoke(app, ["progress", "", "50"])  # Will fail, but that's ok
        
        # Filter by team
        result = runner.invoke(app, ["list-work", "--team", "frontend"])
        assert result.exit_code == 0
        assert "Frontend task" in result.stdout
        
        # Filter by status
        result = runner.invoke(app, ["list-work", "--status", "active"])
        assert result.exit_code == 0

class TestOptimizeCommand:
    """Test the optimize command"""
    
    def test_optimize_archives_completed(self, temp_coordination_dir):
        """Test archiving completed work items"""
        # Create and complete several items
        for i in range(5):
            runner.invoke(app, ["claim", f"task{i}", f"Task {i}", "--fast=false"])
            
        # Complete 3 items
        claims_file = temp_coordination_dir / "work_claims.json"
        with open(claims_file, 'r') as f:
            claims = json.load(f)
            
        for i in range(3):
            work_id = claims[i]["work_item_id"]
            runner.invoke(app, ["complete", work_id])
            
        # Run optimize
        result = runner.invoke(app, ["optimize"])
        assert result.exit_code == 0
        assert "Archived 3 completed items" in result.stdout
        assert "Active items: 2" in result.stdout
        
        # Check archive was created
        archive_dir = temp_coordination_dir / "archived_claims"
        assert archive_dir.exists()
        archive_files = list(archive_dir.glob("completed_*.json"))
        assert len(archive_files) == 1
        
        # Verify only active items remain
        with open(claims_file, 'r') as f:
            remaining = json.load(f)
        assert len(remaining) == 2
        assert all(item["status"] != "completed" for item in remaining)

class TestIntegrationScenarios:
    """Test end-to-end scenarios"""
    
    def test_full_workflow(self, temp_coordination_dir):
        """Test complete workflow: claim -> progress -> complete"""
        # 1. Claim work
        result = runner.invoke(app, [
            "claim", "feature", "User authentication",
            "--priority", "high",
            "--team", "security",
            "--fast=false"
        ])
        assert result.exit_code == 0
        
        # Extract work ID
        output_lines = result.stdout.split('\n')
        work_id_line = [line for line in output_lines if "work_" in line][0]
        work_id = work_id_line.split("work_")[1].split()[0]
        
        # 2. Update progress multiple times
        for progress in [25, 50, 75, 90]:
            result = runner.invoke(app, ["progress", work_id, str(progress)])
            assert result.exit_code == 0
            
        # 3. Complete work
        result = runner.invoke(app, [
            "complete", work_id,
            "--result", "success",
            "--velocity", "13"
        ])
        assert result.exit_code == 0
        
        # 4. Check dashboard
        result = runner.invoke(app, ["dashboard"])
        assert result.exit_code == 0
        assert "Completed: 1" in result.stdout
        assert "13 points" in result.stdout
        
    def test_concurrent_claims_simulation(self, temp_coordination_dir):
        """Test multiple agents claiming work (simulated)"""
        # Simulate different agents by setting AGENT_ID
        agents = ["agent_alpha", "agent_beta", "agent_gamma"]
        
        for i, agent in enumerate(agents):
            with patch.dict(os.environ, {"AGENT_ID": agent}):
                result = runner.invoke(app, [
                    "claim", f"task{i}", f"Task for {agent}",
                    "--team", f"team{i % 2}",
                    "--fast=false"
                ])
                assert result.exit_code == 0
                assert agent in result.stdout
                
        # Verify all claims were recorded
        claims_file = temp_coordination_dir / "work_claims.json"
        with open(claims_file, 'r') as f:
            claims = json.load(f)
        assert len(claims) == 3
        assert set(c["agent_id"] for c in claims) == set(agents)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])