from pydantic import BaseModel, Field
from typing import List, Dict
from dslmodel import DSLModel, init_instant
from dslmodel.utils.dspy_tools import init_versatile


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

    def get_node(self, node_id: str) -> Node:
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
            if to_id not in from_node.connections:
                from_node.connections.append(to_id)
            if from_id not in to_node.connections:
                to_node.connections.append(from_id)
        else:
            raise ValueError(f"One or both nodes not found: {from_id}, {to_id}")

    def visualize(self):
        """
        Print a simple representation of the graph structure.
        """
        for node in self.nodes:
            print(f"Node: {node.label}")
            print(f"  Details: {node.details}")
            print(f"  Connections: {', '.join(node.connections)}")


class GraphOfThoughtsModel(DSLModel):
    """
    DSL model to dynamically generate the graph from structured input.
    """
    graph: GraphOfThoughts

    def __init__(self, **data):
        super().__init__(**data)

    @classmethod
    def parse(cls, prompt: str) -> "GraphOfThoughtsModel":
        """
        Generate a GraphOfThoughts model dynamically based on input prompt.
        """
        init_instant()
        return cls.from_prompt(
            prompt=f"""
                "role": "system",
                 "content": "You are a graph model generator AI. Parse the user's input to create a graph of thoughts.",
                "role": "user", "content": "{prompt}"
                
                first create the nodes and then connect them. Nodes must have connections/
            """
        )


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant
    init_versatile()

    # Example Prompt
    prompt = """
    Create a graph of thoughts for the Codebase Context Specification:
    - Metadata: High-level information about the project.
    - .context Directory: Root directory for all contextual files.
    - index.md: Primary context file.
    - docs.md: Detailed documentation file.
    - Diagrams: Directory for visual files.
    - Architecture Diagram: Represents project architecture.
    - Data Flow Diagram: Represents data flows.

    Relationships:
    - Metadata connects to .context Directory.
    - .context Directory connects to index.md, docs.md, and Diagrams.
    - Diagrams connect to Architecture Diagram and Data Flow Diagram.
    """

    # Generate the Graph
    generated_graph_model = GraphOfThoughtsModel.parse(prompt)
    graph = generated_graph_model.graph

    # Visualize the Graph
    graph.visualize()


if __name__ == '__main__':
    main()
