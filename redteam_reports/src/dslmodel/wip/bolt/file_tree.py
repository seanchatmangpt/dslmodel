# /Users/sac/dev/dslmodel/src/dslmodel/wip/bolt/file_tree.py
import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel

from dslmodel import DSLModel, init_instant
from typing import List, Tuple


def diff(tree1: "FileTreeNode", tree2: "FileTreeNode") -> Tuple[
    List["FileTreeNode"], List["FileTreeNode"], List["FileTreeNode"]]:
    """
    Compare two file trees and return the differences.

    Args:
        tree1 (FileTreeNode): The first tree to compare.
        tree2 (FileTreeNode): The second tree to compare.

    Returns:
        Tuple[List[FileTreeNode], List[FileTreeNode], List[FileTreeNode]]:
            - Added: Nodes present in tree2 but not in tree1.
            - Removed: Nodes present in tree1 but not in tree2.
            - Modified: Nodes with the same name but different attributes/content.
    """
    added = []
    removed = []
    modified = []

    # Helper to find a node by name in a list
    def find_node_by_name(name: str, nodes: List[FileTreeNode]) -> Optional[FileTreeNode]:
        for node in nodes:
            if node.name == name:
                return node
        return None

    # If both are files, compare attributes
    if tree1.type == FileType.file and tree2.type == FileType.file:
        if tree1.attributes != tree2.attributes:
            modified.append(tree2)
        return added, removed, modified

    # Compare children if both are directories
    if tree1.type == FileType.directory and tree2.type == FileType.directory:
        tree1_children = {child.name: child for child in tree1.children or []}
        tree2_children = {child.name: child for child in tree2.children or []}

        # Check for added nodes
        for name, child2 in tree2_children.items():
            if name not in tree1_children:
                added.append(child2)
            else:
                # Recursively diff common nodes
                child1 = tree1_children[name]
                sub_added, sub_removed, sub_modified = diff(child1, child2)
                added.extend(sub_added)
                removed.extend(sub_removed)
                modified.extend(sub_modified)

        # Check for removed nodes
        for name, child1 in tree1_children.items():
            if name not in tree2_children:
                removed.append(child1)

    return added, removed, modified


def get_content(node: "FileTreeNode") -> Optional[str]:
    if node.type == FileType.file:
        for attr in node.attributes:
            if attr.key == "content":
                return attr.value
    return None


def set_content(node: "FileTreeNode", content: str) -> None:
    if node.type != FileType.file:
        raise ValueError("Content can only be set for file nodes.")
    node.attributes.append(Attribute(key="content", value=content))


def add_virtual(node: "FileTreeNode", items: List[str]) -> None:
    """
    Add directories or files to the current node's children.

    Args:
        node (FileTreeNode): The parent node to add items to node as children.
        items (List[str]): A list of directory or file names to add.
    """
    if node.children is None:
        node.children = []

    for item in items:
        # Treat as file if there's a valid file extension after the last dot
        if os.path.splitext(item)[1]:  # This checks for extensions like `.py`, `.txt`
            node.children.append(FileTreeNode(
                type=FileType.file,
                name=item,
                attributes=[],
            ))
        else:  # Otherwise, treat as a directory
            node.children.append(FileTreeNode(
                type=FileType.directory,
                name=item,
                attributes=[],
                children=[],
            ))


def generate_tree_virtual(node: "FileTreeNode", indent: str = '', is_root: bool = True, is_last: bool = True) -> str:
    """
    Generate a string representation of a virtual file tree.

    Args:
        node (FileTreeNode): The root of the virtual file tree to traverse.
        indent (str): The current level of indentation for formatting.
        is_root (bool): Whether the current node is the root.
        is_last (bool): Whether the current node is the last child.

    Returns:
        str: A string representation of the virtual file tree.
    """
    # For the root, skip branch symbols
    if is_root:
        tree_str = f"{node.name}\n"
        new_indent = indent
    else:
        branch = '└── ' if is_last else '├── '
        if node.type == FileType.directory:
            display_name = f"📂 {node.name}"
        else:
            display_name = f"📄 {node.name}"
        tree_str = f"{indent}{branch}{display_name}\n"
        new_indent = indent + ('    ' if is_last else '│   ')

    # Recursively process children if this is a directory
    if node.children:
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            tree_str += generate_tree_virtual(child, new_indent, is_root=False, is_last=is_last_child)

    return tree_str


def create(node: "FileTreeNode", base_path: str) -> None:
    current_path = os.path.join(base_path, node.name)

    if node.type == FileType.directory:
        os.makedirs(current_path, exist_ok=True)
        if node.children:
            for child in node.children:
                create(child, current_path)
    elif node.type == FileType.file:
        with open(current_path, 'w') as f:
            content = get_content(node)
            if content:
                f.write(content)


def load(path: str) -> "FileTreeNode":
    if os.path.isdir(path):
        return FileTreeNode(
            type=FileType.directory,
            name=os.path.basename(path),
            attributes=[],
            children=[
                load(os.path.join(path, child)) for child in os.listdir(path)
            ],
        )
    elif os.path.isfile(path):
        return FileTreeNode(
            type=FileType.file,
            name=os.path.basename(path),
            attributes=[Attribute(key="size", value=str(os.path.getsize(path)))],
            children=None,
        )


def find(node: "FileTreeNode", name: str) -> Optional["FileTreeNode"]:
    if node.name == name:
        return node

    if node.children:
        for child in node.children:
            result = find(child, name)
            if result:
                return result

    return None


class FileType(str, Enum):
    file = "file"
    directory = "directory"


class Attribute(BaseModel):
    key: str
    value: str


class FileTreeNode(DSLModel):
    type: FileType
    name: str
    attributes: List[Attribute]
    children: Optional[List["FileTreeNode"]] = None  # For directories

    def tree(self) -> str:
        return generate_tree_virtual(self)

    def add(self, items: List[str]) -> None:
        add_virtual(self, items)

    def create(self, base_path: str) -> None:
        """
        Create the file tree on the disk starting from the given base path.
        """
        create(self, base_path)

    @classmethod
    def load(cls, path: str) -> "FileTreeNode":
        """
        Load a file tree from the given path on the disk.
        """
        return load(path)

    def find(self, name: str) -> Optional["FileTreeNode"]:
        """
        Find a node by name within the file tree.
        """
        return find(self, name)

    def get_content(self) -> Optional[str]:
        """
        Retrieve the content of a file node.
        """
        return get_content(self)

    def set_content(self, content: str) -> None:
        """
        Set the content for a file node.
        """
        set_content(self, content)

    def __getattr__(self, item: str) -> Optional["FileTreeNode"]:
        if self.children:
            for child in self.children:
                if child.name == item:
                    return child
        raise AttributeError(f"'{self.name}' has no child named '{item}'")


FileTreeNode.model_rebuild()  # Required to enable recursive types


class Response(BaseModel):
    file_tree: FileTreeNode


def main():
    # Example request to generate a non-existent file tree
    init_instant()
    file_tree = FileTreeNode.from_prompt(
        prompt='[{"role": "system", "content": "You are a file tree generator AI. Generate a virtual file tree based on user input."}, {"role": "user", "content": "Create a project structure for a enterprise Python FastAPI application."}]',
    )
    print(file_tree.tree())


def mock_tree_with_dot_access():
    # Create the root directory
    project_tree = FileTreeNode(
        type=FileType.directory,
        name="project",
        attributes=[Attribute(key="owner", value="user123")],
        children=[]
    )

    # Add top-level directories and files to the project tree
    project_tree.add(["src", "tests", "docs", "requirements.txt", "README.md"])

    # Find and add subdirectories/files for "src"
    project_tree.src.add(["main.py", "models", "routes"])

    # Find and add files for "models"
    project_tree.src.models.add(["user.py", "item.py"])

    # Find and add files for "routes"
    project_tree.src.routes.add(["user_routes.py", "item_routes.py"])

    # Find and add files for "tests"
    project_tree.tests.add(["test_main.py", "test_user.py", "test_item.py"])

    # Find and add files for "docs"
    project_tree.docs.add(["installation.md", "usage.md", "api_reference.md"])

    return project_tree


if __name__ == "__main__":
    tree = mock_tree_with_dot_access()

    # Print the tree structure
    print(tree.tree())

    # Access using dot notation
    print(tree.src.models.name)  # Output: models
    print(tree.src.models.children[0].name)  # Output: user.py
