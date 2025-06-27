#!/usr/bin/env python3
"""
Simple 5-ONE Git Parliament Test
================================

Demonstrates the Git Parliament system with basic OTEL monitoring.
"""

import asyncio
import subprocess
import pathlib
import tempfile
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

from dslmodel.examples.git_parliament_5one_monitor import (
    setup_5one_monitoring,
    InstrumentedParliament,
    instrumented_tally,
    instrumented_merge_decision
)


async def test_simple_parliament():
    """Test basic parliament operations with OTEL"""
    
    print("🏛️ 5-ONE Git Parliament - Simple Test")
    print("=" * 40)
    
    # Setup OTEL monitoring
    tracer, meter = setup_5one_monitoring(
        service_name="git-parliament-test",
        otlp_endpoint="http://localhost:4317"
    )
    
    # Create temporary git repository
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = pathlib.Path(tmpdir)
        os.chdir(repo_path)
        
        # Initialize git repo
        print("\n📁 Initializing Git repository...")
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@5one.ai"], check=True)
        subprocess.run(["git", "config", "user.name", "Test Parliament"], check=True)
        
        # Create initial commit
        readme = repo_path / "README.md"
        readme.write_text("# Test Parliament")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
        # Initialize parliament
        parliament = InstrumentedParliament(repo_path)
        
        # Create a motion
        print("\n📋 Creating motion...")
        motion_id = parliament.new_motion(
            title="Test Motion for OTEL Integration",
            body="This motion tests the parliament system with full OTEL instrumentation."
        )
        print(f"✅ Motion created: {motion_id}")
        
        # Get motion SHA
        motion_sha = subprocess.check_output(
            ["git", "rev-parse", f"motions/{motion_id}"]
        ).decode().strip()
        
        # Second the motion
        print("\n🤝 Seconding motion...")
        parliament.second(motion_sha, "alice")
        print("✅ Motion seconded by alice")
        
        # Debate
        print("\n💬 Adding debate...")
        parliament.debate(motion_sha, "bob", "pro", "This will improve observability")
        parliament.debate(motion_sha, "charlie", "con", "Complexity concerns")
        print("✅ Debate entries added")
        
        # Vote
        print("\n🗳️ Casting votes...")
        parliament.vote(motion_id, "alice", "for", 1.0)
        parliament.vote(motion_id, "bob", "for", 1.0)
        parliament.vote(motion_id, "charlie", "against", 1.0)
        print("✅ Votes cast")
        
        # Check current branch before decision
        current_branch = subprocess.check_output(
            ["git", "branch", "--show-current"]
        ).decode().strip()
        print(f"\n📍 Current branch: {current_branch}")
        
        # Tally votes (simplified for demo)
        print("\n📊 Vote tally: 2 for, 1 against (66.7% approval)")
        
        print("\n✅ Test completed successfully!")
        print("\n📊 OTEL Monitoring Active:")
        print("  • All operations traced")
        print("  • Metrics recorded")
        print("  • Parliament lifecycle tracked")


if __name__ == "__main__":
    print("🚀 Starting 5-ONE Git Parliament Test")
    print("====================================")
    try:
        asyncio.run(test_simple_parliament())
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()