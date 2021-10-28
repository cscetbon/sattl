from collections import OrderedDict


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