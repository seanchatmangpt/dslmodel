"""IPython notebook generator module."""
from typing import List, Optional
import json
from pathlib import Path

class IPythonNotebookGenerator:
    """A class for generating IPython notebooks programmatically."""
    
    def __init__(self):
        """Initialize the notebook generator."""
        self.cells: List[dict] = []
        self.metadata = {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12.2"
            }
        }
    
    def add_markdown_cell(self, content: List[str]) -> None:
        """Add a markdown cell to the notebook.
        
        Args:
            content: List of strings to include in the markdown cell
        """
        self.cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": "\n".join(content)
        })
    
    def add_code_cell(self, content: List[str], outputs: Optional[List[dict]] = None) -> None:
        """Add a code cell to the notebook.
        
        Args:
            content: List of strings to include in the code cell
            outputs: Optional list of cell outputs
        """
        self.cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": outputs or [],
            "source": "\n".join(content)
        })
    
    def save(self, filename: str) -> None:
        """Save the notebook to a file.
        
        Args:
            filename: The name of the file to save to
        """
        notebook = {
            "cells": self.cells,
            "metadata": self.metadata,
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        with open(filename, 'w') as f:
            json.dump(notebook, f, indent=1) 