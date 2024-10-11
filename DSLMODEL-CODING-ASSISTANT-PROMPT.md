# DSLMODEL-CODING-ASSISTANT-PROMPT.md

from dslmodel.mixins.tool_mixin import ToolMixin
from dslmodel.mixins.fsm_mixin import FSMMixin
from dslmodel.generators.dsl_class_generator import DSLClassGenerator
from dslmodel.workflow import Workflow, Job, Action, Condition, Loop, CronTrigger, DateTrigger
from dslmodel.utils.file_tools import DataReader, DataWriter
from dslmodel.utils.context_generator import DataFrameContextGenerator, FileNameModel
from dslmodel.notebook_models import (
    NotebookMetadataModel,
    NotebookOutputModel,
    NotebookCellModel,
    NotebookCodeCellModel,
    NotebookMarkdownCellModel,
    NotebookRawCellModel,
    NotebookFileModel,
    IPythonNotebookGenerator
)

ToolMixin is a mixin for tools in DSLModel, containing a list of Tool instances and an ignore_list. It initializes tools by inspecting methods, adding Tool instances based on method attributes.

FSMMixin provides finite state machine capabilities within DSLModel, allowing for state transitions, trigger handling, and integration with workflow actions.

DSLClassGenerator automates the creation of DSLModel classes based on natural language prompts, utilizing templates and handling file operations to streamline model development.

Workflow is a DSLModel orchestrating Jobs based on defined Triggers, handling imports, job ordering, and maintaining execution context.

Job is a DSLModel grouping multiple Actions with name, dependencies, runner, steps, environment variables, and retry configurations.

Action is a DSLModel representing a workflow action with name, use, args, code, env, cond, and loop.

Condition is a DSLModel with an expression string used to evaluate conditions for actions in workflows.

Loop is a DSLModel defining a loop structure with 'over' specifying the iterable and 'var' as the loop variable.

CronTrigger is a DSLModel specifying a cron-based trigger with type 'cron' and a cron expression.

DateTrigger is a DSLModel specifying a date-based trigger with type 'date' and a run_date.

DataReader is a DSPy.Retrieve model supporting multiple file types for data ingestion. It initializes by reading data from a file path with an optional SQL query and returns data as a list of dictionaries.

DataWriter is a DSLModel handling data output to various file types. It initializes with data, file_path, and write_options, and writes data to the specified file, handling CSV and Markdown formats with ID column management.

DataFrameContextGenerator is a DSLModel generating context from a pandas DataFrame, including descriptive statistics and data types information.

FileNameModel is a DSLModel generating unique filenames based on data context, ensuring proper file extensions and naming conventions.

NotebookMetadataModel is a DSLModel containing notebook metadata with kernelspec and language_info.

NotebookOutputModel is a DSLModel representing notebook cell outputs with output_type, text, data, name, and execution_count.

NotebookCellModel is a base DSLModel for notebook cells with cell_type and metadata.

NotebookCodeCellModel is a NotebookCellModel of type 'code' with source, execution_count, and outputs.

NotebookMarkdownCellModel is a NotebookCellModel of type 'markdown' with source.

NotebookRawCellModel is a NotebookCellModel of type 'raw' with source.

NotebookFileModel is a DSLModel representing an entire notebook with metadata and cells. It includes methods to load from and save to .ipynb files.

IPythonNotebookGenerator is a DSLModel for generating IPython notebooks. It contains a NotebookFileModel and methods to save, load, and add different types of cells (code, markdown, raw).

