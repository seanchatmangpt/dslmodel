"""
DSLModel Git Module - Level-5 Git-Native Substrate
Advanced Git operations with OTEL spans and autonomous capabilities
"""

from .git_auto import (
    GitRegistry,
    GitOperation,
    git_wrap,
    # Data-layer superpowers
    add_worktree,
    remove_worktree,
    set_sparse_checkout,
    partial_clone,
    create_bundle,
    # Collaboration & federation
    add_submodule,
    update_submodules,
    add_remote,
    add_notes,
    # Workflow / history manipulation
    cherry_pick_commit,
    rebase_preserve_merges,
    reset_keep,
    start_bisect,
    # Security & provenance
    commit_signed,
    tag_signed,
    add_sbom_attestation,
    # Maintenance & performance
    gc_aggressive,
    repack_with_bitmaps,
    prune_remote_refs,
    # High-level domain operations
    add_domain_pack,
    create_agent_worktree,
    setup_sparse_agent_clone,
    emergency_rollback,
    federation_sync,
    # Registry management
    get_registry,
    reload_registry,
    list_git_operations,
    get_operation_info,
)

__all__ = [
    "GitRegistry",
    "GitOperation", 
    "git_wrap",
    # Data-layer superpowers
    "add_worktree",
    "remove_worktree",
    "set_sparse_checkout",
    "partial_clone",
    "create_bundle",
    # Collaboration & federation
    "add_submodule",
    "update_submodules",
    "add_remote",
    "add_notes",
    # Workflow / history manipulation
    "cherry_pick_commit",
    "rebase_preserve_merges",
    "reset_keep",
    "start_bisect",
    # Security & provenance
    "commit_signed",
    "tag_signed",
    "add_sbom_attestation",
    # Maintenance & performance
    "gc_aggressive",
    "repack_with_bitmaps",
    "prune_remote_refs",
    # High-level domain operations
    "add_domain_pack",
    "create_agent_worktree",
    "setup_sparse_agent_clone",
    "emergency_rollback",
    "federation_sync",
    # Registry management
    "get_registry",
    "reload_registry",
    "list_git_operations",
    "get_operation_info",
]

__version__ = "1.0.0"