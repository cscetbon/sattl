from dataclasses import dataclass, field
from typing import List
from sattl.logger import logger
from sattl.salesforce import SalesforceConnection, SalesforceObject, get_sf_connection
import yaml
from copy import copy


@dataclass
class TestStep:
    prefix: str
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
        sf_connection = get_sf_connection()
        for manifest in self.manifests:
            TestManifest(manifest).apply()
        if self.assertion:
            TestAssert(self.assertion, sf_connection).validate()


@dataclass
class TestManifest:
    filename: str
    __test__ = False

    def apply(self):
        logger.info(f"Applies manifest {self.filename}")
        raise Exception(f"{self.__class__.__name__} failed to apply {self.filename}")


@dataclass
class TestAssert:
    filename: str
    sf_connection: SalesforceConnection
    __test__ = False

    def get_sf_objects(self):
        with open(self.filename) as fh:
            return [
                SalesforceObject(self.sf_connection, content)
                for content in yaml.load_all(fh, Loader=yaml.FullLoader) if content
            ]

    def validate(self):
        logger.info(f"Asserting objects in {self.filename}")
        for sf_object in self.get_sf_objects():
            current = copy(sf_object)
            current.get()
            if not current.matches(sf_object):
                raise Exception(f"Failed to assert object {sf_object}")
