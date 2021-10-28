from mock import patch

from sattl.salesforce import SalesforceConnection


def test_salesforce_connection(salesforce_connection):
    assert salesforce_connection.sf_version == "53.0"
    assert salesforce_connection.domain == "test"
    assert salesforce_connection.sf_instance == "2u-dom-ain-pastg.my.salesforce.com"
    assert salesforce_connection.auth_type == "password"


def test_salesforce_connection_instantiation(salesforce_connection):
    with patch('sattl.salesforce.connection.Salesforce.__init__') as mock_salesforce:
        SalesforceConnection(salesforce_connection.config)
    mock_salesforce.assert_called_with(domain='test', password='PASSWORD', security_token='', username='USERNAME',
                                       version='53.0')
