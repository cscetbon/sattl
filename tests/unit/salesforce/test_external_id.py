from sattl.salesforce.external_id import SalesforceExternalID
import pytest


def test_salesforce_external_id():
    sf_external_id = SalesforceExternalID("KEY", "VALUE")
    assert sf_external_id.field == "KEY"
    assert sf_external_id.value == "VALUE"


@pytest.mark.parametrize('field, value', [
    ("", "a value"),
    ("a field", ""),
    ("", ""),
])
def test_salesforce_external_id_not_empty(field, value):
    with pytest.raises(Exception) as exc:
        SalesforceExternalID(field, value)
    assert str(exc.value) == f"ExternalID field and value must be non empty. SalesforceExternalID(field='{field}', value='{value}')"


def test_salesforce_quoted_external_id():
    assert SalesforceExternalID("_", "AA/BB/F").quoted_value == "AA%2FBB%2FF"
    assert SalesforceExternalID("_", "AA:BB F").quoted_value == "AA%3ABB F"
