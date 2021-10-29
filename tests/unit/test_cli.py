from click.testing import CliRunner
from sattl.cli import run
from mock import patch, call, MagicMock
from logging import DEBUG

runner = CliRunner()


def test_cli_fails_wo_required_params():
    result = runner.invoke(run, ["/tmp"])
    assert result.exit_code == 2
    assert "Missing option '--sf-org'" in result.output

    result = runner.invoke(run, ["--sf-org", "sf-org"])
    assert result.exit_code == 2
    assert "Missing argument 'PATH'" in result.output

    with patch('os.listdir', return_value=[]):
        result = runner.invoke(run, ["--sf-org", "sf-org", "/tmp"])
        assert result.exit_code == 0


def test_cli_no_test_case_option():
    folders = [f"folder{i+1}" for i in range(4)]
    with patch('os.listdir', return_value=folders), patch('sattl.cli.TestCase') as mock_test_case:
        result = runner.invoke(run, ["--sf-org", "fake", "/folder"])
        assert result.exit_code == 0
        assert mock_test_case.call_args_list == [
            call(sf_org="fake", is_sandbox=True, path=f"/folder/{folder}", timeout=30) for folder in folders
        ]


def test_cli_test_case_option():
    with patch('os.listdir', return_value=[]), patch('sattl.cli.TestCase') as mock_test_case:
        result = runner.invoke(run, ["--sf-org", "fake", "--test-case", "/folder"])
        assert result.exit_code == 0
        mock_test_case.assert_called_once_with(sf_org="fake", is_sandbox=True, path='/folder', timeout=30)


def test_cli_timeout_option():
    with patch('os.listdir', return_value=[]), patch('sattl.cli.TestCase') as mock_test_case:
        result = runner.invoke(run, ["--sf-org", "fake", "--timeout", "60", "--test-case", "/folder"])
        assert result.exit_code == 0
        mock_test_case.assert_called_once_with(sf_org="fake", is_sandbox=True, path='/folder', timeout=60)


def test_cli_is_prod_option():
    with patch('os.listdir', return_value=[]), patch('sattl.cli.TestCase') as mock_test_case:
        result = runner.invoke(run, ["--sf-org", "fake", "--is-prod", "--test-case", "/folder"])
        assert result.exit_code == 1
        assert "Aborted!" in result.output
        mock_test_case.assert_not_called()

        with patch("click.confirm") as mock_confirm:
            result = runner.invoke(run, ["--sf-org", "fake", "--is-prod", "--test-case", "/folder"])
            assert result.exit_code == 0
            mock_confirm.assert_called_once()
            mock_test_case.assert_called_once_with(sf_org="fake", is_sandbox=False, path='/folder', timeout=30)


def test_cli_debug_option():
    mock_logger = MagicMock()
    with patch('sattl.cli.logger', mock_logger):
        runner.invoke(run, ["--sf-org", "fake", "--is-prod", "--debug", "--test-case", "/folder"])
        mock_logger.setLevel.assert_called_once_with(DEBUG)
        mock_logger.handlers[0].setLevel.assert_called_once_with(DEBUG)
