import os
from typing import List
from dslmodel import init_instant, init_lm
from dslmodel.generators import gen_list
from dslmodel.wip.bolt.file_tree import FileTreeNode, create as create_structure
from dslmodel.wip.bolt.bolt_models import (
    BoltArtifact,
    ShellAction,
    FileAction,
    StartAction,
)


def generate_folder_structure(prompt: str) -> FileTreeNode:
    """
    Generate the folder structure dynamically using FileTreeNode and a prompt.
    """
    return FileTreeNode.from_prompt(prompt=prompt)


def generate_artifacts(prompt: str) -> List[BoltArtifact]:
    """
    Dynamically generate artifacts based on a prompt.
    """
    return BoltArtifact.from_prompt(prompt=prompt)


def execute_shell_commands(artifacts: List[BoltArtifact]):
    """
    Execute shell commands from the artifacts.
    """
    for artifact in artifacts:
        for action in artifact.actions:
            if action.shell:
                print(f"Executing shell command: {action.shell.command}")
                os.system(action.shell.command)


def populate_files(artifacts: List[BoltArtifact], base_path: str):
    """
    Populate files based on BoltArtifact actions.
    """
    for artifact in artifacts:
        for action in artifact.actions:
            if action.file:
                file_path = os.path.join(base_path, action.file.file_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                print(f"Creating file: {file_path}")
                with open(file_path, "w") as f:
                    f.write(action.file.content)


# Step 2: Generate artifacts for file content
artifact_prompt = (
    "Generate artifacts for a FastAPI application with modular components. "
    # "Include main.py, models/user.py, routes/user_routes.py, and requirements.txt. "
    # "Add a shell command to install dependencies (FastAPI, Uvicorn)."
)


def main():
    # Step 1: Generate folder structure
    folder_structure_prompt = "Generate a folder structure for an enterprise Python FastAPI application."
    print("Generating folder structure...")
    folder_tree = generate_folder_structure(folder_structure_prompt)
    print("Generated Folder Structure:")
    print(folder_tree.tree())

    gen_list("artifact list f{artifact_prompt}")
    print("\nGenerating artifacts...")
    artifacts = generate_artifacts(artifact_prompt)

    # Step 3: Create folder structure on the filesystem
    base_path = "./generated_project"
    print("\nCreating folder structure on disk...")
    folder_tree.create(base_path)

    # Step 4: Populate files and execute commands
    print("\nPopulating files...")
    populate_files(artifacts, base_path)
    print("\nExecuting shell commands...")
    # execute_shell_commands(artifacts)

    print("\nProject setup complete. Check the generated_project directory.")


if __name__ == "__main__":
    init_instant()
    folder_structure_prompt = "Generate a folder structure for an enterprise Python FastAPI application."
    print("Generating folder structure...")
    folder_tree = generate_folder_structure(folder_structure_prompt)
    print("Generated Folder Structure:", folder_tree.tree())
    artifacts = gen_list(f"{artifact_prompt}\n{folder_tree.tree()}")
    print(artifacts)
    folder_tree2 = generate_folder_structure(f"Complete file and folder tree.\n{artifacts}")
    print(folder_tree2.tree())
    # main()
