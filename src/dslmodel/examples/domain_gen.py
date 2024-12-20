from dslmodel.utils.file_tools import data_dir
from dslmodel.spreadsheet import DSLSpreadsheet
from pydantic import Field
from dslmodel import DSLModel
from dslmodel.generators import IPythonNotebookGenerator
import pyperclip

# Step 1: Initialize Notebook Generator
notebook_gen = IPythonNotebookGenerator()

# Step 2: Add Introduction Markdown Cell
notebook_gen.add_markdown_cell([
    "# Domain List Notebook",
    "This notebook demonstrates how to load domain data from a CSV file, "
    "convert it to YAML format, and display the data."
])

# Step 3: Add Model Definitions Cell
notebook_gen.add_code_cell([
    "from pydantic import Field",
    "from dslmodel import DSLModel",
    "",
    "# Define the Domain model to represent each domain entry",
    "class Domain(DSLModel):",
    "    name: str = Field(..., alias='Domain Name')",
    "",
    "# Define the Domains model to hold a list of Domain entries",
    "class Domains(DSLModel):",
    "    domains: list[Domain]",
])

# Step 4: Add Data Loading Cell
notebook_gen.add_code_cell([
    "from dslmodel.spreadsheet import DSLSpreadsheet",
    "from dslmodel.utils.file_tools import data_dir",
    "",
    "# Load data from a CSV file",
    "sheet = DSLSpreadsheet(data_dir('domain_list.csv'), dsl_model=Domain)",
    "domains = Domains(domains=sheet.results)",
    "",
    "# Preview the loaded data",
    "print(domains)"
])

# Step 5: Add YAML Conversion and Clipboard Copy Cell
notebook_gen.add_code_cell([
    "import pyperclip",
    "",
    "# Convert the domains data to YAML format",
    "yaml_content = domains.to_yaml()",
    "",
    "# Copy YAML content to clipboard for easy access",
    "pyperclip.copy(yaml_content)",
    "",
    "# Display the YAML content in the notebook",
    "print(yaml_content)"
])


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()

    # Step 6: Save the Notebook
    notebook_gen.save("domain_list_full_demo.ipynb")

    print("Notebook generated and saved as 'domain_list_full_demo.ipynb'.")


if __name__ == '__main__':
    main()
