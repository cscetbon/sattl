import pytest
import yaml
from requests.structures import CaseInsensitiveDict
from httmock import urlmatch, HTTMock
from collections import OrderedDict
from mock import patch, Mock

from simple_salesforce import SalesforceResourceNotFound
from sattl.salesforce import SalesforceConnection, SalesforceObject, SalesforceRelation, SalesforceExternalID
from sattl.config import Config


@urlmatch(scheme='https', netloc='test.salesforce.com', path=r'/services/Soap/u/53.0', method='post')
def salesforce_login(*_):
    return {'status_code': 200, 'content': """
        <root>
        <sessionId>00D7A0000009g88!AQQAQEev5W85xCXM0urY0oRblZuM6</sessionId>
        <serverUrl>https://2u-dom-ain-pastg.my.salesforce.com</serverUrl>
        </root>
    """}


def query_account(*_):
    return OrderedDict([('attributes',
                     OrderedDict([('type', 'Account'),
                                  ('url',
                                   '/services/data/v53.0/sobjects/Account/0017A00000kkHm8QAE')])),
                    ('Id', '0017A00000kkHm8QAE'),
                    ('Name', 'Mug Coffee'),
                    ('RecordTypeId', '0123t000000FkA9AAK'),
                    ('Student_Type__c', 'Enrolled'),
                    ('UUID__c', 'b2a1da8b-b68b-42b6-81e7-dc89ce6e86f0'),
                    ('University_ID__c', '100087987'),
                    ('University_Email__c', 'jdoe@test.com'),
                    ('SIS_Email__c', None),
                    ('SIS_First_Name__c', 'Mug'),
                    ('SIS_Last_Name__c', 'Coffee')])


def query_record_type(*_):
    return OrderedDict([('attributes',
                     OrderedDict([('type', 'RecordType'),
                                  ('url',
                                   '/services/data/v53.0/sobjects/RecordType/0123t000000FkA9AAK')])),
                    ('Id', '0123t000000FkA9AAK')])


@pytest.fixture
def salesforce_connection():
    config = Config(is_sandbox=True, domain="dom-ain")
    with HTTMock(salesforce_login):
        return SalesforceConnection(config)


def test_salesforce_connection(salesforce_connection):
    sf = salesforce_connection.sf
    assert sf.sf_version == "53.0"
    assert sf.domain == "test"
    assert sf.sf_instance == "2u-dom-ain-pastg.my.salesforce.com"
    assert sf.auth_type == "password"


def test_salesforce_external_id():
    sf_external_id = SalesforceExternalID("KEY", "VALUE")
    assert sf_external_id.field == "KEY"
    assert sf_external_id.value == "VALUE"


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


def test_salesforce_object():
    sf_object = SalesforceObject(Mock(), dict(type="Account", externalID={"Slug__c": "XC-2"},
                                              status="enrolled", location="Cannes"))
    assert sf_object.type == "Account"
    assert sf_object.external_id == SalesforceExternalID("Slug__c", "XC-2")
    assert sf_object.content == dict(status="enrolled", location="Cannes")


def test_salesforce_refresh_relations(salesforce_connection):
    sf_object = SalesforceObject(salesforce_connection, dict(type="Account", externalID={"Slug__c": "XC-2"}))
    sf_object.refresh_relations()
    assert sf_object.refreshed is False

    relation_mock = Mock()
    sf_object.relations = {"field": relation_mock}
    sf_object.refresh_relations()
    assert sf_object.refreshed is True
    assert sf_object.content["field"] == relation_mock.get_id(sf_object.sf_connection)


def test_salesforce_get(salesforce_connection):
    sf_object = SalesforceObject(salesforce_connection, dict(type="Account", externalID={"Slug__c": "XC-2"}))
    with patch("simple_salesforce.api.SFType.get_by_custom_id", query_account):
        assert sf_object.get() is True
        assert sf_object.refreshed is True
    assert sf_object.content == {'Id': '0017A00000kkHm8QAE', 'Name': 'Mug Coffee', 'RecordTypeId': '0123t000000FkA9AAK',
                                 'Student_Type__c': 'Enrolled', 'UUID__c': 'b2a1da8b-b68b-42b6-81e7-dc89ce6e86f0',
                                 'University_ID__c': '100087987', 'University_Email__c': 'jdoe@test.com',
                                 'SIS_Email__c': None, 'SIS_First_Name__c': 'Mug', 'SIS_Last_Name__c': 'Coffee'}


def test_salesforce_matches(salesforce_connection):
    sf_object = SalesforceObject(salesforce_connection, dict(type="Account", externalID={"Slug__c": "XC-2"}))
    with patch("simple_salesforce.api.SFType.get_by_custom_id", query_account):
        assert sf_object.get() is True
    content = """
        type: Account
        externalID:
          Slug__c: XC-2
        relations:
          RecordTypeId:
            type: RecordType
            name: SIS Student
        SIS_First_Name__c: Mug
        SIS_Last_Name__c: Coffee
        University_Email__c: jdoe@test.com
    """
    content = CaseInsensitiveDict(yaml.load(content, Loader=yaml.FullLoader))
    local_sf_object = SalesforceObject(salesforce_connection, content)
    with patch("simple_salesforce.api.SFType.get_by_custom_id", query_record_type):
        assert sf_object.matches(local_sf_object) is True

    local_sf_object.content["SIS_First_Name__c"] = "joe"
    assert sf_object.matches(local_sf_object) is False


def test_salesforce_delete(salesforce_connection):
    sf_object = SalesforceObject(salesforce_connection, dict(type="Account", externalID={"Slug__c": "XC-2"}))
    with patch("simple_salesforce.api.SFType.get_by_custom_id", query_account):
        with patch("simple_salesforce.api.SFType.delete", return_value=204):
            assert sf_object.delete() is True
        with patch("simple_salesforce.api.SFType.delete", side_effect=SalesforceResourceNotFound(*("",)*4)):
            assert sf_object.delete() is False

    with patch("simple_salesforce.api.SFType.get_by_custom_id", side_effect=SalesforceResourceNotFound(*("",)*4)):
        assert sf_object.delete() is False


def test_salesforce_upsert(salesforce_connection):
    content = """
        type: Account
        ID: something
        externalID:
          Slug__c: XC-2
        relations:
          record:
            type: RecordType
            name: SIS Student
        SIS_First_Name__c: Mug
        SIS_Last_Name__c: Coffee
        University_Email__c: jdoe@test.com
    """
    sf_object = SalesforceObject(salesforce_connection, content=yaml.load(content, Loader=yaml.FullLoader))
    with patch("simple_salesforce.api.SFType.get_by_custom_id", query_record_type):
        with patch("simple_salesforce.api.SFType.upsert", return_value=204):
            assert sf_object.upsert() is True

    assert sf_object.content == {
        'SIS_First_Name__c': 'Mug',
        'SIS_Last_Name__c': 'Coffee',
        'University_Email__c': 'jdoe@test.com',
        'record': '0123t000000FkA9AAK'
    }
    assert sf_object.refreshed is True

    with patch("simple_salesforce.api.SFType.upsert", side_effect=SalesforceResourceNotFound(*("",)*4)):
        assert sf_object.upsert() is False
