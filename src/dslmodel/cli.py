"""dslmodel CLI."""

import typer
from rich import print

from pathlib import Path
from dslmodel.generators.gen_dslmodel_class import generate_and_save_dslmodel



app = typer.Typer()


@app.command()
def fire(name: str = "Chell") -> None:
    """Fire portal gun."""
    print(f"[bold red]Alert![/bold red] {name} fired [green]portal gun[/green] :boom:")


@app.command("gen")
def generate_class(
        prompt: str = typer.Argument(..., help="A natural language description of the model(s) to generate."),
        output_dir: Path = typer.Option(Path.cwd(), "--output-dir",
                                        help="The directory to save the generated class files. Defaults to the current directory."),
        file_format: str = typer.Option("py", "--file-format",
                                        help="The file format for saving the generated models. Defaults to 'py'."),
        config: Path = typer.Option(None, "--config", help="Path to a custom configuration file."),
):
    """
    Generate DSLModel-based classes from a natural language prompt.

    The generated classes are saved to the specified directory in the chosen format.
    """
    typer.echo(f"Generating class from prompt: '{prompt}'")
    from dslmodel.utils.dspy_tools import init_lm, init_instant
    # init_lm()
    init_instant()

    # Delegate the core logic to the generate_and_save_dslmodel function
    try:
        generate_and_save_dslmodel(prompt, output_dir, file_format, config)
    except Exception as e:
        typer.echo(f"Error generating class: {e}")
        raise typer.Exit(code=1)

    typer.echo(f"Class generated successfully! Saved in: {output_dir}")


if __name__ == "__main__":
    app()
