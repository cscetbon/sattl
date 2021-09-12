from click.testing import CliRunner
from sattl.cli import test
from mock import patch

runner = CliRunner()


def test_cli_required_params():
    result = runner.invoke(test, ["/tmp"])
    assert result.exit_code == 2
    assert "Missing option '--org'" in result.output

    result = runner.invoke(test, ["--org", "dom-ain"])
    assert result.exit_code == 2
    assert "Missing argument 'PATH'" in result.output

    result = runner.invoke(test, ["--org", "dom-ain", "/tmp"])
    assert result.exit_code == 0


def test_cli_is_sandbox():
    with patch("sattl.cli.check_is_sandbox") as check_is_sandbox:
        result = runner.invoke(test, ["--org", "dom-ain", "--is-sandbox", "no", "/tmp"])
    assert result.exit_code == 0
    check_is_sandbox.assert_called_once_with(False)

    with patch("sattl.cli.check_is_sandbox") as check_is_sandbox:
        result = runner.invoke(test, ["--org", "dom-ain", "/tmp"])
    assert result.exit_code == 0
    check_is_sandbox.assert_called_once_with(True)
