from sattl.config import Config


def test_config():
    config = Config(is_sandbox=True, domain="dom-ain")
    assert config.domain == "dom-ain"
    assert config.is_sandbox is True
    assert config.sf_username == "USERNAME"
    assert config.sf_password == "PASSWORD"

