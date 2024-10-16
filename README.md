# DSLModel

[![Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/your-username/dslmodel) [![GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://github.com/codespaces/new/your-username/dslmodel)

```sh
pip install dslmodel
```

## Custom GPT: [DSLModel Assistant v2024.10.10](https://chatgpt.com/g/g-vmfFW8Xgk-dslmodel-assistant-v2024-10-10)

## Overview

**DSLModel** is a powerful Python framework for declarative model creation using templates and concurrent execution. Built atop `Pydantic` for data validation and `DSPy` for model execution, DSLModel streamlines the development of dynamic models with features like:

- **Dynamic Field Generation:** Utilize Jinja2 templates for flexible model definitions.
- **Concurrent Execution:** Leverage concurrent processing to optimize performance.
- **Workflow Management:** Define and execute complex workflows with conditional logic and loops.
- **Finite State Machines:** Incorporate state machine patterns for managing state transitions.
- **Data Handling Utilities:** Read from and write to various data formats seamlessly.
- **Notebook Generation:** Programmatically create and manage IPython notebooks.
- **AI-Assisted Development:** Enhance productivity with AI-driven tools for code generation.

## Table of Contents

- [DSLModel](#dslmodel)
  - [Custom GPT: DSLModel Assistant v2024.10.10](#custom-gpt-dslmodel-assistant-v20241010)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Getting Started](#getting-started)
    - [Defining Models](#defining-models)
    - [Generating Data from Templates](#generating-data-from-templates)
    - [Concurrent Execution](#concurrent-execution)
    - [Workflow Management](#workflow-management)
    - [Workflow YAML](#workflow-yaml)
    - [Finite State Machines](#finite-state-machines)
    - [Data Handling](#data-handling)
    - [Notebook Generation](#notebook-generation)
  - [Architecture](#architecture)
    - [Core Components](#core-components)
    - [Data Flow](#data-flow)
  - [Development](#development)
    - [Setup](#setup)
    - [Testing](#testing)
    - [Contributing](#contributing)
  - [Deployment](#deployment)
    - [Deployment Pipeline](#deployment-pipeline)
  - [License](#license)
  - [Contact](#contact)

## Installation

Ensure you have Python 3.12 or higher installed. Then, install DSLModel via pip:

```sh
pip install dslmodel
```

Alternatively, install from source:

```sh
git clone https://github.com/your-username/dslmodel.git
cd dslmodel
poetry install
```

## Getting Started

### Defining Models

Create dynamic models using Jinja2 templates and `DSLModel`.

```python
from typing import List
from pydantic import Field
from dslmodel import DSLModel


class Participant(DSLModel):
    """Represents a participant in a meeting."""
    name: str = Field("{{ fake_name() }}", description="Name of the participant.")
    role: str = Field("{{ fake_job() }}", description="Role of the participant.")

class Meeting(DSLModel):
    """Represents a meeting and its participants."""
    name: str = Field(..., description="Name of the meeting.")
    participants: List[Participant] = Field(..., description="List of participants.")
```

### Generating Data from Templates

Use templates to generate model instances with dynamic content.

```python
from typing import List, Optional, Dict, Union
from pydantic import Field

from dslmodel import init_lm, DSLModel


class Participant(DSLModel):
    """Represents a participant in a meeting."""
    name: str = Field("{{ fake_name() }}", description="Name of the participant.")
    role: str = Field("{{ fake_job() }}", description="Role of the participant.")


class Meeting(DSLModel):
    """Represents a meeting, its participants, agenda, and other details."""
    name: str = Field(..., description="Name of the meeting.")
    meeting_date: str = Field(..., description="Date of the meeting.")
    location: Optional[str] = Field(None, description="Location where the meeting is held.")
    chairperson: Participant = Field(..., description="Chairperson of the meeting.")
    secretary: Participant = Field(..., description="Secretary responsible for taking minutes.")
    participants: List[Participant] = Field(..., description="List of all participants in the meeting.")
    agenda: List[str] = Field(..., description="Agenda items for the meeting.", min_length=3)
    minutes: List[str] = Field(..., description="Minutes of the meeting. Time, Description", min_length=3)
    rules_of_order: List[str] = Field(..., description="Rules governing the meeting.", min_length=3)


participants = [Participant() for _ in range(5)]  # Created using Jinja defaults (no LM)

# Generate the Meeting 
init_lm()  # Sets the lm to gpt-4o-mini


meeting_template = """
Fortune 500 Meeting about {{ fake_bs() }}
Participants:
{% for participant in participants %}
- {{ participant.name }} ({{ participant.role }})
{% endfor %}
"""

meeting_instance = Meeting.from_prompt(meeting_template, participants=participants)

print(meeting_instance.to_yaml())
```

### Concurrent Execution

Execute multiple tasks concurrently to improve performance.

```python
from dslmodel import init_lm, DSLModel
from dslmodel.utils.model_tools import run_dsls
from pydantic import Field


class Participant(DSLModel):
    """Represents a participant in a meeting."""
    name: str = Field(..., description="Name of the participant.")
    role: str = Field(..., description="Role of the participant.")


tasks = [(Participant, "Create a person with a name and job role") for _ in range(5)]

init_lm()  # Sets the lm to gpt-4o-mini

results = run_dsls(tasks, max_workers=5)

for i, result in enumerate(results):
    print(f"Participant {i+1}: {result}")
```

### Workflow Management

Define and execute complex workflows using `Workflow`, `Job`, and `Action`.

```python
from dslmodel.workflow import Workflow, Job, Action, Condition, CronTrigger

condition = Condition(expr="len(participants) > 3")

action1 = Action(
    name="Generate Participants",
    code="participants.extend([Participant() for _ in range(5)])"
)

action2 = Action(
    name="Notify Organizer",
    code="print('Organizer notified.')",
    cond=condition
)

job = Job(
    name="Setup Meeting",
    steps=[action1, action2]
)

trigger = CronTrigger(cron="0 9 * * MON")  # Every Monday at 9 AM

workflow = Workflow(
    name="Weekly Meeting Setup",
    triggers=[trigger],
    jobs=[job],
    context={"participants": []}
)

workflow.execute()
```

### Workflow YAML

```yaml
workflow:
  name: "Weekly Meeting Setup"
  triggers:
    - type: "CronTrigger"
      cron: "0 9 * * MON"  # Every Monday at 9 AM
  context:
    participants: []
  jobs:
    - name: "Setup Meeting"
      steps:
        - name: "Generate Participants"
          code: "participants.extend([Participant() for _ in range(5)])"
        - name: "Notify Organizer"
          code: "print('Organizer notified.')"
          condition:
            expr: "len(participants) > 3"
```

### Finite State Machines

Manage state transitions using `FSMMixin`.


```python
import logging
from enum import Enum, auto
from dslmodel.mixins import FSMMixin, trigger

class SalesState(Enum):
    INITIALIZING = auto()
    RESEARCHING = auto()
    OUTREACHING = auto()
    CLOSING = auto()
    COMPLETING = auto()


class ChallengerSalesAgent(FSMMixin):
    def __init__(self):
        super().__init__()
        self.setup_fsm(state_enum=SalesState, initial=SalesState.INITIALIZING)

    @trigger(source=SalesState.INITIALIZING, dest=SalesState.RESEARCHING)
    def start_research(self):
        print("Starting market research.")

    @trigger(source=SalesState.RESEARCHING, dest=SalesState.OUTREACHING)
    def conduct_outreach(self):
        print("Conducting outreach to leads.")

    @trigger(source=SalesState.OUTREACHING, dest=SalesState.CLOSING)
    def close_deal(self):
        print("Closing the deal with the client.")

    @trigger(source=SalesState.CLOSING, dest=SalesState.COMPLETING)
    def complete_sale(self):
        print("Completing the sale.")

    def forward(self, prompt, **kwargs):
        super().forward(prompt, **kwargs)
        print(f"Processing prompt: {prompt}")


def main():
    agent = ChallengerSalesAgent()
    print("Initial state:", agent.state)

    # Simulating the simplified flow of the sales process
    agent.forward("start researching the market")
    print("State after research:", agent.state)

    agent.forward("reach out to leads")
    print("State after outreach:", agent.state)

    agent.forward("finalize the deal")
    print("State after closing the deal:", agent.state)

    agent.forward("complete the sale")
    print("Final state:", agent.state)


if __name__ == '__main__':
    main()
```

### Data Handling

Read from and write to various data formats using `DataReader` and `DataWriter`.

```python
from dslmodel import DataReader, DataWriter

# Reading data
data_reader = DataReader(file_path="data/sample_data.csv")
data = data_reader.forward()
print(data)

# Writing data
data_writer = DataWriter(data=data, file_path="output/data_output.csv")
data_writer.forward()
```

### Notebook Generation

Programmatically create and manage IPython notebooks.

```python
from dslmodel.generators import IPythonNotebookGenerator


# The generator is a DSLModel, so it can be used like any other DSLModel
notebook_gen = IPythonNotebookGenerator()

# Add a markdown cell
notebook_gen.add_markdown_cell(["# Welcome to DSLModel Notebook", "Demonstrating notebook generation."])

# Add a code cell
notebook_gen.add_code_cell(["print('Hello, DSLModel!')"])

# Save the notebook
notebook_gen.save("notebooks/demo_notebook.ipynb")
```

## Architecture

### Core Components

- **DSLModel:** Core framework for declarative model creation using templates.
- **Mixins:**
  - `ToolMixin`: Adds dynamic tool execution capabilities.
  - `FSMMixin`: Provides finite state machine functionality.
- **Workflow Components:**
  - `Workflow`, `Job`, `Action`, `Condition`, `CronTrigger`: Orchestrate complex workflows.
- **Data Handling Utilities:**
  - `DataReader`, `DataWriter`: Handle data ingestion and output.
- **Notebook Models:**
  - `IPythonNotebookGenerator`: Generate and manage IPython notebooks.

### Data Flow

```
User Inputs -> DSLModel Templates -> Generated Models -> Validation and Execution
```

## Development

### Setup

1. **Clone the Repository**

   ```sh
   git clone https://github.com/your-username/dslmodel.git
   cd dslmodel
   ```

2. **Install Dependencies**

   ```sh
   poetry install
   ```

3. **Configure Environment Variables**

   Create a `.env` file and add necessary environment variables, such as `OPENAI_API_KEY`.

4. **Run the Development Server**

   ```sh
   poe api --dev
   ```

### Testing

Run tests using `pytest`:

```sh
poetry run pytest
```

Ensure test coverage is at least 90%.

### Contributing

Contributions are welcome! Please follow the [contribution guidelines](CONTRIBUTING.md) and adhere to the code of conduct.

## Deployment

DSLModel utilizes GitHub Actions for continuous integration and deployment.

### Deployment Pipeline

1. **Code Push:** Developers push code to the repository.
2. **Automated Testing:** GitHub Actions run test suites.
3. **Linting:** Code is linted using `ruff` to maintain quality.
4. **Build and Deployment:** Successful builds are deployed to staging or production.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Contact

- **Project Link:** [https://github.com/your-username/dslmodel](https://github.com/your-username/dslmodel)
- **Issues:** [https://github.com/your-username/dslmodel/issues](https://github.com/your-username/dslmodel/issues)

---

By following this guide, you can effectively utilize DSLModel for declarative model creation, workflow management, data handling, state machine implementation, and AI-assisted development.