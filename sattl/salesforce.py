from simple_salesforce import Salesforce
from sattl.config import Config


class SalesforceConnection:

    def __init__(self, config: Config):
        opts = dict(version="53.0")
        if config.is_sandbox:
            opts["domain"] = "test"
        self.sf = Salesforce(username=config.sf_username, password=config.sf_username, security_token="", **opts)



class SalesforceObject:

    def __init__(self, content: dict):
        self.content = content

    def __eq__(self, other):
        return self.content == other.content
