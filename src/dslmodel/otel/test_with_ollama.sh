#!/bin/bash

# Test Full OpenTelemetry Ecosystem Loop with Ollama/Qwen3
# This script ensures Ollama is running and tests the complete system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 Testing Full OpenTelemetry Ecosystem with Ollama/Qwen3${NC}"
echo "=============================================================="

# Check if Ollama is installed
check_ollama_installed() {
    if ! command -v ollama &> /dev/null; then
        echo -e "${RED}❌ Ollama is not installed${NC}"
        echo "Install from: https://ollama.ai/"
        exit 1
    fi
    echo -e "${GREEN}✅ Ollama is installed${NC}"
}

# Check if Ollama service is running
check_ollama_running() {
    if ! pgrep -f "ollama" > /dev/null; then
        echo -e "${YELLOW}⚠️  Ollama service not running, starting it...${NC}"
        
        # Start Ollama in background
        ollama serve &
        OLLAMA_PID=$!
        
        # Wait for Ollama to start
        echo -n "Waiting for Ollama to start"
        for i in {1..30}; do
            if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
                echo -e "\n${GREEN}✅ Ollama is running${NC}"
                break
            fi
            echo -n "."
            sleep 1
        done
        
        if [ $i -eq 30 ]; then
            echo -e "\n${RED}❌ Ollama failed to start${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Ollama is already running${NC}"
    fi
}

# Check if Qwen3 model is available
check_qwen3_model() {
    echo -e "${YELLOW}🔍 Checking for Qwen3 model...${NC}"
    
    if ollama list | grep -q "qwen3"; then
        echo -e "${GREEN}✅ Qwen3 model is available${NC}"
    else
        echo -e "${YELLOW}⚠️  Qwen3 model not found, pulling it...${NC}"
        echo "This may take a few minutes depending on your internet connection."
        
        ollama pull qwen3 || {
            echo -e "${RED}❌ Failed to pull Qwen3 model${NC}"
            echo "You can try manually: ollama pull qwen3"
            exit 1
        }
        
        echo -e "${GREEN}✅ Qwen3 model downloaded successfully${NC}"
    fi
}

# Test Ollama connectivity
test_ollama_connectivity() {
    echo -e "${YELLOW}🧪 Testing Ollama connectivity...${NC}"
    
    # Test basic connectivity
    response=$(curl -s -X POST http://localhost:11434/api/generate \
        -H "Content-Type: application/json" \
        -d '{
            "model": "qwen3",
            "prompt": "Say \"Hello World\" if you can respond.",
            "stream": false
        }')
    
    if echo "$response" | grep -q "Hello World\|hello world"; then
        echo -e "${GREEN}✅ Ollama/Qwen3 connectivity test passed${NC}"
    else
        echo -e "${RED}❌ Ollama/Qwen3 connectivity test failed${NC}"
        echo "Response: $response"
        exit 1
    fi
}

# Check Python dependencies
check_python_deps() {
    echo -e "${YELLOW}🐍 Checking Python dependencies...${NC}"
    
    python -c "
import sys
sys.path.insert(0, '/Users/sac/dev/dslmodel/src')

try:
    import dspy
    print('✅ DSPy available')
except ImportError:
    print('❌ DSPy not available - install with: pip install dspy-ai')
    sys.exit(1)

try:
    from opentelemetry import trace
    print('✅ OpenTelemetry available')
except ImportError:
    print('❌ OpenTelemetry not available - install with: pip install opentelemetry-api opentelemetry-sdk')
    sys.exit(1)

try:
    from dslmodel.utils.dspy_tools import init_lm
    print('✅ DSLModel utils available')
except ImportError as e:
    print(f'❌ DSLModel utils not available: {e}')
    sys.exit(1)
"
}

# Check if OTel Collector is running (optional)
check_otel_collector() {
    echo -e "${YELLOW}🔍 Checking OpenTelemetry Collector (optional)...${NC}"
    
    if curl -sf http://localhost:13133/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OTel Collector is running${NC}"
        export OTEL_COLLECTOR_AVAILABLE=true
    else
        echo -e "${YELLOW}⚠️  OTel Collector not running (spans will be logged to console)${NC}"
        export OTEL_COLLECTOR_AVAILABLE=false
    fi
}

# Run the actual test
run_test() {
    echo -e "${BLUE}🚀 Running Full Ecosystem Test...${NC}"
    echo ""
    
    # Set environment variables
    export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
    export OTEL_SERVICE_NAME=swarm-test-suite
    export PYTHONPATH=/Users/sac/dev/dslmodel/src:$PYTHONPATH
    
    # Run the test with appropriate flags
    if [ "$1" = "--quick" ]; then
        python test_full_loop.py --quick --verbose
    elif [ "$1" = "--verbose" ]; then
        python test_full_loop.py --verbose
    else
        python test_full_loop.py
    fi
}

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    
    if [ ! -z "$OLLAMA_PID" ]; then
        echo "Stopping Ollama service..."
        kill $OLLAMA_PID 2>/dev/null || true
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main execution
main() {
    echo -e "${BLUE}Prerequisites Check:${NC}"
    check_ollama_installed
    check_ollama_running
    check_qwen3_model
    test_ollama_connectivity
    check_python_deps
    check_otel_collector
    
    echo ""
    echo -e "${GREEN}✅ All prerequisites met!${NC}"
    echo ""
    
    run_test "$1"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--quick|--verbose|--help]"
        echo ""
        echo "Options:"
        echo "  --quick     Run test in quick mode (faster execution)"
        echo "  --verbose   Enable verbose output and console span export"
        echo "  --help      Show this help message"
        exit 0
        ;;
    *)
        main "$1"
        ;;
esac