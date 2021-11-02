from sattl.config import Config
import pytest


@pytest.mark.parametrize('is_prod, prefix', [(False, "test"), (True, "login")])
def test_config(is_prod, prefix):
    config = Config(is_prod, "sf-org")
    assert config.is_prod is is_prod
    assert config.sf_org == "sf-org"
    assert config.sf_username == "USERNAME"
    assert config.sf_password == "PASSWORD"
