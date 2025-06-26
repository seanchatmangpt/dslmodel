#!/usr/bin/env python3
"""
Test Git Auto Functionality
===========================

Simple test to validate git auto operations.
"""

def test_git_auto_cli():
    """Test git auto CLI functionality"""
    # Test that imports work
    from src.dslmodel.commands.git_auto_cli import GitAutoManager
    
    manager = GitAutoManager()
    status = manager.get_repo_status()
    
    print(f"Current branch: {status['branch']}")
    print(f"Staged files: {len(status['staged_files'])}")
    print(f"Modified files: {len(status['unstaged_files'])}")
    print(f"Untracked files: {len(status['untracked_files'])}")
    
    # Test smart commit message generation
    if not status["is_clean"]:
        message = manager.generate_smart_commit_message(status)
        print(f"Generated message: {message}")
    
    return True

if __name__ == "__main__":
    test_git_auto_cli()
    print("✅ Git Auto CLI test completed")