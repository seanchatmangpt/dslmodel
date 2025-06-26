from typing import List, Optional
from pydantic import BaseModel, Field

from dslmodel import DSLModel


# Define Metadata Model
class Metadata(BaseModel):
    """
    High-level metadata about the module or project.
    """
    module_name: str = Field(..., description="The unique name of the module or project.")
    description: str = Field(..., description="A concise summary of the module's purpose.")
    related_modules: List[dict] = Field(
        default_factory=list,
        description=(
            "A list of related modules with their names and paths. Example: "
            "[{'name': 'shared-utils', 'path': '../shared-utils'}]"
        ),
    )
    architecture: dict = Field(
        default_factory=dict,
        description=(
            "Information about the module's architecture. Includes style (e.g., 'Microservices') "
            "and components with their descriptions."
        ),
    )
    patterns: List[dict] = Field(
        default_factory=list,
        description=(
            "Design patterns applied within the module, with their usage rationale. "
            "Example: [{'name': 'Repository Pattern', 'usage': 'To abstract database queries.'}]"
        ),
    )


# Define ContextFile Model
class ContextFile(BaseModel):
    """
    Represents a single file in the .context directory.
    """
    name: str = Field(..., description="The file name, including its extension (e.g., 'index.md').")
    content: str = Field(..., description="The file's content, typically in Markdown format.")


# Define DiagramFile Model
class DiagramFile(ContextFile):
    """
    Specialization of ContextFile for Mermaid diagrams.
    """
    diagram_type: str = Field(
        ...,
        description="The type of diagram (e.g., 'Architecture', 'Data Flow')."
    )


# Define ContextDirectory Model
class ContextDirectory(BaseModel):
    """
    Represents a directory containing files and optional subdirectories.
    """
    name: str = Field(..., description="The directory name (e.g., '.context').")
    files: List[ContextFile] = Field(
        default_factory=list,
        description=(
            "List of files (ContextFile or DiagramFile) contained in the directory. "
            "Example: [{'name': 'index.md', 'content': '...'}]"
        ),
    )
    subdirectories: List["ContextDirectory"] = Field(
        default_factory=list,
        description="List of nested ContextDirectory objects for hierarchical organization."
    )

    class Config:
        # Allow recursive types for subdirectories
        arbitrary_types_allowed = True


# Define CodebaseContextSpecification Model
class CodebaseContextSpecification(DSLModel):
    """
    The top-level model encapsulating metadata and the .context directory structure.
    """
    metadata: Metadata = Field(..., description="High-level project information.")
    context_directory: ContextDirectory = Field(
        ...,
        description="The root .context directory containing files and subdirectories."
    )


from pydantic import BaseModel, Field
from typing import List, Optional


class Node(BaseModel):
    """
    Represents a thought or node in the graph.
    """
    id: str = Field(..., description="Unique identifier for the node.")
    label: str = Field(..., description="Short description or title for the node.")
    details: str = Field(..., description="Detailed explanation or content for the node.")
    connections: List[str] = Field(
        default_factory=list,
        description="List of connected node IDs representing relationships."
    )


class GraphOfThoughts(BaseModel):
    """
    Represents the overall graph structure for CodebaseContextSpecification.
    """
    nodes: List[Node] = Field(..., description="List of all nodes in the graph.")

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Retrieve a node by its ID.
        """
        return next((node for node in self.nodes if node.id == node_id), None)

    def add_connection(self, from_id: str, to_id: str):
        """
        Create a connection between two nodes.
        """
        from_node = self.get_node(from_id)
        to_node = self.get_node(to_id)

        if from_node and to_node:
            from_node.connections.append(to_id)
            to_node.connections.append(from_id)  # Assuming bidirectional connection
        else:
            raise ValueError(f"One or both nodes not found: {from_id}, {to_id}")


def main():
    # Define nodes
    nodes = [
        Node(
            id="metadata",
            label="Metadata",
            details="High-level information about the module or project, such as name, description, and related modules."
        ),
        Node(
            id="context_directory",
            label=".context Directory",
            details="The root directory containing all context-related files and subdirectories."
        ),
        Node(
            id="index_md",
            label="index.md",
            details="The primary file in the .context directory that provides an overview and YAML metadata."
        ),
        Node(
            id="docs_md",
            label="docs.md",
            details="A file containing detailed documentation, including technical and business context."
        ),
        Node(
            id="diagrams",
            label="Diagrams",
            details="A subdirectory containing visual documentation in Mermaid format."
        ),
        Node(
            id="architecture_diagram",
            label="Architecture Diagram",
            details="A visual representation of the module or project's architecture."
        ),
        Node(
            id="data_flow_diagram",
            label="Data Flow Diagram",
            details="A diagram illustrating the flow of information or processes between components."
        ),
    ]

    # Create the graph and define relationships
    graph = GraphOfThoughts(nodes=nodes)

    # Add connections between nodes
    graph.add_connection("metadata", "context_directory")
    graph.add_connection("context_directory", "index_md")
    graph.add_connection("context_directory", "docs_md")
    graph.add_connection("context_directory", "diagrams")
    graph.add_connection("diagrams", "architecture_diagram")
    graph.add_connection("diagrams", "data_flow_diagram")

    # Visualize the graph structure
    for node in graph.nodes:
        print(f"Node: {node.label}")
        print(f"  Details: {node.details}")
        print(f"  Connections: {', '.join(node.connections)}")


# Example Usage (Optional Test)
if __name__ == "__main__":
    # Example Metadata
    metadata = Metadata(
        module_name="recruiter",
        description="Tools for discovering and managing talent.",
        related_modules=[{"name": "shared-utils", "path": "../shared-utils"}],
        architecture={
            "style": "Microservices",
            "components": [{"name": "Candidate Matching", "description": "AI-driven job matching."}]
        },
        patterns=[{"name": "CQRS", "usage": "To separate read and write operations."}]
    )

    # Example ContextDirectory
    context_directory = ContextDirectory(
        name=".context",
        files=[
            ContextFile(
                name="index.md",
                content=(
                    "---\nmodule-name: 'recruiter'\ndescription: 'Tools for discovering and managing talent.'\n---\n"
                )
            ),
            DiagramFile(
                name="architecture.mmd",
                diagram_type="Architecture",
                content="graph TD\n  User -->|Interacts with| Frontend\n  Frontend --> Backend\n"
            )
        ],
        subdirectories=[
            ContextDirectory(
                name="diagrams",
                files=[
                    DiagramFile(
                        name="data-flow.mmd",
                        diagram_type="Data Flow",
                        content="graph LR\n  API -->|Sends Data| Service\n  Service --> Database\n"
                    )
                ]
            )
        ]
    )

    # Combine into CCS
    ccs = CodebaseContextSpecification(metadata=metadata, context_directory=context_directory)

    # Print CCS Data
    print(ccs.to_yaml())

    main()
