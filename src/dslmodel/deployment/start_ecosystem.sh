#!/bin/bash

# Full OpenTelemetry Ecosystem Startup Script for Swarm Agents
# This script starts the complete observability stack and swarm agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Full OpenTelemetry Ecosystem for Swarm Agents${NC}"
echo "=================================================="

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Set environment variables
export DEPLOYMENT_ENV=${DEPLOYMENT_ENV:-development}
export SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL:-}
export OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-http://localhost:4317}

echo -e "${YELLOW}🔧 Environment: $DEPLOYMENT_ENV${NC}"

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p logs grafana/dashboards grafana/datasources

# Create logs directory if it doesn't exist
touch logs/.gitkeep

# Start the observability stack
echo -e "${YELLOW}🐳 Starting observability stack...${NC}"
docker-compose down --remove-orphans
docker-compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"

check_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf http://localhost:$port > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service is ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $service failed to start${NC}"
    return 1
}

# Check core services
echo -n "Checking OTel Collector (13133)... "
check_service "OTel Collector" 13133

echo -n "Checking Jaeger (16686)... "
check_service "Jaeger" 16686

echo -n "Checking Prometheus (9090)... "
check_service "Prometheus" 9090

echo -n "Checking Grafana (3000)... "
check_service "Grafana" 3000

echo -n "Checking Elasticsearch (9200)... "
check_service "Elasticsearch" 9200

# Install Python dependencies if needed
echo -e "${YELLOW}🐍 Installing Python dependencies...${NC}"
pip install -q opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation opentelemetry-exporter-otlp

# Initialize coordination environment
echo -e "${YELLOW}🎯 Initializing coordination environment...${NC}"
python otel_coordination_cli.py init

# Show access URLs
echo -e "${GREEN}🎉 OpenTelemetry Ecosystem is ready!${NC}"
echo "=================================================="
echo -e "${BLUE}🔗 Access URLs:${NC}"
echo "   • Jaeger UI (Traces):    http://localhost:16686"
echo "   • Grafana (Dashboards):  http://localhost:3000 (admin/admin)"
echo "   • Prometheus (Metrics):  http://localhost:9090"
echo "   • Kibana (Logs):         http://localhost:5601"
echo "   • OTel Collector:        http://localhost:55679 (debug)"
echo "   • AlertManager:          http://localhost:9093"
echo ""

# Offer to start agents
echo -e "${YELLOW}🤖 Would you like to start the swarm agents? (y/n)${NC}"
read -r start_agents

if [[ $start_agents =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Starting swarm agents...${NC}"
    
    # Start agents in background with tmux if available
    if command -v tmux &> /dev/null; then
        echo -e "${BLUE}Starting agents in tmux sessions...${NC}"
        
        # Kill existing sessions if they exist
        tmux kill-session -t swarm-roberts 2>/dev/null || true
        tmux kill-session -t swarm-scrum 2>/dev/null || true
        tmux kill-session -t swarm-lean 2>/dev/null || true
        
        # Start new sessions
        tmux new-session -d -s swarm-roberts "python -m dslmodel.agents.otel.otel_swarm_agent roberts"
        tmux new-session -d -s swarm-scrum "python -m dslmodel.agents.otel.otel_swarm_agent scrum"
        tmux new-session -d -s swarm-lean "python -m dslmodel.agents.otel.otel_swarm_agent lean"
        
        echo -e "${GREEN}✅ Agents started in tmux sessions${NC}"
        echo "   • roberts: tmux attach -t swarm-roberts"
        echo "   • scrum:   tmux attach -t swarm-scrum"
        echo "   • lean:    tmux attach -t swarm-lean"
    else
        echo -e "${YELLOW}tmux not available. Start agents manually:${NC}"
        echo "   python -m dslmodel.agents.otel.otel_swarm_agent roberts"
        echo "   python -m dslmodel.agents.otel.otel_swarm_agent scrum"
        echo "   python -m dslmodel.agents.otel.otel_swarm_agent lean"
    fi
fi

# Show example commands
echo ""
echo -e "${BLUE}🚀 Example Commands:${NC}"
echo "   # Create work item"
echo "   python otel_coordination_cli.py work claim feature 'Sprint 42 Planning' high"
echo ""
echo "   # List work items"  
echo "   python otel_coordination_cli.py work list"
echo ""
echo "   # Generate load for testing"
echo "   for i in {1..10}; do"
echo "     python otel_coordination_cli.py work claim bug \"Bug \$i\" medium &"
echo "   done"
echo ""

# Show shutdown instructions
echo -e "${YELLOW}🛑 To shutdown:${NC}"
echo "   • Stop agents: Ctrl+C or 'tmux kill-server'"
echo "   • Stop stack:  'docker-compose down'"
echo "   • Clean up:    'docker-compose down -v' (removes data)"
echo ""

echo -e "${GREEN}✨ Happy observing! ✨${NC}"