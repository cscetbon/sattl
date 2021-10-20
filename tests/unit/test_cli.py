from click.testing import CliRunner
from sattl.cli import run
from mock import patch, call

runner = CliRunner()


def test_cli_fails_wo_required_params():
    result = runner.invoke(run, ["/tmp"])
    assert result.exit_code == 2
    assert "Missing option '--domain'" in result.output

    result = runner.invoke(run, ["--domain", "dom-ain"])
    assert result.exit_code == 2
    assert "Missing argument 'PATH'" in result.output

    with patch('os.listdir', return_value=[]):
        result = runner.invoke(run, ["--domain", "dom-ain", "/tmp"])
        assert result.exit_code == 0


def test_cli_no_test_case_option():
    with patch('os.listdir', return_value=["folder1", "folder2"]), patch('sattl.cli.TestCase') as mock_test_case:
        result = runner.invoke(run, ["--domain", "fake", "/folder"])
        assert result.exit_code == 0
        assert mock_test_case.call_args_list == [
            call(domain="fake", is_sandbox=True, path='folder1'),
            call(domain="fake", is_sandbox=True, path='folder2')
        ]


def test_cli_test_case_option():
    with patch('os.listdir', return_value=[]), patch('sattl.cli.TestCase') as mock_test_case:
        result = runner.invoke(run, ["--domain", "fake", "--test-case", "/folder"])
        assert result.exit_code == 0
        mock_test_case.assert_called_once_with(domain="fake", is_sandbox=True, path='/folder')


def test_cli_is_prod_option():
    with patch('os.listdir', return_value=[]), patch('sattl.cli.TestCase') as mock_test_case:
        result = runner.invoke(run, ["--domain", "fake", "--is-prod", "--test-case", "/folder"])
        assert result.exit_code == 1
        assert "Aborted!" in result.output
        mock_test_case.assert_not_called()

        with patch("click.confirm") as mock_confirm:
            result = runner.invoke(run, ["--domain", "fake", "--is-prod", "--test-case", "/folder"])
            assert result.exit_code == 0
            mock_confirm.assert_called_once()
            mock_test_case.assert_called_once_with(domain="fake", is_sandbox=False, path='/folder')
