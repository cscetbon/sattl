from click.testing import CliRunner
from sattl.cli import run
from mock import patch

runner = CliRunner()


def test_cli_required_params():
    result = runner.invoke(run, ["/tmp"])
    assert result.exit_code == 2
    assert "Missing option '--domain'" in result.output

    result = runner.invoke(run, ["--domain", "dom-ain"])
    assert result.exit_code == 2
    assert "Missing argument 'PATH'" in result.output

    with patch('os.listdir', return_value=[]):
        result = runner.invoke(run, ["--domain", "dom-ain", "/tmp"])
        assert result.exit_code == 0
