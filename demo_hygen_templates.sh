#!/bin/bash
#
# Demo script showing Hygen template usage for SwarmAgent features
# This demonstrates generating a complete monitoring feature

echo "🚀 SwarmAgent Hygen Templates Demo"
echo "=================================="
echo ""
echo "This demo will generate a complete monitoring feature including:"
echo "- Monitoring agent with state machine"
echo "- Alert workflow with multiple agents"
echo "- Telemetry integration"
echo "- CLI commands"
echo "- FSM mixin for alert handling"
echo ""

# Check if hygen is installed
if ! command -v hygen &> /dev/null; then
    echo "⚠️  Hygen not found. Install with: npm install -g hygen"
    echo "   Or use npx: npx hygen <template> <action>"
    exit 1
fi

# Function to show generated files
show_generated() {
    echo ""
    echo "📁 Generated: $1"
    echo "---"
    if [ -f "$1" ]; then
        head -20 "$1" | sed 's/^/   /'
        echo "   ..."
        echo ""
    fi
}

# 1. Generate Monitoring Agent
echo "1️⃣  Generating Monitoring Agent..."
echo ""

cat << EOF | hygen swarm-agent new
Monitoring
System monitoring and alerting agent
IDLE,MONITORING,ANALYZING,ALERTING,REPORTING
start,monitor,analyze,alert,report
swarmsh.monitoring
y
EOF

show_generated "src/dslmodel/agents/examples/monitoring_agent.py"

# 2. Generate Alert Workflow
echo "2️⃣  Generating Alert Workflow..."
echo ""

cat << EOF | hygen swarm-workflow new
alert
Multi-agent alert handling workflow
monitoring,analyzer,notifier
6
y
y
EOF

show_generated "src/dslmodel/workflows/alert_workflow.py"

# 3. Generate Telemetry Integration
echo "3️⃣  Generating Monitoring Telemetry..."
echo ""

cat << EOF | hygen otel-integration new
Monitoring
OpenTelemetry integration for monitoring metrics
metrics
swarmsh.monitoring
y
y
y
EOF

show_generated "src/dslmodel/otel/monitoring_telemetry.py"

# 4. Generate CLI Commands
echo "4️⃣  Generating Monitor CLI Command..."
echo ""

cat << EOF | hygen cli-command new
monitor
Monitor system resources and alerts
swarm
y



y
n
EOF

show_generated "src/dslmodel/commands/swarm_monitor_command.py"

# 5. Generate Alert FSM Mixin
echo "5️⃣  Generating Alert FSM Mixin..."
echo ""

cat << EOF | hygen fsm-mixin new
Alert
State machine for alert lifecycle management
PENDING,ACKNOWLEDGED,INVESTIGATING,RESOLVED,ESCALATED
y
y
y
y
EOF

show_generated "src/dslmodel/mixins/alert_fsm_mixin.py"

# Summary
echo ""
echo "✅ Demo Complete!"
echo ""
echo "📋 Generated Files Summary:"
echo "  • Agent: src/dslmodel/agents/examples/monitoring_agent.py"
echo "  • Tests: src/dslmodel/agents/tests/test_monitoring_agent.py"
echo "  • Workflow: src/dslmodel/workflows/alert_workflow.py"
echo "  • Telemetry: src/dslmodel/otel/monitoring_telemetry.py"
echo "  • CLI: src/dslmodel/commands/swarm_monitor_command.py"
echo "  • Mixin: src/dslmodel/mixins/alert_fsm_mixin.py"
echo ""
echo "🧪 Test the generated components:"
echo "  python src/dslmodel/agents/examples/monitoring_agent.py"
echo "  python src/dslmodel/workflows/alert_workflow.py --dry-run"
echo "  pytest src/dslmodel/agents/tests/test_monitoring_agent.py"
echo ""
echo "🔧 Next steps:"
echo "  1. Review and customize the generated code"
echo "  2. Update __init__.py files to export new components"
echo "  3. Integrate with existing SwarmAgent ecosystem"
echo "  4. Add specific monitoring logic for your use case"
echo ""

# Create a simple test script
cat > test_generated_monitoring.py << 'EOF'
#!/usr/bin/env python3
"""Test script for generated monitoring components."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Test imports
    print("Testing imports...")
    from src.dslmodel.agents.examples.monitoring_agent import MonitoringAgent
    from src.dslmodel.workflows.alert_workflow import run_alert_workflow
    from src.dslmodel.otel.monitoring_telemetry import MonitoringTelemetry
    from src.dslmodel.mixins.alert_fsm_mixin import AlertFSMMixin
    print("✅ All imports successful!")
    
    # Test agent
    print("\nTesting MonitoringAgent...")
    agent = MonitoringAgent()
    print(f"  State: {agent.state}")
    print(f"  Type: {agent.AGENT_TYPE}")
    
    # Test telemetry
    print("\nTesting MonitoringTelemetry...")
    telemetry = MonitoringTelemetry()
    with telemetry.span("test.operation", {"test": True}):
        time.sleep(0.1)
    print("✅ Telemetry working!")
    
    print("\n🎉 All tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure to run the demo script first!")
except Exception as e:
    print(f"❌ Error: {e}")
EOF

chmod +x test_generated_monitoring.py

echo "📝 Created test script: test_generated_monitoring.py"