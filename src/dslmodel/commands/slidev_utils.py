import subprocess
from typing import Optional
import typer


def _validate_nodejs_deps():
    try:
        # Check if `slidev` is installed
        subprocess.run(["pnpm", "list", "-g", "slidev"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True)

        # Check if `playwright-chromium` is installed
        subprocess.run(["pnpm", "list", "-g", "playwright-chromium"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        typer.echo(
            "Error: Required Node.js packages are not installed. "
            "Please ensure you have run:\n\n"
            "    pnpm install -g @slidev/cli playwright-chromium\n",
            err=True,
        )
        raise typer.Exit(1)


def run_slidev_command(command: list):
    """
    Helper to run Slidev CLI commands using subprocess.
    """
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=e.returncode)


def slidev(entry: str, port: int, open_browser: bool, remote: Optional[str], bind: str, log: str, force: bool,
           theme: Optional[str]):
    """
    Logic for the `slidev` command.
    """
    command = [
        "npx"
        "@slidev/cli",
        entry,
        "--port", str(port),
        "--open" if open_browser else "",
        f"--remote={remote}" if remote else "",
        "--bind", bind,
        "--log", log,
        "--force" if force else "",
        f"--theme={theme}" if theme else "",
    ]
    run_slidev_command([arg for arg in command if arg])  # Remove empty args


def build(entry: str, out: str, base: str, download: bool, theme: Optional[str]):
    """
    Logic for the `build` command.
    """
    command = [
        "npx"
        "@slidev/cli",
        "build", entry,
        "--out", out,
        "--base", base,
        "--download" if download else "",
        f"--theme={theme}" if theme else "",
    ]
    run_slidev_command([arg for arg in command if arg])


def export(entry: str, output: Optional[str], format_: str, timeout: int, range_: Optional[str], dark: bool,
           with_clicks: bool, theme: Optional[str], omit_background: bool):
    """
    Logic for the `export` command.
    """
    command = [
        "npx"
        "@slidev/cli",
        "export", entry,
        f"--output={output}" if output else "",
        "--format", format_,
        "--timeout", str(timeout),
        f"--range={range_}" if range_ else "",
        "--dark" if dark else "",
        "--with-clicks" if with_clicks else "",
        f"--theme={theme}" if theme else "",
        "--omit-background" if omit_background else "",
    ]
    run_slidev_command([arg for arg in command if arg])


def format_cmd(entry: str):
    """
    Logic for the `format` command.
    """
    command = ["npx", "@slidev/cli",
               "format", entry]
    run_slidev_command(command)


def eject(entry: str, dir_: str, theme: Optional[str]):
    """
    Logic for the `theme` command.
    """
    command = [
        "npx"
        "@slidev/cli",
        "theme", "eject", entry,
        "--dir", dir_,
        f"--theme={theme}" if theme else "",
    ]
    run_slidev_command([arg for arg in command if arg])
