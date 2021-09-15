from simple_salesforce import Salesforce
from sattl.config import Config
from requests.structures import CaseInsensitiveDict

EXTERNAL_ID = "externalid"
RELATIONS = "relations"
TYPE = "type"


class SalesforceConnection:

    def __init__(self, config: Config):
        opts = dict(version="53.0")
        if config.is_sandbox:
            opts["domain"] = "test"
        self.sf = Salesforce(username=config.sf_username, password=config.sf_username, security_token="", **opts)


class SalesforceExternalID:

    def __init__(self, field, value):
        self.field = field
        self.value = value

    def __eq__(self, other):
        return self.field == other.field and self.value == other.value

    def __repr__(self):
        return f"{self.__class__.__name__}(field={self.field}, value={self.value})"


def soql_from_type_and_external_id(fields:str, _type: str, external_id: SalesforceExternalID):
    return f'SELECT {fields} FROM {_type} WHERE {external_id.field} = "{external_id.value}" LIMIT 1'


class SalesforceRelation:

    def __init__(self, content):
        if not content:
            raise AttributeError("content used to initialize SalesforceRelation can't be empty")
        _content = CaseInsensitiveDict(content)
        if len(_content) != 2 or TYPE not in _content:
            raise AttributeError("relation must have 2 keys with one being type and the other one and external ID")
        self.type = _content[TYPE]
        self.external_id = SalesforceExternalID(*[(k,v) for k,v in _content.items() if k.lower() != TYPE][0])

    def get_id(self, salesforce_connection: SalesforceConnection):
        result = salesforce_connection.sf.query(soql_from_type_and_external_id("ID", self.type, self.external_id))
        if not result or result.get("totalSize", 0) != 1:
            raise AttributeError(f'record of type {self.type} with {self.external_id.field} having '
                                 f'the value "{self.external_id.value}" cannot be found')

        return result["records"][0]["Id"]


def _insensitive_content(content: dict):
    return CaseInsensitiveDict({k: v for k, v in content.items()
                                if k.lower() not in [RELATIONS, EXTERNAL_ID, TYPE]})


class SalesforceObject:

    def __init__(self, salesforce_connection: SalesforceConnection, content: dict):
        if not content:
            raise AttributeError("content can't be empty")
        _content = CaseInsensitiveDict(content)
        for field in [EXTERNAL_ID, TYPE]:
            if field not in _content:
                raise AttributeError(f"{field} not found in content passed")
        if not _content[EXTERNAL_ID] or len(_content[EXTERNAL_ID]) != 1:
            raise AttributeError("externalID can't be empty and must have only one entry")
        relations = _content.get(RELATIONS, {})
        for field, relation in relations.items():
            if len(relation) != 2 or TYPE not in relation:
                raise AttributeError("relation must have 2 keys with one being type and the other one and external ID")

        self.relations = {k:SalesforceRelation(v) for k, v in relations.items() if v}
        self.refreshed = False
        self.external_id = SalesforceExternalID(*list(_content[EXTERNAL_ID].items())[0])
        self.sf_connection = salesforce_connection
        self.sf = salesforce_connection.sf
        self.type = _content[TYPE]
        self.content = _insensitive_content(_content)

    def __eq__(self, other):
        return self.content == other.content

    def matches(self, other):
        """
        To match other, self needs to have the same type, the same external id and other's content
        must be a subset of its
        """
        if self.type != other.type or self.external_id != other.external_id:
            return False
        for sf_object in [self, other]:
            if not sf_object.refreshed and (relations := sf_object.relations.items()):
                for field, relation in relations:
                    sf_object.content[field] = relation.get_id(self.sf_connection)
                sf_object.refreshed = True

        other_content = _insensitive_content(other.content)
        if any([self.content.get(field) != other_content.get(field) for field in other_content]):
            return False
        return True

    def get(self):
        result = self.sf.query(soql_from_type_and_external_id("FIELDS(ALL)", self.type, self.external_id))
        if result and result.get("totalSize", 0) == 1:
            self.content = CaseInsensitiveDict(result["records"][0])
            del self.content["attributes"]
            self.refreshed = True
            return True
