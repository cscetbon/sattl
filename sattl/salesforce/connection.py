from simple_salesforce import Salesforce

from sattl.config import Config


class SalesforceConnection(Salesforce):

    def __init__(self, config: Config):
        self.config = config
        self.opts = dict(version="53.0")
        if config.is_sandbox:
            self.opts["domain"] = "test"
        super().__init__(username=config.sf_username, password=config.sf_password, security_token="", **self.opts)


def get_sf_connection(is_sandbox: bool, sf_org: str):
    return SalesforceConnection(Config(is_sandbox, sf_org))
