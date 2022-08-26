from copy import copy

import yaml
from requests.structures import CaseInsensitiveDict

from difflib import ndiff
from simple_salesforce import SalesforceResourceNotFound

from sattl.logger import logger
from sattl.salesforce.constants import ID, EXTERNAL_ID, RELATIONS, TYPE
from sattl.salesforce.connection import SalesforceConnection
from sattl.salesforce.external_id import SalesforceExternalID
from sattl.salesforce.relation import SalesforceRelation


def get_salesforce_objects(salesforce_connection: SalesforceConnection, content: list):
    sf_objects = []
    for sf_content in content:
        if not sf_content:
            continue
        case_insensitive_sf_content = CaseInsensitiveDict(sf_content)
        if (external_id := case_insensitive_sf_content.get(EXTERNAL_ID)) and isinstance(external_id, list):
            for _id in external_id:
                sf_object = copy(case_insensitive_sf_content)
                sf_object[EXTERNAL_ID] = _id
                sf_objects.append(SalesforceObject(salesforce_connection, sf_object))
            continue

        sf_objects.append(SalesforceObject(salesforce_connection, sf_content))

    return sf_objects


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

        self.relations = {k: SalesforceRelation(v) for k, v in relations.items() if v}
        self.sf_connection = salesforce_connection

        self.external_id = SalesforceExternalID(*dict(_content.pop(EXTERNAL_ID)).popitem())
        self.type = _content.pop(TYPE)
        self.content = CaseInsensitiveDict(_content)

    def __repr__(self):
        return str(self.original_content)

    def __eq__(self, other):
        return self.content == other.content

    def as_yaml_split_with_content(self, content: dict):
        return yaml.dump(dict(
            type=self.type, **self.external_id.as_dict(), **content
        )).splitlines(keepends=True)

    def refresh_relations(self):
        if not self.relations:
            return

        self.content.update({field: relation.get_id(self.sf_connection) for field, relation in self.relations.items()})
        self.relations = {}

    def differences(self, other):
        """
        To match other, self needs to have the same type, the same external id and other's content
        must be a subset of its
        """
        if (self.type == other.type and self.external_id == other.external_id and
                other.content.items() <= self.content.items()):
            return

        intersect_content = {key: self.content[key] for key in self.content.keys() & other.content.keys()}
        return "".join(
            ndiff(
                self.as_yaml_split_with_content(intersect_content),
                other.as_yaml_split_with_content(other.content)
            )
        )

    def load(self):
        try:
            logger.debug("Get object %s with %s = %s", self.type, self.external_id.field, self.external_id.value)
            result = self.sf_type.get_by_custom_id(self.external_id.field, self.external_id.quoted_value)
            for field in ["attributes", self.external_id.field]:
                result.pop(field, None)
            self.content = CaseInsensitiveDict(result)
            return True
        except SalesforceResourceNotFound:
            return False

    def delete(self):
        try:
            logger.debug("Delete object %s with %s = %s", self.type, self.external_id.field, self.external_id.value)
            self.sf_type.delete(f"{self.external_id.field}/{self.external_id.quoted_value}")
            return True
        except SalesforceResourceNotFound:
            pass
        return False

    def upsert(self):
        try:
            self.content.pop(ID, None)
            data = dict(self.content)
            logger.debug("Upsert object %s with %s = %s and content:\n%s",
                         self.type, self.external_id.field, self.external_id.value, data)
            self.sf_type.upsert(f"{self.external_id.field}/{self.external_id.quoted_value}", data)
            return True
        except SalesforceResourceNotFound:
            pass
        return False

    @property
    def sf_type(self):
        return self.sf_connection.__getattr__(self.type)
