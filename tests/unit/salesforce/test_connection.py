import pytest
from httmock import HTTMock
from mock import patch

from sattl.config import Config
from sattl.salesforce import SalesforceConnection
from tests.unit.salesforce.common import salesforce_login


def test_salesforce_connection(salesforce_connection):
    assert salesforce_connection.sf_version == "53.0"
    assert salesforce_connection.domain == "test"
    assert salesforce_connection.sf_instance == "2u-dom-ain-pastg.my.salesforce.com"
    assert salesforce_connection.auth_type == "password"


@pytest.mark.parametrize('is_prod, opts', [
    (False, {"domain": "test"}),
    (True, {}),
])
def test_salesforce_connection_instantiation(is_prod, opts):
    with HTTMock(salesforce_login), patch('sattl.salesforce.connection.Salesforce.__init__') as mock_salesforce:
        config = Config(is_prod, sf_org="sf-org")
        SalesforceConnection(config)
    mock_salesforce.assert_called_with(**opts, password='PASSWORD', security_token='', username='USERNAME',
                                       version='53.0')
