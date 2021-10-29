from typing import Dict

from requests.structures import CaseInsensitiveDict
from simple_salesforce import SalesforceResourceNotFound

from sattl.salesforce.constants import ID, TYPE
from sattl.salesforce.external_id import SalesforceExternalID
from sattl.salesforce.connection import SalesforceConnection


class SalesforceRelation:

    def __init__(self, content: Dict):
        if not content:
            raise AttributeError("content used to initialize SalesforceRelation can't be empty")
        _content = CaseInsensitiveDict(content)
        if len(_content) != 2 or TYPE not in _content:
            raise AttributeError("relation must have 2 keys with one being type and the other one an external ID")
        self.type = _content.pop(TYPE)
        self.external_id = SalesforceExternalID(*_content.popitem())

    def get_id(self, salesforce_connection: SalesforceConnection):
        key, value = self.external_id.field, self.external_id.value
        try:
            return salesforce_connection.__getattr__(self.type).get_by_custom_id(
                self.external_id.field, self.external_id.quoted_value
            )[ID]
        except SalesforceResourceNotFound:
            raise AttributeError(f'record of type {self.type} with {key} having the value "{value}" cannot be found')
