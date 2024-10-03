"""Test dslmodel CLI."""

from typer.testing import CliRunner

from dslmodel.cli import app

runner = CliRunner()


def test_fire() -> None:
    """Test that the fire command works as expected."""
    name = "GLaDOS"
    result = runner.invoke(app, ["fire", "--name", name])
    assert result.exit_code == 0
    assert name in result.stdout
