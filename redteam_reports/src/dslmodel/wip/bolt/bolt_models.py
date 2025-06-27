# /Users/sac/dev/dslmodel/src/dslmodel/wip/bolt/bolt_models.py
from pydantic import Field
from typing import List, Optional

from dslmodel import DSLModel


class ShellAction(DSLModel):
    """Represents a shell command action."""
    command: str = Field(..., description="The shell command to execute as part of this action.")


class FileAction(DSLModel):
    """Represents a file creation or modification action."""
    file_path: str = Field(..., description="The path to the file being created or modified.")
    content: str = Field(..., description="The full content to write to the file. Partial updates are not allowed.")


class StartAction(DSLModel):
    """Represents a dev server start action."""
    command: str = Field(..., description="The command to start the dev server.")


class BoltAction(DSLModel):
    """Represents an action in an artifact."""
    shell: Optional[ShellAction] = Field(None, description="A shell command action.")
    file: Optional[FileAction] = Field(None, description="A file creation or modification action.")
    start: Optional[StartAction] = Field(None, description="An action to start a dev server.")


class BoltArtifact(DSLModel):
    """Represents an artifact containing multiple actions."""
    id: str = Field(..., description="Unique identifier for the artifact.")
    title: str = Field(..., description="Title describing the artifact's purpose.")
    actions: List[BoltAction] = Field(..., description="List of actions included in the artifact.")


class SystemConstraints(DSLModel):
    """Defines the operational constraints."""
    operating_environment: str = Field(..., description="Environment the system operates in, e.g., WebContainer.")
    limitations: List[str] = Field(..., description="List of limitations, e.g., unavailable compilers.")
    preferred_tools: List[str] = Field(..., description="Preferred tools or frameworks for development.")
    available_commands: List[str] = Field(..., description="Shell commands available in the current environment.")


class CodeFormattingInfo(DSLModel):
    """Details about formatting standards."""
    indentation: int = Field(..., description="Number of spaces for indentation.")
    language: str = Field(..., description="Programming language used for the code.")


class MessageFormattingInfo(DSLModel):
    """Specifies allowed HTML elements."""
    allowed_html_elements: List[str] = Field(..., description="HTML elements allowed in the output.")


class DiffSpec(DSLModel):
    """Defines the specifications for file modifications."""
    modification_tag_name: str = Field(..., description="Tag name for identifying file modifications.")
    diff_format: str = Field(..., description="Format for file diffs, e.g., GNU unified diff.")


class ArtifactInfo(DSLModel):
    """Information about artifacts and their usage."""
    description: str = Field(..., description="Description of the artifact's purpose.")
    rules: List[str] = Field(..., description="Rules to follow when creating or using artifacts.")


class ChainOfThoughtInstructions(DSLModel):
    """Outlines planning and execution instructions."""
    disallowed_phrases: List[str] = Field(..., description="Phrases disallowed in the response.")
    steps: List[str] = Field(..., description="Step-by-step guide for planning and execution.")


class PromptOptions(DSLModel):
    """Metadata for the prompt configuration."""
    cwd: str = Field(..., description="Current working directory for file operations.")
    allowed_html_elements: List[str] = Field(..., description="HTML elements allowed in the output.")
    modification_tag_name: str = Field(..., description="Tag name for file modifications.")
