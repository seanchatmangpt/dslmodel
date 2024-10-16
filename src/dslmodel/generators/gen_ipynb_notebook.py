from pydantic import Field

from dslmodel import DSLModel


# Notebook metadata model
class NotebookMetadataModel(DSLModel):
    kernelspec: dict = Field(..., description="Information about the notebook's kernel.")
    language_info: dict = Field(
        ..., description="Information about the notebook's programming language."
    )


# Notebook output model for code cells
class NotebookOutputModel(DSLModel):
    output_type: str = Field(
        ..., description="The type of the output (e.g., stream, display_data, error)."
    )
    text: list[str] | None = Field(None, description="Text output for streams or errors.")
    data: dict | None = Field(None, description="Data output (e.g., images, JSON).")
    name: str | None = Field(
        None, description="For stream output, the name (e.g., 'stdout', 'stderr')."
    )
    execution_count: int | None = Field(None, description="Execution count if relevant.")


# Base model for a notebook cell
class NotebookCellModel(DSLModel):
    cell_type: str = Field(..., description="The type of the cell (e.g., code, markdown, raw).")
    metadata: dict | None = Field({}, description="Cell-specific metadata.")


# Code cell model
class NotebookCodeCellModel(NotebookCellModel):
    cell_type: str = "code"
    source: list[str] = Field(..., description="The source code inside the code cell.")
    execution_count: int | None = Field(None, description="The execution count of the cell.")
    outputs: list[NotebookOutputModel] | None = Field(
        None, description="Outputs produced by this code cell."
    )


# Markdown cell model
class NotebookMarkdownCellModel(NotebookCellModel):
    cell_type: str = "markdown"
    source: list[str] = Field(..., description="Markdown text inside the cell.")


# Raw cell model
class NotebookRawCellModel(NotebookCellModel):
    cell_type: str = "raw"
    source: list[str] = Field(..., description="Raw content inside the cell.")


# Root model for the entire notebook file
class NotebookFileModel(DSLModel):
    metadata: NotebookMetadataModel
    cells: list[NotebookCodeCellModel | NotebookMarkdownCellModel | NotebookRawCellModel]

    @classmethod
    def from_ipynb_file(cls, file_path: str) -> "NotebookFileModel":
        return cls.load(file_path, file_format="json")

    def to_ipynb_file(self, file_path: str) -> None:
        self.save(file_path, file_format="json")


# New class for generating IPython notebooks
class IPythonNotebookGenerator(DSLModel):
    notebook: NotebookFileModel = Field(..., description="Filesystem reference")

    def __init__(
        self,
        metadata: NotebookMetadataModel = None,
        cells: list[
            NotebookCodeCellModel | NotebookMarkdownCellModel | NotebookRawCellModel
        ] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.notebook = NotebookFileModel(metadata=metadata, cells=cells)

    def save_notebook(self, file_path: str) -> None:
        """Saves the notebook to a file."""
        self.notebook.to_ipynb_file(file_path)

    @classmethod
    def load_notebook(cls, file_path: str) -> "IPythonNotebookGenerator":
        """Loads a notebook from a file."""
        notebook_model = NotebookFileModel.from_ipynb_file(file_path)
        return cls(metadata=notebook_model.metadata, cells=notebook_model.cells)

    def add_code_cell(self, source: list[str], execution_count: int | None = None) -> None:
        """Adds a code cell to the notebook."""
        code_cell = NotebookCodeCellModel(source=source, execution_count=execution_count)
        self.notebook.cells.append(code_cell)

    def add_markdown_cell(self, source: list[str]) -> None:
        """Adds a markdown cell to the notebook."""
        markdown_cell = NotebookMarkdownCellModel(source=source)
        self.notebook.cells.append(markdown_cell)

    def add_raw_cell(self, source: list[str]) -> None:
        """Adds a raw cell to the notebook."""
        raw_cell = NotebookRawCellModel(source=source)
        self.notebook.cells.append(raw_cell)


def main():
    """Main function"""
    from dslmodel import init_instant

    init_instant()

    import pyperclip

    content = pyperclip.paste()
    print(content)

    note = IPythonNotebookGenerator.from_prompt(content)
    print(note)


if __name__ == "__main__":
    main()
