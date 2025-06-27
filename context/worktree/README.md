# DSL Worktree Command

## Overview
The `worktree` command manages Git worktrees for exclusive worktree development, enabling isolated development environments.

## Usage
```bash
# List all worktrees
dsl worktree list

# Create a new worktree
dsl worktree create

# Remove a worktree
dsl worktree remove

# Show status of all worktrees
dsl worktree status

# Get command to switch to worktree
dsl worktree switch

# Initialize exclusive worktree workflow
dsl worktree init

# Clean up merged/stale worktrees
dsl worktree clean
```

## Subcommands

### list
List all worktrees:
```bash
dsl worktree list
```

### create
Create a new worktree for isolated development:
```bash
dsl worktree create --name "feature-auth" --branch "feature/user-authentication"
```

### remove
Remove a worktree and optionally its branch:
```bash
dsl worktree remove --name "feature-auth" --delete-branch
```

### status
Show status of all worktrees:
```bash
dsl worktree status
```

### switch
Get the command to switch to a specific worktree:
```bash
dsl worktree switch --name "feature-auth"
```

### init
Initialize exclusive worktree development workflow:
```bash
dsl worktree init
```

### clean
Clean up merged/stale worktrees:
```bash
dsl worktree clean
```

## Worktree Features
- **Isolated Development**: Separate environments for each feature
- **Exclusive Access**: Agent-specific worktree isolation
- **Automatic Cleanup**: Removal of stale worktrees
- **Status Monitoring**: Real-time worktree status tracking

## Context
The worktree system provides isolated development environments for agents, ensuring clean separation of concerns and preventing conflicts during concurrent development. 