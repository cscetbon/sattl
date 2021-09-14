from sattl.salesforce import SalesforceConnection
from sattl.config import Config
from httmock import urlmatch, HTTMock


@urlmatch(scheme='https', netloc='test.salesforce.com', path=r'/services/Soap/u/53.0', method='post')
def salesforce_login(*_):
    return {'status_code': 200,
            'content':
                """<?xml version="1.0" encoding="UTF-8"?>
                    <sessionId>00D7A0000009g88!AQQAQEev5W85xCXM0urY0oRblZuM6</sessionId>
                    <serverUrl>2u-dom-ain-pastg.my.salesforce.com</serverUrl>"""}


def test_salesforce_connection():
    config = Config(is_sandbox=True, domain="dom-ain")
    with HTTMock(salesforce_login):
        sf_connection = SalesforceConnection(config)
    assert sf_connection.sf_version == "53.0"
    assert sf_connection.domain == "test"
    assert sf_connection.sf_instance == ""
    assert sf_connection.auth_type == "password"


# def test_salesforce_matches():
#     config = Config(is_sandbox=True, domain="dom-ain")
#     sf_connection = SalesforceConnection(config)
#     content = """
#         type: Account
#         externalIDs:
#           Slug__c: XC-2
#         fields:
#           sis_first_name__c: John
#           sis_last_name__c: Doe
#           University_Email__c: jdoe@test.com
#         relation:
#           record:
#             type: RecordType
#             name: SIS Student
#     """
#     sf_object = SalesforceObject(content=yaml.load(content))
#     # Patch query to return an object with same content
#     assert sf_object.get() == sf_object
#
#
# def test_salesforce_get():
#     config = Config(is_sandbox=True, domain="dom-ain")
#     sf_connection = SalesforceConnection(config)
#     content = """
#         type: Account
#         externalIDs:
#           Slug__c: XC-2
#         fields:
#           sis_first_name__c: John
#           sis_last_name__c: Doe
#           University_Email__c: jdoe@test.com
#         relation:
#           record:
#             type: RecordType
#             name: SIS Student
#     """
#     sf_object = SalesforceObject(content=yaml.load(content))
#     # Patch query to return an object with same content
#     assert sf_object.get() == sf_object
#     # keyValue, err := externalID(obj)
#     # soql := fmt.Sprintf("SELECT ID FROM %s WHERE %s = %s", obj.Type, keyValue.key, keyValue.value)
#     # result, err := r.Client.Query(soql)
#     # oid := result.Records[0]["Id"].(string)
#     # res := r.Client.SObject(obj.Type).Get(oid)
#
#
# def test_salesforce_upsert():
#     config = Config(is_sandbox=True, domain="dom-ain")
#     sf_connection = SalesforceConnection(config)
#     content = """
#         type: Account
#         externalIDs:
#           Slug__c: XC-2
#         fields:
#           sis_first_name__c: John
#           University_Email__c: danny@test.com
#         relation:
#           record:
#             type: RecordType
#             name: SIS Student
#     """
#     sf_object = SalesforceObject(content=yaml.load(content))
#     sf_object.upsert()
#     # Patch query to return an object with same content
#     assert sf_object.get() == sf_object
#
#
# def test_salesforce_delete():
#     config = Config(is_sandbox=True, domain="dom-ain")
#     sf_connection = SalesforceConnection(config)
#     content = """
#         type: Account
#         externalIDs:
#           Slug__c: XC-2
#     """
#     sf_object = SalesforceObject(content=yaml.load(content))
#     # Patch query to return an object with same content
#     sf_object.delete()
#     # assert query is DELETE FROM Account WHERE Slug__c = "XC-2"
