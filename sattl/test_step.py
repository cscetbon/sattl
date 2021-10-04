from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List
from sattl.logger import logger
from sattl.salesforce import SalesforceConnection, SalesforceObject, get_sf_connection
import yaml
from copy import copy


@dataclass
class TestStep:
    prefix: str
    sf_connection: SalesforceConnection = None
    assertion: str = None
    manifests: List = field(default_factory=list)
    __test__ = False

    def __post_init__(self):
        if self.manifests is None:
            self.manifests = []

    def add_manifest(self, filename):
        self.manifests.append(filename)

    def set_assertion(self, filename):
        if self.assertion:
            raise Exception(f"Assertion already set to {self.assertion}. You can't have more than one.")
        self.assertion = filename

    def run(self):
        logger.info(f"Running step {self.prefix}")
        for manifest in self.manifests:
            TestManifest(manifest, self.sf_connection).validate()
        if self.assertion:
            TestAssert(self.assertion, self.sf_connection).validate()


def _get_sf_objects(sf_connection, filename):
    with open(filename) as fh:
        return [
            SalesforceObject(sf_connection, content)
            for content in yaml.load_all(fh, Loader=yaml.FullLoader) if content
        ]


@dataclass
class TestElement:
    filename: str
    sf_connection: SalesforceConnection
    __test__ = False

    @abstractmethod
    def validate(self):
        pass


class TestManifest(TestElement):

    def validate(self):
        logger.info(f"Applying manifest {self.filename}")
        for sf_object in _get_sf_objects(self.sf_connection, self.filename):
            sf_object.refresh_relations()
            if not sf_object.upsert():
                raise Exception(f"Failed to apply object {sf_object}")


class TestAssert(TestElement):

    def validate(self):
        logger.info(f"Asserting objects in {self.filename}")
        for sf_object in _get_sf_objects(self.sf_connection, self.filename):
            sf_object.refresh_relations()
            current = copy(sf_object)
            if not (current.load() and current.matches(sf_object)):
                raise Exception(f"Failed to assert object {sf_object}")
