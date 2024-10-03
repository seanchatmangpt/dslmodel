# dslmodel

`dslmodel` is a framework for declarative model creation using templates and concurrent execution, built on top of the `pydantic` and `dspy` library. It provides tools to generate models with dynamic fields and execute tasks concurrently.

[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/to/do) [![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://github.com/codespaces/new/to/do)

## Installing

To install this package, run:

```sh
pip install dslmodel
```

## Using

To view the CLI help information, run:

```sh
dsl --help
```

## Example Usage

### Defining Models

You can define models with dynamic fields using Jinja templates, and then instantiate these models using the provided tools.

```python
from typing import List
from pydantic import Field
from dslmodel import DSLModel

class Participant(DSLModel):
    """Represents a participant in a meeting."""
    name: str = Field("{{ fake_name() }}", description="Name of the participant.")
    role: str = Field("{{ fake_job() }}", description="Role of the participant.")

class Meeting(DSLModel):
    """Represents a meeting, its participants, and other details."""
    name: str = Field(..., description="Name of the meeting.")
    participants: List[Participant] = Field(..., description="List of participants.")
```

### Generating Data from a Template

Here's how you can use a Jinja template to dynamically generate meeting details, including participants with fake data:

```python
meeting_template = """
Fortune 500 Meeting about {{ fake_bs() }}
Participants: 
{% for participant in participants %}
  - {{ participant.name }} ({{ participant.role }})
{% endfor %}
"""

# Create participants
participants = [Participant() for _ in range(5)]

# Generate the meeting instance
meeting_instance = Meeting.from_prompt(meeting_template, participants=participants)

# Output the meeting in YAML format
print(meeting_instance.to_yaml())
```

### Concurrent Execution with `run_dsls`

You can generate multiple participants concurrently using the `run_dsls` function:

```python
from dslmodel.utils.model_tools import run_dsls

def create_participants_concurrently():
    tasks = [(Participant, "{{ fake_name() }} - {{ fake_job() }}") for _ in range(5)]
    
    # Run the tasks concurrently
    results = run_dsls(tasks, max_workers=5)

    for i, result in enumerate(results):
        print(f"Participant {i+1}: {result}")

# Create participants concurrently
create_participants_concurrently()
```

### Saving and Loading Models

You can save your generated model instances to a file and reload them as needed:

```python
# Save the meeting instance to a YAML file
meeting_instance.save(file_path="meeting_output.yaml")

# Load the meeting instance from the saved YAML file
loaded_meeting = Meeting.from_yaml("meeting_output.yaml")

# Display loaded content
print(loaded_meeting.to_yaml())
```

## Contributing

<details>
<summary>Prerequisites</summary>

<details>
<summary>1. Set up Git to use SSH</summary>

1. [Generate an SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) and [add the SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
1. Configure SSH to automatically load your SSH keys:
    ```sh
    cat << EOF >> ~/.ssh/config
    
    Host *
      AddKeysToAgent yes
      IgnoreUnknown UseKeychain
      UseKeychain yes
      ForwardAgent yes
    EOF
    ```

</details>

<details>
<summary>2. Install Docker</summary>

1. [Install Docker Desktop](https://www.docker.com/get-started).
    - _Linux only_:
        - Export your user's user id and group id so that [files created in the Dev Container are owned by your user](https://github.com/moby/moby/issues/3206):
            ```sh
            cat << EOF >> ~/.bashrc
            
            export UID=$(id --user)
            export GID=$(id --group)
            EOF
            ```

</details>

<details>
<summary>3. Install VS Code or PyCharm</summary>

1. [Install VS Code](https://code.visualstudio.com/) and [VS Code's Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). Alternatively, install [PyCharm](https://www.jetbrains.com/pycharm/download/).
2. _Optional:_ install a [Nerd Font](https://www.nerdfonts.com/font-downloads) such as [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode) and [configure VS Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) or [configure PyCharm](https://github.com/tonsky/FiraCode/wiki/Intellij-products-instructions) to use it.

</details>

</details>

<details open>
<summary>Development environments</summary>

The following development environments are supported:

1. ⭐️ _GitHub Codespaces_: click on _Code_ and select _Create codespace_ to start a Dev Container with [GitHub Codespaces](https://github.com/features/codespaces).
1. ⭐️ _Dev Container (with container volume)_: click on [Open in Dev Containers](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/to/do) to clone this repository in a container volume and create a Dev Container with VS Code.
1. _Dev Container_: clone this repository, open it with VS Code, and run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Dev Containers: Reopen in Container_.
1. _PyCharm_: clone this repository, open it with PyCharm, and [configure Docker Compose as a remote interpreter](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#docker-compose-remote) with the `dev` service.
1. _Terminal_: clone this repository, open it with your terminal, and run `docker compose up --detach dev` to start a Dev Container in the background, and then run `docker compose exec dev zsh` to open a shell prompt in the Dev Container.

</details>

<details>
<summary>Developing</summary>

- Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project.
- Run `poetry add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `poetry.lock`. Add `--group test` or `--group dev` to install a CI or development dependency, respectively.
- Run `poetry update` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`.

</details>
