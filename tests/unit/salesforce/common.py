from collections import OrderedDict

from httmock import urlmatch


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


@urlmatch(scheme='https', netloc='test.salesforce.com', path=r'/services/Soap/u/53.0', method='post')
def salesforce_login(*_):
    return {'status_code': 200, 'content': """
        <root>
        <sessionId>00D7A0000009g88!AQQAQEev5W85xCXM0urY0oRblZuM6</sessionId>
        <serverUrl>https://2u-sf-org-pastg.my.salesforce.com</serverUrl>
        </root>
    """}
