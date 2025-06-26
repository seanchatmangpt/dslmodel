# Git Auto DX - Automated Git Operations with Smart Developer Experience

## Overview

Git Auto DX provides intelligent, automated git operations with excellent developer experience. It follows the 80/20 principle - automating the 80% of common git workflows while providing smart defaults and safety checks.

## 🚀 Quick Start

### Essential Commands
```bash
# Check status with smart suggestions
poe git-status

# Automated workflow (safe - no push)
poe git-auto-safe

# Complete automation (with push)
poe git-auto

# 80/20 workflow
poe git-8020
```

### Individual Operations
```bash
# Smart add with validation
poe git-add

# Interactive file selection
poe git-add-interactive

# Smart commit with auto-generated messages
poe git-commit

# Manual commit message
poe git-commit-manual

# Smart push with conflict resolution
poe git-push
```

## 🎯 Key Features

### Smart Commit Messages
Automatically generates intelligent commit messages based on:
- File patterns (tests, docs, config, CLI, examples)
- Change types (feat, fix, docs, test, chore)
- Scope detection (cli, validation, config)
- File statistics

Example generated messages:
```
feat(cli): add automated git operations

- 3 files modified
- 1 CLI files
- 2 documentation files
```

### Pre-commit Validation
Automatically checks for:
- Large files (>10MB) with warnings
- Sensitive data patterns (API keys, passwords, secrets)
- File type validation
- Size limits

### Branch Protection
- Protects main/master/production branches from force push
- Requires confirmation for protected branch operations
- Smart upstream branch handling

### Conflict Resolution
- Automatic pull and retry on push conflicts
- Rebase integration for clean history
- Interactive conflict resolution

## 🔧 Configuration

### View Configuration
```bash
poe git-config
```

### Set Configuration
```bash
# Enable auto-push
python src/dslmodel/commands/git_auto_cli.py config --set auto_push --value true

# Disable smart commit messages
python src/dslmodel/commands/git_auto_cli.py config --set smart_commit_messages --value false

# Add custom commit prefix
python src/dslmodel/commands/git_auto_cli.py config --set auto_commit_prefixes --value '["feat:", "fix:", "docs:", "custom:"]'
```

### Configuration Options
```json
{
  "auto_commit_prefixes": ["feat:", "fix:", "docs:", "refactor:", "test:", "chore:"],
  "smart_commit_messages": true,
  "pre_commit_validation": true,
  "auto_push": false,
  "branch_protection": ["main", "master", "production"],
  "commit_template": "{type}: {scope} - {description}",
  "max_commit_length": 72,
  "include_file_stats": true
}
```

## 📊 Workflow Examples

### 80/20 Development Workflow
```bash
# 1. Check current status
poe git-status

# 2. Complete automated workflow
poe git-8020
```

### Safe Development Workflow
```bash
# 1. Add files with validation
poe git-add

# 2. Commit with smart message
poe git-commit

# 3. Review before pushing
poe git-status

# 4. Push when ready
poe git-push
```

### Interactive Workflow
```bash
# 1. Interactive file selection
poe git-add-interactive

# 2. Manual commit message
poe git-commit-manual

# 3. Smart push
poe git-push
```

## 🛡️ Safety Features

### Security Checks
- Scans for API keys, passwords, tokens
- Warns about large files
- Validates file types
- Checks for binary files in text commits

### Branch Protection
- Prevents accidental force push to protected branches
- Requires confirmation for sensitive operations
- Smart upstream branch detection

### Conflict Prevention
- Pre-push conflict detection
- Automatic pull and retry
- Clean rebase integration

## 🎨 Developer Experience

### Rich UI
- Colorful status tables
- Progress indicators
- Smart suggestions
- Error context

### Intelligent Defaults
- Auto-detects file patterns
- Generates contextual commit messages
- Suggests next steps
- Remembers user preferences

### Minimal Configuration
- Works out of the box
- Sensible defaults
- Optional customization
- Per-repo configuration

## 📈 Performance

### 80/20 Optimizations
- Fast status checks
- Minimal git operations
- Efficient file scanning
- Smart caching

### Batch Operations
- Groups related files
- Optimizes git commands
- Reduces repository locks
- Parallel validation

## 🔄 Integration

### Poetry/Poe Integration
All commands available as poe tasks for consistent developer experience:

```bash
poe git-status        # Enhanced status
poe git-add           # Smart add
poe git-commit        # Smart commit
poe git-push          # Smart push
poe git-auto          # Complete automation
poe git-8020          # 80/20 workflow
```

### CI/CD Integration
```bash
# In CI/CD pipelines
python src/dslmodel/commands/git_auto_cli.py auto --no-push --validate
```

### IDE Integration
Can be integrated with editors through:
- Command palette
- Keyboard shortcuts
- Git hooks
- Status bar integration

## 🐛 Troubleshooting

### Common Issues

#### "No changes to commit"
```bash
# Check what's available
poe git-status

# Add files first
poe git-add
```

#### "Push rejected"
```bash
# Auto-handled by git-push, but manual:
git pull --rebase
poe git-push
```

#### "Validation failed"
```bash
# Review sensitive data warnings
# Remove sensitive files or add to .gitignore
poe git-add-interactive
```

#### "Branch protected"
```bash
# Review protection settings
poe git-config

# Override protection (careful!)
python src/dslmodel/commands/git_auto_cli.py push --force
```

### Recovery Commands
```bash
# Reset configuration
python src/dslmodel/commands/git_auto_cli.py config --reset

# Check repository status
poe git-status

# Clean restart
poe git-add
poe git-commit
```

## 📚 Examples

### Feature Development
```bash
# Start feature
git checkout -b feature/new-cli

# Develop...
# (make changes)

# Automated commit
poe git-auto-safe

# Review and push
poe git-status
poe git-push
```

### Bug Fix
```bash
# Quick fix workflow
poe git-8020

# Generated message: "fix(validation): resolve edge case in file detection"
```

### Documentation Update
```bash
# Update docs
# (edit documentation)

poe git-auto

# Generated message: "docs: update git auto DX documentation"
```

---

**Git Auto DX**: Intelligent automation with excellent developer experience. 
*Part of DSLModel CLI ecosystem.*