from pathlib import Path

import typer
from typing import Optional
from typing_extensions import Annotated
from dslmodel.commands.slidev_utils import slidev, build, export, format_cmd, eject, _validate_nodejs_deps


def callback():
    """
    Validate that required Node.js dependencies for Slidev are installed.
    """
    _validate_nodejs_deps()


app = typer.Typer(help="Slidev CLI commands. https://sli.dev/builtin/cli", callback=callback)


@app.command(name="server", help="Start a local server for Slidev. https://sli.dev/builtin/cli#dev")
def slidev_command(
        entry: Annotated[str, typer.Argument(help="Path to the markdown file containing your slides.")] = "slides.md",
        port: Annotated[int, typer.Option("--port", "-p", help="Port number.")] = 3030,
        open_browser: Annotated[bool, typer.Option("--open", "-o", help="Open in the browser.")] = False,
        remote: Annotated[
            Optional[str], typer.Option(help="Enable remote control (set password for private access).")] = None,
        bind: Annotated[str, typer.Option(help="Specify the IP address to listen on.")] = "0.0.0.0",
        log: Annotated[str, typer.Option(help="Log level (error, warn, info, silent).")] = "warn",
        force: Annotated[bool, typer.Option("--force", "-f", help="Force the optimizer to ignore the cache.")] = False,
        theme_: Annotated[Optional[str], typer.Option("--theme", "-t", help="Override the theme.")] = None,
):
    slidev(entry, port, open_browser, remote, bind, log, force, theme_)


@app.command(name="build",
             help="Build a hostable SPA. https://sli.dev/builtin/cli#build")
def build_command(
        entry: Annotated[str, typer.Argument(help="Path to the slides markdown file.")] = "slides.md",
        out: Annotated[str, typer.Option("--out", "-o", help="Output directory.")] = "dist",
        base: Annotated[str, typer.Option(help="Base URL.")] = "/",
        download: Annotated[bool, typer.Option(help="Allow slide download as PDF in the SPA.")] = False,
        theme_: Annotated[Optional[str], typer.Option("--theme", "-t", help="Override the theme.")] = None,
):
    build(entry, out, base, download, theme_)


@app.command(name="export",
             help="Export the slides to a different format (pdf, png, pptx, md). https://sli.dev/builtin/cli#export")
def export_command(
        entry: Annotated[str, typer.Argument(help="Path to the slides markdown entry.")] = "slides.md",
        output: Annotated[Optional[str], typer.Option(help="Path to the output.")] = None,
        format_: Annotated[str, typer.Option("--format", help="Output format (pdf, png, pptx, md).")] = "pdf",
        timeout: Annotated[int, typer.Option(help="Timeout for rendering the print page.")] = 30000,
        range_: Annotated[Optional[str], typer.Option("--range", help="Page ranges to export.")] = None,
        dark: Annotated[bool, typer.Option(help="Export as dark theme.")] = False,
        with_clicks: Annotated[
            bool, typer.Option("--with-clicks", "-c", help="Export pages for every click animation.")] = False,
        theme_: Annotated[Optional[str], typer.Option("--theme", "-t", help="Override the theme.")] = None,
        omit_background: Annotated[bool, typer.Option(help="Remove the default browser background.")] = False,
):
    export(entry, output, format_, timeout, range_, dark, with_clicks, theme_, omit_background)


@app.command(name="format",
             help="Format the markdown file. https://sli.dev/builtin/cli#format")
def format_command(
        entry: Annotated[str, typer.Argument(help="Path to the slides markdown entry.")] = "slides.md",
):
    format_cmd(entry)


@app.command(name="eject", help="Eject the theme. https://sli.dev/builtin/cli#theme")
def eject_command(
        entry: Annotated[Path, typer.Argument(help="Path to the slides markdown entry.")] = "slides.md",
        dir_: Annotated[Path, typer.Option("--dir", help="Output directory for the ejected theme.")] = "theme",
        theme_: Annotated[Optional[str], typer.Option("--theme", "-t", help="Override the theme.")] = None,
):
    eject(entry, dir_, theme_)


if __name__ == "__main__":
    app()
