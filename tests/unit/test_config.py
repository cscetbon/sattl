from sattl.config import Config
import pytest


@pytest.mark.parametrize('is_sandbox,prefix', [(True, "test"), (False, "login")])
def test_config(is_sandbox, prefix):
    config = Config(is_sandbox=is_sandbox, sf_org="sf-org")
    assert config.sf_org == "sf-org"
    assert config.is_sandbox is is_sandbox
    assert config.sf_username == "USERNAME"
    assert config.sf_password == "PASSWORD"
