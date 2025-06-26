#!/bin/bash

# E2E Worktree Feature Development Setup
# This script creates a proper worktree structure for isolated feature development

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌳 DSLModel E2E Worktree Setup${NC}"
echo "=================================="

# Configuration
WORKTREE_BASE="${HOME}/dev/dslmodel-worktrees"
MAIN_REPO_PATH="${HOME}/dev/dslmodel"

# Feature branches to create
declare -a FEATURE_BRANCHES=(
    "feature/swarmsh-core"
    "feature/enterprise-coordination"
    "feature/weaver-fsm-integration"
    "feature/otel-telemetry"
    "feature/demo-engine"
    "feature/productization"
)

# Ensure we're in the main repository
cd "$MAIN_REPO_PATH"

# Create worktree base directory
echo -e "${GREEN}📁 Creating worktree base directory...${NC}"
mkdir -p "$WORKTREE_BASE"

# Function to create worktree
create_worktree() {
    local branch_name=$1
    local worktree_name=$(echo $branch_name | sed 's/feature\///')
    local worktree_path="$WORKTREE_BASE/$worktree_name"
    
    echo -e "${BLUE}🌿 Creating worktree for $branch_name...${NC}"
    
    # Check if branch exists remotely
    if git ls-remote --heads origin $branch_name | grep -q $branch_name; then
        # Branch exists, create worktree from it
        git worktree add "$worktree_path" "$branch_name" || {
            echo -e "${YELLOW}⚠️  Worktree already exists, removing and recreating...${NC}"
            git worktree remove "$worktree_path" --force 2>/dev/null || true
            rm -rf "$worktree_path"
            git worktree add "$worktree_path" "$branch_name"
        }
    else
        # Branch doesn't exist, create new branch in worktree
        git worktree add -b "$branch_name" "$worktree_path" main || {
            echo -e "${YELLOW}⚠️  Worktree already exists, removing and recreating...${NC}"
            git worktree remove "$worktree_path" --force 2>/dev/null || true
            rm -rf "$worktree_path"
            git worktree add -b "$branch_name" "$worktree_path" main
        }
    fi
    
    # Setup Python environment for the worktree
    echo -e "${GREEN}🐍 Setting up Python environment for $worktree_name...${NC}"
    cd "$worktree_path"
    
    # Install poetry dependencies
    poetry install --no-interaction
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        echo "# Worktree: $worktree_name" > .env
        echo "WORKTREE_NAME=$worktree_name" >> .env
        echo "FEATURE_BRANCH=$branch_name" >> .env
    fi
    
    cd "$MAIN_REPO_PATH"
    echo -e "${GREEN}✅ Worktree $worktree_name created successfully!${NC}"
    echo
}

# Create worktrees for each feature branch
for branch in "${FEATURE_BRANCHES[@]}"; do
    create_worktree "$branch"
done

# Create a development scripts directory
echo -e "${BLUE}📝 Creating E2E development scripts...${NC}"
mkdir -p "$WORKTREE_BASE/scripts"

# Create E2E test runner script
cat > "$WORKTREE_BASE/scripts/run_e2e_tests.sh" << 'EOF'
#!/bin/bash
# E2E Test Runner for all worktrees

set -euo pipefail

WORKTREE_BASE="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo "🧪 Running E2E tests across all worktrees..."
echo "=========================================="

for worktree in "$WORKTREE_BASE"/*/; do
    if [ -d "$worktree" ] && [ -f "$worktree/pyproject.toml" ]; then
        worktree_name=$(basename "$worktree")
        echo -e "\n🌿 Testing worktree: $worktree_name"
        cd "$worktree"
        
        # Run E2E coordination demo
        if [ -f "src/dslmodel/examples/enterprise_demo_minimal.py" ]; then
            echo "Running enterprise coordination demo..."
            poetry run python src/dslmodel/examples/enterprise_demo_minimal.py || echo "⚠️  Demo failed"
        fi
        
        # Run other E2E tests
        if [ -f "tests/test_e2e.py" ]; then
            echo "Running E2E test suite..."
            poetry run pytest tests/test_e2e.py -v || echo "⚠️  Tests failed"
        fi
    fi
done

echo -e "\n✅ E2E test run complete!"
EOF

chmod +x "$WORKTREE_BASE/scripts/run_e2e_tests.sh"

# Create worktree sync script
cat > "$WORKTREE_BASE/scripts/sync_worktrees.sh" << 'EOF'
#!/bin/bash
# Sync all worktrees with main branch

set -euo pipefail

WORKTREE_BASE="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo "🔄 Syncing all worktrees with main..."
echo "====================================="

for worktree in "$WORKTREE_BASE"/*/; do
    if [ -d "$worktree" ] && [ -f "$worktree/pyproject.toml" ]; then
        worktree_name=$(basename "$worktree")
        echo -e "\n🌿 Syncing worktree: $worktree_name"
        cd "$worktree"
        
        # Fetch latest changes
        git fetch origin
        
        # Get current branch
        current_branch=$(git rev-parse --abbrev-ref HEAD)
        
        # Merge or rebase with main
        echo "Merging main into $current_branch..."
        git merge origin/main --no-edit || echo "⚠️  Merge conflicts may need resolution"
    fi
done

echo -e "\n✅ Worktree sync complete!"
EOF

chmod +x "$WORKTREE_BASE/scripts/sync_worktrees.sh"

# Create worktree status script
cat > "$WORKTREE_BASE/scripts/worktree_status.sh" << 'EOF'
#!/bin/bash
# Show status of all worktrees

set -euo pipefail

WORKTREE_BASE="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo "📊 Worktree Status Report"
echo "========================="
echo

# Show main repo status first
MAIN_REPO="$HOME/dev/dslmodel"
echo "🏠 Main Repository: $MAIN_REPO"
cd "$MAIN_REPO"
echo "   Branch: $(git rev-parse --abbrev-ref HEAD)"
echo "   Status: $(git status --porcelain | wc -l) uncommitted changes"
echo

echo "🌳 Worktrees:"
git worktree list

echo -e "\n📋 Detailed Status:"
for worktree in "$WORKTREE_BASE"/*/; do
    if [ -d "$worktree" ] && [ -f "$worktree/pyproject.toml" ]; then
        worktree_name=$(basename "$worktree")
        cd "$worktree"
        
        echo -e "\n🌿 $worktree_name:"
        echo "   Branch: $(git rev-parse --abbrev-ref HEAD)"
        echo "   Status: $(git status --porcelain | wc -l) uncommitted changes"
        echo "   Last commit: $(git log -1 --format='%h %s' 2>/dev/null || echo 'No commits')"
    fi
done

echo -e "\n✅ Status report complete!"
EOF

chmod +x "$WORKTREE_BASE/scripts/worktree_status.sh"

# Create VS Code workspace file for multi-root development
cat > "$WORKTREE_BASE/dslmodel-e2e.code-workspace" << EOF
{
    "folders": [
        {
            "name": "Main Repository",
            "path": "$MAIN_REPO_PATH"
        },
        {
            "name": "SwarmSH Core",
            "path": "$WORKTREE_BASE/swarmsh-core"
        },
        {
            "name": "Enterprise Coordination",
            "path": "$WORKTREE_BASE/enterprise-coordination"
        },
        {
            "name": "Weaver FSM Integration",
            "path": "$WORKTREE_BASE/weaver-fsm-integration"
        },
        {
            "name": "OTEL Telemetry",
            "path": "$WORKTREE_BASE/otel-telemetry"
        },
        {
            "name": "Demo Engine",
            "path": "$WORKTREE_BASE/demo-engine"
        },
        {
            "name": "Productization",
            "path": "$WORKTREE_BASE/productization"
        }
    ],
    "settings": {
        "python.defaultInterpreterPath": "\${workspaceFolder}/.venv/bin/python",
        "python.terminal.activateEnvironment": true,
        "files.exclude": {
            "**/__pycache__": true,
            "**/.pytest_cache": true,
            "**/.mypy_cache": true
        }
    }
}
EOF

# Summary
echo
echo -e "${GREEN}✅ E2E Worktree Setup Complete!${NC}"
echo
echo "📁 Worktree Base: $WORKTREE_BASE"
echo "🌳 Created worktrees:"
for branch in "${FEATURE_BRANCHES[@]}"; do
    worktree_name=$(echo $branch | sed 's/feature\///')
    echo "   - $worktree_name → $branch"
done

echo
echo "🛠️  Available scripts:"
echo "   - $WORKTREE_BASE/scripts/run_e2e_tests.sh    # Run E2E tests across all worktrees"
echo "   - $WORKTREE_BASE/scripts/sync_worktrees.sh   # Sync all worktrees with main"
echo "   - $WORKTREE_BASE/scripts/worktree_status.sh  # Show status of all worktrees"

echo
echo "💻 VS Code workspace:"
echo "   code $WORKTREE_BASE/dslmodel-e2e.code-workspace"

echo
echo -e "${BLUE}🚀 Ready for E2E feature development!${NC}"