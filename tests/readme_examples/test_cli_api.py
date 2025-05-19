from typer.testing import CliRunner
from dslmodel.cli import app as cli_app
from fastapi.testclient import TestClient
from dslmodel.api import app as api_app

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli_app, ['--help'])
    assert result.exit_code == 0
    assert 'Usage' in result.output or 'usage' in result.output

def test_api_root():
    client = TestClient(api_app)
    response = client.get('/')
    assert response.status_code in (200, 404)  # Accept 404 if root not implemented 