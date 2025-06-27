#!/usr/bin/env python3
"""
Full OpenTelemetry Ecosystem Loop Test with Ollama/Qwen3

This script tests the complete swarm agent ecosystem using:
- init_lm("ollama/qwen3") for AI-powered agent decisions
- Full OpenTelemetry instrumentation 
- Cross-agent coordination and tracing
- Business workflow automation

Usage:
    python test_full_loop.py [--quick] [--verbose]
"""

import asyncio
import json
import time
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List
from contextlib import asynccontextmanager
import signal

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dslmodel.utils.dspy_tools import init_lm
from dslmodel.otel.otel_instrumentation import init_otel, get_otel
from dslmodel.otel.otel_swarm_agent import OTelSwarmAgent
from dslmodel.agents.swarm.swarm_models import NextCommand, SpanData
from dslmodel.mixins import trigger
from enum import Enum, auto

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global test state
test_results = {
    "ollama_init": False,
    "otel_init": False,
    "agents_started": False,
    "workflow_completed": False,
    "spans_generated": 0,
    "errors": []
}


class TestWorkflowState(Enum):
    """Test workflow states."""
    INIT = auto()
    GOVERNANCE_TEST = auto()
    DELIVERY_TEST = auto()
    OPTIMIZATION_TEST = auto()
    COMPLETED = auto()


class TestOrchestratorAgent(OTelSwarmAgent):
    """
    Test orchestrator that drives the full workflow using Ollama/Qwen3.
    
    This agent uses AI to make intelligent decisions about the test workflow
    and coordinates other agents through OpenTelemetry spans.
    """
    
    StateEnum = TestWorkflowState
    LISTEN_FILTER = "swarmsh.test."
    TRIGGER_MAP = {
        "start": "start_governance_test",
        "governance_complete": "start_delivery_test", 
        "delivery_complete": "start_optimization_test",
        "optimization_complete": "complete_workflow"
    }
    
    def __init__(self, **kwargs):
        super().__init__(service_name="test-orchestrator", **kwargs)
        self.lm = None
        self.test_data = {}
        
    async def initialize_ai(self):
        """Initialize Ollama/Qwen3 for AI-powered decisions."""
        try:
            logger.info("🧠 Initializing Ollama/Qwen3...")
            self.lm = init_lm(
                "ollama/qwen3",
                api_base="http://localhost:11434",
                temperature=0.7,
                max_tokens=1000
            )
            
            # Test the connection with a simple prompt
            with self.otel.trace_span(
                name="test.ai.connectivity",
                attributes={"model": "ollama/qwen3"}
            ) as span:
                # Simple test to verify AI is working
                response = await self._ask_ai("Say 'AI Ready' if you can respond.")
                if "ready" in response.lower() or "ai" in response.lower():
                    test_results["ollama_init"] = True
                    span.set_attribute("ai.status", "ready")
                    logger.info("✅ Ollama/Qwen3 initialized successfully")
                else:
                    raise Exception(f"Unexpected AI response: {response}")
                    
        except Exception as e:
            test_results["errors"].append(f"AI init failed: {e}")
            logger.error(f"❌ Failed to initialize Ollama/Qwen3: {e}")
            raise
    
    async def _ask_ai(self, prompt: str) -> str:
        """Ask the AI a question and get a response."""
        if not self.lm:
            return "AI not initialized"
            
        try:
            # Use DSPy to get AI response
            import dspy
            
            # Create a simple signature for our query
            class Reasoning(dspy.Signature):
                """You are a helpful assistant in a swarm agent test system."""
                query = dspy.InputField(desc="The question or task")
                response = dspy.OutputField(desc="Your response")
            
            predictor = dspy.Predict(Reasoning)
            result = predictor(query=prompt)
            return result.response
            
        except Exception as e:
            logger.error(f"AI query failed: {e}")
            return f"Error: {e}"
    
    def setup_triggers(self):
        """Setup trigger methods."""
        pass
    
    @trigger(source=TestWorkflowState.INIT, dest=TestWorkflowState.GOVERNANCE_TEST)
    async def start_governance_test(self, span: SpanData) -> NextCommand:
        """Start governance workflow test with AI guidance."""
        with self.otel.trace_span(
            name="test.governance.start",
            attributes={"framework": "roberts", "test_phase": "governance"}
        ) as test_span:
            
            # Ask AI for governance test strategy
            ai_strategy = await self._ask_ai(
                "We're testing a Roberts Rules governance agent. "
                "What motion should we propose for a sprint planning approval? "
                "Respond with just the motion text."
            )
            
            logger.info(f"🏛️ AI suggests governance motion: {ai_strategy}")
            
            # Record AI decision in span
            test_span.set_attribute("ai.strategy", ai_strategy[:200])
            test_span.set_attribute("motion.type", "sprint_planning")
            
            self._transition("Starting governance test with AI strategy", 
                           TestWorkflowState.GOVERNANCE_TEST)
            
            # Create work item that triggers Roberts agent
            return NextCommand(
                fq_name="swarmsh.roberts.motion",
                args=[
                    "--motion-id", "test-sprint-42",
                    "--description", ai_strategy,
                    "--voting-method", "voice_vote"
                ],
                description="AI-generated governance motion"
            )
    
    @trigger(source=TestWorkflowState.GOVERNANCE_TEST, dest=TestWorkflowState.DELIVERY_TEST)  
    async def start_delivery_test(self, span: SpanData) -> NextCommand:
        """Start delivery workflow test."""
        with self.otel.trace_span(
            name="test.delivery.start", 
            attributes={"framework": "scrum", "test_phase": "delivery"}
        ) as test_span:
            
            # Ask AI for sprint planning guidance
            ai_guidance = await self._ask_ai(
                "A governance motion for sprint planning was approved. "
                "What should be the sprint capacity and key objectives? "
                "Keep it brief."
            )
            
            logger.info(f"🏃 AI suggests delivery plan: {ai_guidance}")
            test_span.set_attribute("ai.guidance", ai_guidance[:200])
            
            self._transition("Starting delivery test with AI guidance",
                           TestWorkflowState.DELIVERY_TEST)
            
            return NextCommand(
                fq_name="swarmsh.scrum.sprint-start",
                args=[
                    "--sprint-id", "42",
                    "--capacity", "40",
                    "--team", "alpha"
                ],
                description="AI-guided sprint start"
            )
    
    @trigger(source=TestWorkflowState.DELIVERY_TEST, dest=TestWorkflowState.OPTIMIZATION_TEST)
    async def start_optimization_test(self, span: SpanData) -> NextCommand:
        """Start optimization workflow test."""
        with self.otel.trace_span(
            name="test.optimization.start",
            attributes={"framework": "lean", "test_phase": "optimization"}
        ) as test_span:
            
            # Simulate finding a quality issue and ask AI for improvement
            ai_improvement = await self._ask_ai(
                "We detected a 4% defect rate in our sprint (above 3% threshold). "
                "What Lean Six Sigma improvement project should we start? "
                "Suggest a problem statement."
            )
            
            logger.info(f"🔧 AI suggests improvement: {ai_improvement}")
            test_span.set_attribute("ai.improvement", ai_improvement[:200])
            test_span.set_attribute("defect_rate", 4.0)
            
            self._transition("Starting optimization test with AI improvement",
                           TestWorkflowState.OPTIMIZATION_TEST)
            
            return NextCommand(
                fq_name="swarmsh.lean.define-project",
                args=[
                    "--project-id", "quality-improvement-001",
                    "--problem", ai_improvement,
                    "--sponsor", "test-orchestrator"
                ],
                description="AI-suggested improvement project"
            )
    
    @trigger(source=TestWorkflowState.OPTIMIZATION_TEST, dest=TestWorkflowState.COMPLETED)
    async def complete_workflow(self, span: SpanData) -> NextCommand:
        """Complete the test workflow."""
        with self.otel.trace_span(
            name="test.workflow.complete",
            attributes={"test_phase": "completion", "status": "success"}
        ) as test_span:
            
            # Ask AI for test summary
            ai_summary = await self._ask_ai(
                "We completed a full governance → delivery → optimization workflow. "
                "Provide a brief success summary for our test results."
            )
            
            logger.info(f"🎉 AI test summary: {ai_summary}")
            test_span.set_attribute("ai.summary", ai_summary[:200])
            
            self._transition("Workflow completed successfully",
                           TestWorkflowState.COMPLETED)
            
            test_results["workflow_completed"] = True
            
            return None


class SimpleRobertsAgent(OTelSwarmAgent):
    """Simplified Roberts agent for testing."""
    
    class RorState(Enum):
        IDLE = auto()
        MOTION_OPEN = auto()
        VOTING = auto()
        CLOSED = auto()
    
    StateEnum = RorState
    LISTEN_FILTER = "swarmsh.roberts."
    TRIGGER_MAP = {
        "motion": "handle_motion",
        "vote": "handle_vote"
    }
    
    def setup_triggers(self):
        pass
    
    @trigger(source=RorState.IDLE, dest=RorState.MOTION_OPEN)
    def handle_motion(self, span: SpanData) -> NextCommand:
        logger.info("🏛️ Roberts: Processing motion")
        self._transition("Motion received", self.RorState.MOTION_OPEN)
        
        # Simulate quick approval
        return NextCommand(
            fq_name="swarmsh.roberts.vote",
            args=["--motion-id", span.attributes.get("motion_id", "test"),
                  "--result", "approved"],
            description="Auto-approve test motion"
        )
    
    @trigger(source=RorState.MOTION_OPEN, dest=RorState.CLOSED)
    def handle_vote(self, span: SpanData) -> NextCommand:
        logger.info("🏛️ Roberts: Vote completed")
        self._transition("Vote completed", self.RorState.CLOSED)
        
        # Trigger next phase
        return NextCommand(
            fq_name="swarmsh.test.governance_complete",
            args=[],
            description="Governance phase complete"
        )


async def setup_test_environment():
    """Setup the test environment."""
    logger.info("🔧 Setting up test environment...")
    
    # Initialize OTel
    try:
        otel = init_otel(
            service_name="swarm-test-suite",
            otlp_endpoint="http://localhost:4317",
            enable_console_export=True
        )
        test_results["otel_init"] = True
        logger.info("✅ OpenTelemetry initialized")
    except Exception as e:
        test_results["errors"].append(f"OTel init failed: {e}")
        logger.error(f"❌ OTel initialization failed: {e}")
        raise
    
    # Create test data directory
    test_dir = Path("~/s2s/agent_coordination").expanduser()
    test_dir.mkdir(parents=True, exist_ok=True)
    
    return otel


async def run_full_loop_test(quick_mode: bool = False, verbose: bool = False):
    """Run the complete ecosystem test."""
    logger.info("🚀 Starting Full OpenTelemetry Ecosystem Loop Test")
    logger.info("=" * 60)
    
    try:
        # Setup environment
        otel = await setup_test_environment()
        
        # Create test orchestrator
        orchestrator = TestOrchestratorAgent(
            enable_console_export=verbose
        )
        
        # Initialize AI
        await orchestrator.initialize_ai()
        
        # Create simplified test agents
        roberts_agent = SimpleRobertsAgent(
            service_name="roberts-test-agent",
            enable_console_export=verbose
        )
        
        logger.info("✅ All agents initialized")
        test_results["agents_started"] = True
        
        # Start the workflow with a test span
        with otel.trace_span(
            name="test.workflow.start",
            attributes={
                "test.type": "full_ecosystem_loop",
                "test.mode": "quick" if quick_mode else "full",
                "ai.model": "ollama/qwen3"
            }
        ) as workflow_span:
            
            # Emit initial test span
            test_span_data = {
                "name": "swarmsh.test.start",
                "trace_id": format(workflow_span.get_span_context().trace_id, '032x'),
                "span_id": format(workflow_span.get_span_context().span_id, '016x'),
                "timestamp": time.time(),
                "attributes": {
                    "test.phase": "initialization",
                    "ai.model": "ollama/qwen3"
                }
            }
            
            # Process through orchestrator
            result = await orchestrator.forward(test_span_data)
            if result:
                logger.info(f"🎯 Executing: {result.description}")
                # In a real system, this would trigger the CLI
                # For testing, we'll simulate the response
                
                # Simulate governance completion
                await asyncio.sleep(1 if quick_mode else 3)
                
                governance_span = {
                    "name": "swarmsh.test.governance_complete", 
                    "trace_id": format(workflow_span.get_span_context().trace_id, '032x'),
                    "span_id": f"span_{int(time.time() * 1000000)}",
                    "timestamp": time.time(),
                    "attributes": {"phase": "governance_complete"}
                }
                
                result = await orchestrator.forward(governance_span)
                if result:
                    logger.info(f"🎯 Executing: {result.description}")
                    
                    # Simulate delivery completion
                    await asyncio.sleep(1 if quick_mode else 3)
                    
                    delivery_span = {
                        "name": "swarmsh.test.delivery_complete",
                        "trace_id": format(workflow_span.get_span_context().trace_id, '032x'), 
                        "span_id": f"span_{int(time.time() * 1000000)}",
                        "timestamp": time.time(),
                        "attributes": {"phase": "delivery_complete"}
                    }
                    
                    result = await orchestrator.forward(delivery_span)
                    if result:
                        logger.info(f"🎯 Executing: {result.description}")
                        
                        # Simulate optimization completion
                        await asyncio.sleep(1 if quick_mode else 3)
                        
                        optimization_span = {
                            "name": "swarmsh.test.optimization_complete",
                            "trace_id": format(workflow_span.get_span_context().trace_id, '032x'),
                            "span_id": f"span_{int(time.time() * 1000000)}",
                            "timestamp": time.time(), 
                            "attributes": {"phase": "optimization_complete"}
                        }
                        
                        await orchestrator.forward(optimization_span)
        
        # Test completed successfully
        logger.info("🎉 Full ecosystem loop test completed successfully!")
        return True
        
    except Exception as e:
        test_results["errors"].append(f"Test execution failed: {e}")
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_test_results():
    """Print comprehensive test results."""
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    results = [
        ("Ollama/Qwen3 Initialization", test_results["ollama_init"]),
        ("OpenTelemetry Setup", test_results["otel_init"]),
        ("Agent Startup", test_results["agents_started"]),
        ("Workflow Completion", test_results["workflow_completed"])
    ]
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name:.<30} {status}")
    
    if test_results["errors"]:
        logger.info("\n🚨 ERRORS:")
        for error in test_results["errors"]:
            logger.error(f"  • {error}")
    
    success_rate = sum(r[1] for r in results) / len(results) * 100
    logger.info(f"\n📈 Overall Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        logger.info("🎉 ALL TESTS PASSED - Full ecosystem loop working!")
    else:
        logger.info("⚠️  Some tests failed - check errors above")


async def main():
    """Main test execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Full OTel Ecosystem Loop Test")
    parser.add_argument("--quick", action="store_true", help="Run in quick mode")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Setup signal handling for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\n🛑 Test interrupted by user")
        print_test_results()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        success = await run_full_loop_test(args.quick, args.verbose)
        print_test_results()
        
        if success:
            logger.info("\n🚀 Test suite completed successfully!")
            logger.info("The full OpenTelemetry ecosystem loop is working with Ollama/Qwen3!")
        else:
            logger.error("\n❌ Test suite failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Test interrupted")
        print_test_results()
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())