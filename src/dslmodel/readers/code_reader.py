import dspy
from pathlib import Path
from fnmatch import fnmatch

from dspy import Prediction

import wcmatch.glob as wglob

import dspy
import typer


class CodeReader(dspy.Retrieve):
    def __init__(self, path, gitignore=None, max_depth=None):
        super().__init__()
        self.path = Path(path)
        self.max_depth = max_depth
        self.gitignore = Path(gitignore) if gitignore else self.path / ".gitignore"
        self.gitignore_patterns = self.parse_gitignore(self.gitignore)
        self.gitignore_patterns.add(".git")

    def parse_gitignore(self, gitignore_path):
        if not gitignore_path.exists():
            return set()

        with gitignore_path.open("r", encoding="utf-8") as file:
            patterns = set(
                line.strip() for line in file if line.strip() and not line.startswith("#")
            )
        return patterns

    def forward(self, query = None) -> list[str] | Prediction | list[Prediction]:
        content = []
        file_dict = {}

        # Use wcmatch.WcMatch to search for files
        flags = wglob.GLOBSTAR | wglob.IGNORECASE

        # Setup the walker with respect to the max_depth
        for file_path in wglob.iglob(
                str(self.path / "**"),
                flags=flags,
                exclude=self.gitignore_patterns,
                depth=(0 if self.max_depth is None else self.max_depth)
        ):
            file_path = Path(file_path)

            # Apply additional filters
            if (
                    file_path.is_file()
                    and not self.is_binary(file_path)
                    and (not query or self.is_filtered(file_path, query))
            ):
                try:
                    print(file_path)
                    with file_path.open("r", encoding="utf-8") as f:
                        file_content = f.read()
                        file_dict[file_path] = file_content
                except UnicodeDecodeError:
                    continue

                file_info = self.extract_file_info(file_path)
                content.append(file_info + file_content + "\n```\n\n")

        return dspy.Prediction(passages=content, file_dict=file_dict)

    def is_filtered(self, file_path, query):
        # Use wcmatch.fnmatch to check if file matches the query
        return wglob.globmatch(str(file_path), query)

    def is_binary(self, file_path):
        try:
            with open(file_path, "rb") as file:
                return b"\x00" in file.read(1024)
        except IOError:
            return False

    def extract_file_info(self, file_path):
        file_extension = file_path.suffix.lstrip('.')
        file_info = f"## File: {file_path}\n\n```{file_extension}\n"
        return file_info


def get_files_from_directory(directory, query, gitignore=None, max_depth=None):
    """Retrieves code snippets from a specified directory using CodeReader."""
    code_retriever = CodeReader(directory, gitignore, max_depth)
    result = code_retriever.forward(query)
    return result.passages  # Return the list of file contents


def main(directory: str, query: str, gitignore: str = None, max_depth: int = None):
    # Initialize OpenAI LLM and DSPy settings
    init_ol(model="phi3", max_tokens=2000)

    # Instantiate CodeReader
    code_retriever = CodeReader(directory, gitignore, max_depth)

    # Retrieve and print results
    result = code_retriever.forward(query)
    for file_content in result.passages:
        print(file_content)


if __name__ == '__main__':
    typer.run(main)

# def main():
#     init_ol(model="phi3", max_tokens=2000)
#     #init_dspy(model="gpt-4o", max_tokens=3000)
#     path = "/Users/sac/dev/nuxt-ai-chatbot/stores"
#     gitignore = "/.gitignore"  # Optional
#
#     code_retriever = CodeReader(path, gitignore)
#     result = code_retriever.forward("*.py") # and only the code after ```python and ending with ``` ")
#     print(result.passages)
#
#     for file_content in result.passages:
#         #from sungen.dspy_modules.nuxt_module import nuxt_call
#         print(file_content)
#         #nuxt = nuxt_call(path=path, readme=file_content)
#         #print(nuxt)
# for file_content in result.passages:
#     print(file_content)  # Here, you can instead write to a Markdown file or process further.

# If I want one file containing all the code snippets
# with open("code_snippets.md", "w") as f:
#     for file_content in result.passages:
#         f.write(file_content)


# if __name__ == '__main__':
#     main()


import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Any
import typer

from dslmodel.utils.dspy_tools import init_lm, init_instant

# Initialize Typer application
app = typer.Typer()


def query_python_files(directory: str, gitignore: str = None) -> List[str]:
    """Find all Python files in the directory."""
    return get_files_from_directory(directory, "*.py", gitignore)


def query_markdown_files(directory: str, gitignore: str = None) -> List[str]:
    """Find all Markdown files in the directory."""
    return get_files_from_directory(directory, "*.md", gitignore)


def query_large_files(directory: str, size_threshold: int, gitignore: str = None) -> List[str]:
    """Find all files larger than a specified size."""
    result = []
    for file_path in wglob.iglob(str(Path(directory) / "**"), flags=wglob.GLOBSTAR | wglob.RECURSIVE):
        if Path(file_path).is_file() and (os.path.getsize(file_path) > size_threshold):
            result.append(str(file_path))
    return result


def query_recent_files(directory: str, days: int, gitignore: str = None) -> List[str]:
    """Find files modified within a specific number of days."""
    cutoff_time = datetime.now() - timedelta(days=days)
    result = []
    for file_path in wglob.iglob(str(Path(directory) / "**"), flags=wglob.GLOBSTAR | wglob.RECURSIVE):
        if Path(file_path).is_file() and datetime.fromtimestamp(os.path.getmtime(file_path)) > cutoff_time:
            result.append(str(file_path))
    return result


def query_ignored_files(directory: str, gitignore: str = None) -> List[str]:
    """List all files that match patterns in .gitignore."""
    code_retriever = CodeReader(directory, gitignore)
    return [str(path) for path in code_retriever.gitignore_patterns]


def query_binary_files(directory: str, gitignore: str = None) -> List[str]:
    """Find binary files in the directory."""
    result = []
    code_retriever = CodeReader(directory, gitignore)
    for file_path in wglob.iglob(str(Path(directory) / "**"), flags=wglob.GLOBSTAR | wglob.RECURSIVE):
        if Path(file_path).is_file() and code_retriever.is_binary(Path(file_path)):
            result.append(str(file_path))
    return result


def query_files_with_pattern(directory: str, pattern: str, gitignore: str = None) -> List[str]:
    """Find files containing a specific text pattern."""
    result = []
    code_retriever = CodeReader(directory, gitignore)
    for file_path in wglob.iglob(str(Path(directory) / "**"), flags=wglob.GLOBSTAR | wglob.RECURSIVE):
        if Path(file_path).is_file() and pattern in Path(file_path).read_text(encoding="utf-8", errors="ignore"):
            result.append(str(file_path))
    return result


def main(directory: str, query_type: str, size: int = 1024, days: int = 7, pattern: str = "", gitignore: str = None):
    # Initialize LLM configuration
    init_instant()

    if query_type == "python":
        results = query_python_files(directory, gitignore)
    elif query_type == "markdown":
        results = query_markdown_files(directory, gitignore)
    elif query_type == "large":
        results = query_large_files(directory, size, gitignore)
    elif query_type == "recent":
        results = query_recent_files(directory, days, gitignore)
    elif query_type == "ignored":
        results = query_ignored_files(directory, gitignore)
    elif query_type == "binary":
        results = query_binary_files(directory, gitignore)
    elif query_type == "pattern":
        results = query_files_with_pattern(directory, pattern, gitignore)
    else:
        print(f"Unknown query type: {query_type}")
        return

    for result in results:
        print(result)


if __name__ == "__main__":
    typer.run(main)
