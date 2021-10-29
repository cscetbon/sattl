import yaml
import pytest
from httmock import urlmatch, HTTMock

from sattl.config import Config
from sattl.salesforce import SalesforceConnection


@pytest.fixture
def sample_object_content():
    return dict(type="Account", externalID=dict(Slug__c="aaa"), name="bbb")


@pytest.fixture
def yaml_with_five_sf_objects(sample_object_content):
    return yaml.dump_all([*(sample_object_content,)*5])


@urlmatch(scheme='https', netloc='test.salesforce.com', path=r'/services/Soap/u/53.0', method='post')
def salesforce_login(*_):
    return {'status_code': 200, 'content': """
        <root>
        <sessionId>00D7A0000009g88!AQQAQEev5W85xCXM0urY0oRblZuM6</sessionId>
        <serverUrl>https://2u-dom-ain-pastg.my.salesforce.com</serverUrl>
        </root>
    """}


@pytest.fixture
def salesforce_connection():
    config = Config(is_sandbox=True, sf_org="sf-org")
    with HTTMock(salesforce_login):
        return SalesforceConnection(config)