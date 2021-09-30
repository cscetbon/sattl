from os import getenv

from simple_salesforce import Salesforce, SalesforceResourceNotFound
from sattl.config import Config
from requests.structures import CaseInsensitiveDict
from typing import Dict

ID = "Id"
EXTERNAL_ID = "externalid"
RELATIONS = "relations"
TYPE = "type"


class SalesforceConnection(Salesforce):

    def __init__(self, config: Config):
        opts = dict(version="53.0")
        if config.is_sandbox:
            opts["domain"] = "test"
        super().__init__(username=config.sf_username, password=config.sf_username, security_token="", **opts)


class SalesforceExternalID:

    def __init__(self, field, value):
        self.field = field
        self.value = value

    def __eq__(self, other):
        return self.field == other.field and self.value == other.value

    def __repr__(self):
        return f"{self.__class__.__name__}(field={self.field}, value={self.value})"


class SalesforceRelation:

    def __init__(self, content: Dict):
        if not content:
            raise AttributeError("content used to initialize SalesforceRelation can't be empty")
        _content = CaseInsensitiveDict(content)
        if len(_content) != 2 or TYPE not in _content:
            raise AttributeError("relation must have 2 keys with one being type and the other one an external ID")
        self.type = _content.pop(TYPE)
        external_id_field = next(iter(_content))
        self.external_id = SalesforceExternalID(external_id_field, _content[external_id_field])

    def get_id(self, salesforce_connection: SalesforceConnection):
        key, value = self.external_id.field, self.external_id.value
        try:
            return salesforce_connection.__getattr__("self.type").get_by_custom_id(key, value)[ID]
        except SalesforceResourceNotFound:
            raise AttributeError(f'record of type {self.type} with {key} having the value "{value}" cannot be found')


class SalesforceObject:

    def __init__(self, salesforce_connection: SalesforceConnection, content: dict):
        if not content:
            raise AttributeError("content can't be empty")
        self.original_content = content
        _content = CaseInsensitiveDict(content)
        for field in [EXTERNAL_ID, TYPE]:
            if field not in _content:
                raise AttributeError(f"{field} not found in content passed")
        if not _content[EXTERNAL_ID] or len(_content[EXTERNAL_ID]) != 1:
            raise AttributeError("externalID can't be empty and must have only one entry")
        relations = _content.pop(RELATIONS, {})
        for field, relation in relations.items():
            if len(relation) != 2 or TYPE not in relation:
                raise AttributeError("relation must have 2 keys with one being type and the other one and external ID")

        self.relations = {k:SalesforceRelation(v) for k, v in relations.items() if v}
        self.external_id = SalesforceExternalID(*list(_content.pop(EXTERNAL_ID).items())[0])
        self.sf_connection = salesforce_connection
        self.type = _content.pop(TYPE)
        self.content = CaseInsensitiveDict(_content)

    def __repr__(self):
        return str(self.original_content)

    def __eq__(self, other):
        return self.content == other.content

    def refresh_relations(self):
        if not self.relations:
            return

        self.content.update({field: relation.get_id(self.sf_connection) for field, relation in self.relations.items()})
        self.relations = {}

    def matches(self, other):
        """
        To match other, self needs to have the same type, the same external id and other's content
        must be a subset of its
        """
        if not self.get():
            return False
        if self.type != other.type or self.external_id != other.external_id:
            return False
        other.refresh_relations()
        return other.content.items() <= self.content.items()

    def get(self):
        try:
            result = self.sf_type.get_by_custom_id(self.external_id.field, self.external_id.value)
            del result["attributes"]
            self.content = CaseInsensitiveDict(result)
            return True
        except SalesforceResourceNotFound:
            pass
        return False

    def delete(self):
        try:
            result = self.sf_type.get_by_custom_id(self.external_id.field, self.external_id.value)
            self.sf_type.delete(result[ID])
            return True
        except SalesforceResourceNotFound:
            pass
        return False

    def upsert(self):
        try:
            self.refresh_relations()
            self.content.pop(ID, None)
            self.sf_type.upsert(f"{self.external_id.field}/{self.external_id.value}", self.content)
            return True
        except SalesforceResourceNotFound:
            pass
        return False

    @property
    def sf_type(self):
        return self.sf_connection.__getattr__(self.type)


def get_sf_connection():
    config = Config(is_sandbox=getenv("IS_SANDBOX", True), domain=getenv("SF_DOMAIN"))
    return SalesforceConnection(config)
