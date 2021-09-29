from dataclasses import dataclass, field
from typing import List
from sattl.logger import logger


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
        for manifest in self.manifests:
            TestManifest(manifest).apply()
        if self.assertion:
            TestAssert(self.assertion).validate()


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
    __test__ = False

    def validate(self):
        logger.info(f"Assert state {self.filename}")
        raise Exception(f"{self.__class__.__name__} failed to assert {self.filename}")
