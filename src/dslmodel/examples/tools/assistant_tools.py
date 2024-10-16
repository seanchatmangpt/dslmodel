from dslmodel.mixins.tools import ToolMixin, MetaToolMixin


class UtilityFunctions(ToolMixin):
    """Provides utility functions like getting time, generating random numbers, and running code."""

    def get_current_time(self):
        """Returns the current time."""
        from datetime import datetime
        return datetime.now()

    def get_random_number(self):
        """Returns a random number between 1 and 100."""
        import random
        return random.randint(1, 100)

    def open_browser(self, url: str):
        """Opens a browser tab with the provided URL."""
        import webbrowser
        webbrowser.open(url)

    def generate_diagram(self, prompt: str):
        """Generates a mermaid diagram based on the given prompt."""
        return f"```mermaid\n{prompt}\n```"

    def runnable_code_check(self, file_path: str):
        """Checks if the code in the file is runnable and suggests necessary changes if not."""
        try:
            with open(file_path, "r") as f:
                code = f.read()
                compile(code, file_path, "exec")
            return "The code is runnable."
        except Exception as e:
            return f"Error: {e}. Suggested fixes: [Provide solution here]."

    def run_python(self, script_name: str):
        """Executes a Python script from the scratch_pad_dir and returns the output."""
        import subprocess
        result = subprocess.run(["python", script_name], capture_output=True, text=True)
        return result.stdout or result.stderr


class BrowserFileOperations(ToolMixin):
    """Manages file operations and browser-based interactions."""

    def create_file(self, file_name: str, content: str):
        """Creates a new file with the specified content."""
        with open(file_name, "w") as f:
            f.write(content)
        return f"File '{file_name}' created."

    def update_file(self, file_name: str, new_content: str):
        """Updates the specified file with new content."""
        with open(file_name, "a") as f:
            f.write("\n" + new_content)
        return f"File '{file_name}' updated."

    def delete_file(self, file_name: str):
        """Deletes the specified file."""
        import os
        os.remove(file_name)
        return f"File '{file_name}' deleted."

    def discuss_file(self, file_name: str):
        """Discusses the content of the specified file."""
        with open(file_name, "r") as f:
            content = f.read()
        return f"File '{file_name}' content: \n{content}"

    def read_file_into_memory(self, file_name: str):
        """Reads the content of a file into memory."""
        with open(file_name, "r") as f:
            content = f.read()
        return {file_name: content}

    def read_dir_into_memory(self, dir_path: str):
        """Reads all files in the specified directory into memory."""
        import os
        memory = {}
        for file_name in os.listdir(dir_path):
            with open(os.path.join(dir_path, file_name), "r") as f:
                memory[file_name] = f.read()
        return memory


class MemoryManagement(ToolMixin):
    """Handles operations related to memory management."""

    memory = {}

    def clipboard_to_memory(self, clipboard_content: str):
        """Copies the content from the clipboard to memory."""
        self.memory["clipboard"] = clipboard_content
        return "Clipboard content saved to memory."

    def add_to_memory(self, key: str, value: str):
        """Adds a key-value pair to memory."""
        self.memory[key] = value
        return f"Added '{key}' to memory."

    def remove_variable_from_memory(self, key: str):
        """Removes a variable from memory."""
        if key in self.memory:
            del self.memory[key]
            return f"Removed '{key}' from memory."
        return f"Key '{key}' not found in memory."

    def reset_active_memory(self):
        """Resets the active memory to an empty dictionary."""
        self.memory.clear()
        return "Memory reset."


class InformationSourcing(ToolMixin):
    """Handles information gathering and file-saving tasks."""

    def scrap_to_file_from_clipboard(self, url: str, file_name: str):
        """Scrapes content from a URL and saves it to a file."""
        import requests
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(file_name, "w") as f:
                f.write(response.text)
            return f"Content from {url} saved to '{file_name}'."
        except Exception as e:
            return f"Error scraping content: {e}. Make sure FIRECRAWL_API_KEY is set if required."


class CodeAssistant(MetaToolMixin):
    utils = UtilityFunctions()
    file_ops = BrowserFileOperations()
    memory_ops = MemoryManagement()
    info_src = InformationSourcing()
