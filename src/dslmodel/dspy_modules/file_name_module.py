import dspy
import pyperclip
from typer import Typer
from inflection import underscore, dasherize
from datetime import datetime

from dslmodel.utils.str_tools import pythonic_str
from zipp import Path

app = Typer(
    help="Generate a file name from any text, with optional timestamp and safe file format handling."
)

# Define safe time formats for filenames (no invalid characters)
class TimeFormats:
    ISO_LIKE = "%Y-%m-%dT%H%M%S"                    # 2024-09-27T153000 (ISO-like without colons)
    YEAR_MONTH_DAY_UNDERSCORE = "%Y-%m-%d"          # 2024-09-27
    FULL_DATETIME_UNDERSCORE = "%Y-%m-%d-%H%M%S"    # 2024-09-27-153000
    YEAR_MONTH_DAY_COMPACT = "%Y%m%d"               # 20240927 (Compact date only)
    DATE_HOUR_MIN_SEC_COMPACT = "%Y%m%d-%H%M%S"     # 20240927-153000
    TIME_ONLY = "%H%M%S"                            # 153000 (Time only)
    HUMAN_READABLE_UNDERSCORE = "%B-%d-%Y"          # September-27-2024 (Human-readable, safe)
    YEAR_MONTH = "%Y-%m"                            # 2024-09 (Year and month only)


class WindowsSafeFileName(dspy.Signature):
    """
    Generate a Windows-safe filename from file content without adding the file extension.
    Ensures the filename complies with Windows naming conventions and restrictions.
    """

    file_content = dspy.InputField(desc="Text content that needs to be converted to a valid Windows-safe filename.")
    safe_filename = dspy.OutputField(desc="The generated Windows-safe filename.", prefix="filename:")


class FileContentToFileNameModule(dspy.Module):
    """Converts file content to a safe file name with an optional timestamp and extension."""

    def __init__(self, extension: str = None, time_format: str = None, add_timestamp: bool = False):
        super().__init__()
        self.extension = extension
        self.time_format = time_format
        self.add_timestamp = add_timestamp

    def forward(self, file_content: str) -> str:
        """
        Converts the provided file content to a valid filename with the specified extension.
        Optionally appends a timestamp using a specified time format.
        """
        # Chain of Thought to generate a valid file name
        pred = dspy.ChainOfThought(WindowsSafeFileName)

        # Generate the file name from the content
        result = pred(file_content=file_content).safe_filename
        result = result.replace(" ", "-")

        # Convert to snake_case if the extension is .py
        if self.extension == "py":
            result = pythonic_str(result)

        # Add a timestamp if required
        if self.add_timestamp and self.time_format:
            current_time = datetime.now().strftime(self.time_format)
            result = f"{result}_{current_time}"

        # Append the extension to the file name if provided
        if self.extension:
            result = f"{result}.{self.extension}"

        return result


def file_name_call(file_content: str, extension: str = None, time_format: str = TimeFormats.YEAR_MONTH_DAY_UNDERSCORE, add_timestamp: bool = False) -> str:
    """Generates the file name from content with an optional timestamp and file extension."""
    file_content_to_file_name = FileContentToFileNameModule(
        extension=extension, time_format=time_format, add_timestamp=add_timestamp
    )
    return file_content_to_file_name.forward(file_content=file_content)


def main():
    # Get file content from clipboard (or initialize with other input)
    from dspygen.utils.dspy_tools import init_versatile
    init_versatile()
    file_content = pyperclip.paste()

    # Example usage of file_name_call with a timestamp
    file_name = file_name_call(
        file_content=file_content,
        extension="md",  # Example: Python file extension
        time_format=TimeFormats.FULL_DATETIME_UNDERSCORE,  # Example safe timestamp format
        add_timestamp=True
    ) 

    print(file_name)

    # write the file to my obsidian vault
    file_path = "/Users/sac/dev/vault/myvault/" + file_name
    with open(file_path, "w") as file:
        file.write(file_content)

@app.command()
def call(file_content: str, extension: str = None, add_timestamp: bool = False, time_format: str = None):
    """CLI command to convert file content to a file name with optional timestamp."""
    file_name = file_name_call(
        file_content=file_content,
        extension=extension,
        time_format=time_format if time_format else TimeFormats.YEAR_MONTH_DAY_UNDERSCORE,
        add_timestamp=add_timestamp
    )
    print(file_name)



def watch_clipboard():
    """Watch the clipboard for changes and call the main function when it changes."""
    clipboard_content = pyperclip.paste()

    while True:
        new_clipboard_content = pyperclip.paste()
        if new_clipboard_content != clipboard_content:
            import time
            time.sleep(0.01)  # Sleep for 0.01 seconds to ensure clipboard content is fully updated
            clipboard_content = new_clipboard_content
            main()
    

if __name__ == "__main__":
    # For running via CLI
    watch_clipboard()  # For direct execution
    # Uncomment below to use the Typer CLI:
    # app()
