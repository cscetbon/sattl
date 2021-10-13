from dataclasses import dataclass, field
from typing import List
from sattl.logger import logger
from sattl.salesforce import SalesforceConnection, SalesforceObject
from sattl.retry_with_timeout import RetryWithTimeout
import yaml
from copy import copy


@dataclass
class TestStep:
    prefix: str
    assert_timeout: int
    sf_connection: SalesforceConnection = None
    assertion: str = None
    delete: str = None
    manifests: List = field(default_factory=list)
    __test__ = False

    def __post_init__(self):
        if self.manifests is None:
            self.manifests = []

    def add_manifest(self, filename):
        self.manifests.append(filename)

    def _set_attribute(self, name, value):
        if current_value := self.__getattribute__(name):
            raise Exception(f"{name.title()} already set to {current_value}. You can't have more than one.")
        self.__setattr__(name, value)

    def set_assertion(self, filename):
        self._set_attribute("assertion", filename)

    def set_delete(self, filename):
        self._set_attribute("delete", filename)

    def run(self):
        logger.info(f"Running step {self.prefix}")
        for manifest in self.manifests:
            TestManifest(manifest, self.sf_connection).apply()
        if self.assertion:
            RetryWithTimeout(TestAssert(self.assertion, self.sf_connection).validate, seconds=self.assert_timeout)
        if self.delete:
            TestDelete(self.delete, self.sf_connection).apply()


@dataclass
class TestStepElement:
    filename: str
    sf_connection: SalesforceConnection
    __test__ = False

    def get_sf_objects_from_file(self):
        with open(self.filename) as fh:
            return [
                SalesforceObject(self.sf_connection, content)
                for content in yaml.load_all(fh, Loader=yaml.FullLoader) if content
            ]


class TestManifest(TestStepElement):

    def apply(self):
        logger.info(f"Applying manifest {self.filename}")
        for sf_object in self.get_sf_objects_from_file():
            sf_object.refresh_relations()
            if not sf_object.upsert():
                raise Exception(f"Failed to upsert object {sf_object}")


class TestAssert(TestStepElement):

    def validate(self):
        logger.info(f"Asserting objects in {self.filename}")
        for sf_object in self.get_sf_objects_from_file():
            sf_object.refresh_relations()
            current = copy(sf_object)
            if not current.load():
                raise Exception("Assert failed because the object can't be accessed")
            if diff := current.differences(sf_object):
                raise Exception(f"Assert failed because there are differences:\n{diff}")


class TestDelete(TestStepElement):

    def apply(self):
        logger.info(f"Delete objects in {self.filename}")
        for sf_object in self.get_sf_objects_from_file():
            sf_object.delete()
