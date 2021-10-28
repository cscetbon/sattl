from collections import OrderedDict
from http import HTTPStatus

import pytest
import yaml
from mock import Mock, patch, call
from requests.structures import CaseInsensitiveDict
from simple_salesforce import SalesforceResourceNotFound

from sattl.salesforce import SalesforceObject
from sattl.salesforce.external_id import SalesforceExternalID
from tests.unit.salesforce.common import query_account


def query_record_type(*_):
    return OrderedDict([('attributes',
                         OrderedDict([('type', 'RecordType'),
                                      ('url',
                                       '/services/data/v53.0/sobjects/RecordType/0123t000000FkA9AAK')])),
                        ('Id', '0123t000000FkA9AAK'),
                        ('Slug__c', 'XC-2')])


def test_salesforce_object():
    sf_conn_mock = Mock()
    sf_object = SalesforceObject(sf_conn_mock,dict(
        type="Account", externalID={"Slug__c": "XC-2"}, status="enrolled", location="Cannes"
    ))
    assert sf_object.type == "Account"
    assert sf_object.sf_type == sf_conn_mock.Account
    assert sf_object.external_id == SalesforceExternalID("Slug__c", "XC-2")
    assert sf_object.content == dict(status="enrolled", location="Cannes")


def test_salesforce_refresh_relations(salesforce_connection):
    sf_object = SalesforceObject(salesforce_connection, dict(type="Account", externalID={"Slug__c": "XC-2"}))
    sf_object.refresh_relations()
    relation_mock = Mock()
    sf_object.relations = {"field": relation_mock}
    sf_object.refresh_relations()
    assert sf_object.content["field"] == relation_mock.get_id(sf_object.sf_connection)
    assert not sf_object.relations


def test_salesforce_load(salesforce_connection):
    sf_object = SalesforceObject(salesforce_connection, dict(type="Account", externalID={"Slug__c": "XC-2"}))
    with patch("simple_salesforce.api.SFType.get_by_custom_id", query_account):
        assert sf_object.load() is True
    assert sf_object.content == {
        'Id': '0017A00000kkHm8QAE',
        'Name': 'Mug Coffee',
        'RecordTypeId': '0123t000000FkA9AAK',
        'Student_Type__c': 'Enrolled',
        'UUID__c': 'b2a1da8b-b68b-42b6-81e7-dc89ce6e86f0',
        'University_ID__c': '100087987',
        'University_Email__c': 'jdoe@test.com',
        'SIS_Email__c': None,
        'SIS_First_Name__c': 'Mug',
        'SIS_Last_Name__c': 'Coffee'
    }


@pytest.mark.parametrize('first_name, diff', [
    ("Mug", None),
    ("Joe", ("  RecordTypeId: 0123t000000FkA9AAK\n"
             "- SIS_First_Name__c: Mug\n"
             "?                    ^^^\n"
             "+ SIS_First_Name__c: Joe\n"
             "?                    ^^^\n"
             "  SIS_Last_Name__c: Coffee\n"
             "  Slug__c: XC-2\n"
             "  University_Email__c: jdoe@test.com\n"
             "  type: Account\n"))
])
def test_salesforce_matches(first_name, diff, salesforce_connection):
    sf_object = SalesforceObject(salesforce_connection, dict(type="Account", externalID={"Slug__c": "XC-2"}))
    with patch("simple_salesforce.api.SFType.get_by_custom_id", query_account):
        assert sf_object.load() is True
    content = """
        type: Account
        externalID:
          Slug__c: XC-2
        relations:
          RecordTypeId:
            type: RecordType
            name: SIS Student
        SIS_Last_Name__c: Coffee
        University_Email__c: jdoe@test.com
    """
    content = CaseInsensitiveDict(yaml.load(content, Loader=yaml.FullLoader))
    local_sf_object = SalesforceObject(salesforce_connection, content)
    with patch("simple_salesforce.api.SFType.get_by_custom_id", side_effect=[query_record_type(), query_account()]):
        local_sf_object.content["SIS_First_Name__c"] = first_name
        local_sf_object.refresh_relations()
        assert sf_object.differences(local_sf_object) == diff


SF_RESOURCE_NOT_FOUND = SalesforceResourceNotFound(*("",) * 4)


@pytest.mark.parametrize('side_effect', [lambda _: HTTPStatus.NO_CONTENT, SF_RESOURCE_NOT_FOUND])
def test_salesforce_delete(side_effect, salesforce_connection):
    sf_object = SalesforceObject(salesforce_connection, dict(type="Account", externalID={"Slug__c": "XC-2"}))
    with patch("simple_salesforce.api.SFType.delete", side_effect=side_effect) as mock_delete:
            sf_object.delete()
            mock_delete.assert_called_once_with("Slug__c/XC-2")


def get_account_sf_object(salesforce_connection):
    content = """
        type: Account
        ID: something
        externalID:
          Slug__c: AA:BB/CCC
        relations:
          relationField:
            type: RelationType
            value: DD:EE/FFF
        SIS_First_Name__c: Mug
        SIS_Last_Name__c: Coffee
        University_Email__c: jdoe@test.com
    """
    return SalesforceObject(salesforce_connection, content=yaml.load(content, Loader=yaml.FullLoader))


def test_salesforce_upsert_succeeds(salesforce_connection):
    with patch("simple_salesforce.api.SFType.upsert", return_value=HTTPStatus.NO_CONTENT):
        assert get_account_sf_object(salesforce_connection).upsert() is True


def test_salesforce_upsert_fails(salesforce_connection):
    with patch("simple_salesforce.api.SFType.upsert", side_effect=SF_RESOURCE_NOT_FOUND):
        assert get_account_sf_object(salesforce_connection).upsert() is False


def test_get_by_custom_id_uses_quoted_values(salesforce_connection):
    sf_object = get_account_sf_object(salesforce_connection)

    with patch("simple_salesforce.api.SFType.get_by_custom_id", side_effect=query_record_type) as mock_get_id:
        sf_object.refresh_relations()
        sf_object.load()

    mock_get_id.assert_has_calls([call("value", "DD%3AEE%2FFFF"), call("Slug__c", "AA%3ABB%2FCCC")])


def test_api_delete_uses_quoted_values(salesforce_connection):
    sf_object = get_account_sf_object(salesforce_connection)

    with patch("simple_salesforce.api.SFType.delete", side_effect=SF_RESOURCE_NOT_FOUND) as mock_delete:
        sf_object.delete()

    mock_delete.assert_called_once_with("Slug__c/AA%3ABB%2FCCC")


def test_api_upsert_uses_quoted_values(salesforce_connection):
    sf_object = get_account_sf_object(salesforce_connection)

    with patch("simple_salesforce.api.SFType.upsert", return_value=HTTPStatus.NO_CONTENT) as mock_upsert:
        sf_object.upsert()

    mock_upsert.assert_called_once_with(
        "Slug__c/AA%3ABB%2FCCC",
        {
            'SIS_First_Name__c': 'Mug',
            'SIS_Last_Name__c': 'Coffee',
            'University_Email__c': 'jdoe@test.com'
        }
    )
