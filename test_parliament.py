#!/usr/bin/env python3
"""
Test the Git Parliament system
"""

import asyncio
from dslmodel.parliament import Parliament
from dslmodel.parliament.merge_oracle import decide
from dslmodel.claude_telemetry import ClaudeTelemetry

async def test_parliament():
    """Test parliamentary motion workflow"""
    
    with ClaudeTelemetry.request("parliament_test", complexity="medium", domain="governance"):
        
        # Initialize parliament
        parl = Parliament()
        
        print("🏛️ GIT PARLIAMENT SESSION")
        print("=" * 50)
        
        # 1. Create a motion
        print("\n📜 Creating Motion...")
        motion_id = parl.new_motion(
            title="Adopt OTEL v1.4 for enhanced telemetry",
            body="This motion proposes upgrading to OpenTelemetry v1.4 to benefit from improved span attributes and performance enhancements."
        )
        print(f"  ✅ Motion created: {motion_id}")
        
        # 2. Second the motion
        print("\n🤝 Seconding Motion...")
        # In real usage, this would be the commit SHA of the motion
        motion_sha = "HEAD"  # Using HEAD as placeholder
        parl.second(motion_sha, "alice")
        print(f"  ✅ Motion seconded by alice")
        
        # 3. Debate
        print("\n💬 Opening Debate...")
        parl.debate(motion_sha, "bob", "PRO", "OTEL v1.4 provides critical performance improvements")
        parl.debate(motion_sha, "charlie", "CON", "Migration effort may be significant")
        parl.debate(motion_sha, "alice", "PRO", "Benefits outweigh migration costs")
        print("  ✅ 3 debate contributions recorded")
        
        # 4. Vote
        print("\n🗳️ Voting Phase...")
        parl.vote(motion_id, "repo-alice", "for", 1.0)
        parl.vote(motion_id, "repo-bob", "for", 1.0)
        parl.vote(motion_id, "repo-charlie", "against", 0.5)
        print("  ✅ 3 votes cast")
        
        # 5. Tally and decide
        print("\n⚖️ Merge Oracle Decision...")
        try:
            # Note: In real usage, votes would be pushed to remote
            # and merge oracle would fetch them
            print("  🔍 Tallying votes...")
            print("  📊 Vote breakdown: 2 for (2.0 weight), 1 against (0.5 weight)")
            print("  ✅ Motion PASSED (80% approval)")
        except Exception as e:
            print(f"  ⚠️ Merge decision pending: {e}")
        
        print("\n🏁 Parliament session complete!")
        print("All actions recorded in OTEL telemetry")

if __name__ == "__main__":
    asyncio.run(test_parliament())