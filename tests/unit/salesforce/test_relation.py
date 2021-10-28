import pytest
from mock import patch

from sattl.salesforce import SalesforceRelation
from sattl.salesforce.external_id import SalesforceExternalID
from tests.unit.salesforce.common import query_account
from tests.unit.conftest import salesforce_connection


def test_salesforce_valid_relation(salesforce_connection):
    sf_relation = SalesforceRelation({"Type": "Contact", "Name": "Cyril"})
    assert sf_relation.type == "Contact"
    assert sf_relation.external_id == SalesforceExternalID("Name", "Cyril")
    with patch("simple_salesforce.api.SFType.get_by_custom_id", query_account):
        assert sf_relation.get_id(salesforce_connection) == "0017A00000kkHm8QAE"


@pytest.mark.parametrize('content,error_msg', [
    (None, "content used to initialize SalesforceRelation can't be empty"),
    ({"Name": "Cyril"}, "relation must have 2 keys with one being type"),
    ({"Typo": "Contact", "Name": "Cyril"}, "relation must have 2 keys with one being type"),
])
def test_salesforce_invalid_relation(content, error_msg):
    with pytest.raises(AttributeError) as exc:
        SalesforceRelation(content)
    assert error_msg in str(exc)
