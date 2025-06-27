import os

from dslmodel.examples.file_tree import *


def create_recruiter_context_tree() -> FileTreeNode:
    """
    Generate the `.context` directory structure for the recruiter module.
    Returns:
        FileTreeNode: Root of the `.context` directory tree.
    """
    # Content for `index.md`
    index_content = """---
module-name: "recruiter"
description: "Tools for discovering and managing talent."
related-modules: []
architecture: "Layered Architecture"
components:
  - name: Job Matching
    description: Matches job seekers with roles.
  - name: Talent Pool Management
    description: Manages candidate data.
patterns:
  - name: Factory
    usage: Used for creating reusable services.
  - name: Mediator
    usage: Used for managing interactions between modules.
---
"""

    # Content for `docs.md`
    docs_content = """# Documentation for Recruiter Module

## Overview
The Recruiter module offers tools to discover, engage, and manage talent efficiently.

## Features
- AI-driven job matching.
- Candidate data management.
- Collaboration tools for recruiters.

## Development Practices
- Use clean architecture principles.
- Modularize code for testability.

## API Details
- Endpoints for candidate search and job matching.
- REST API for third-party integrations.

## Integration Notes
- Ensure proper error handling for external API calls.
"""

    # Content for diagram files
    architecture_diagram = "%% Diagram showing high-level architecture for the recruiter module."
    data_flow_diagram = "%% Diagram showing recruiter-specific data flows."

    # Build the `.context` file tree
    context_tree = FileTreeNode(
        type=FileType.directory,
        name=".context",
        attributes=[],
        children=[
            FileTreeNode(
                type=FileType.file,
                name="index.md",
                attributes=[Attribute(key="content", value=index_content)],
            ),
            FileTreeNode(
                type=FileType.file,
                name="docs.md",
                attributes=[Attribute(key="content", value=docs_content)],
            ),
            FileTreeNode(
                type=FileType.directory,
                name="diagrams",
                attributes=[],
                children=[
                    FileTreeNode(
                        type=FileType.file,
                        name="architecture.mmd",
                        attributes=[Attribute(key="content", value=architecture_diagram)],
                    ),
                    FileTreeNode(
                        type=FileType.file,
                        name="data-flow.mmd",
                        attributes=[Attribute(key="content", value=data_flow_diagram)],
                    ),
                ],
            ),
        ],
    )
    return context_tree


def write_tree_to_disk(node: FileTreeNode, base_path: str) -> None:
    """
    Recursively write the file tree to disk.
    Args:
        node (FileTreeNode): Root of the file tree.
        base_path (str): The path to write files.
    """
    current_path = os.path.join(base_path, node.name)

    if node.type == FileType.directory:
        os.makedirs(current_path, exist_ok=True)
        if node.children:
            for child in node.children:
                write_tree_to_disk(child, current_path)
    elif node.type == FileType.file:
        with open(current_path, "w") as file:
            content = node.get_content()
            if content:
                file.write(content)


if __name__ == "__main__":
    # Generate the recruiter `.context` tree
    recruiter_context = create_recruiter_context_tree()

    # Define the base path to write the directory
    base_path = "./recruiter"

    # Write the `.context` tree to disk
    write_tree_to_disk(recruiter_context, base_path)

    # Print the generated virtual tree structure
    print(recruiter_context.tree())
