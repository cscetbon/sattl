from dataclasses import dataclass, field
from typing import List
from sattl.logger import logger


@dataclass
class TestStep:
    prefix: str
    _assert: str = None
    manifests: List = field(default_factory=list)
    __test__ = False

    def __post_init__(self):
        if self.manifests is None:
            self.manifests = []

    def append(self, f):
        self.manifests.append(f)

    def run(self):
        logger.info(f"Running step {self.prefix}")
        for manifest in self.manifests:
            TestManifest(manifest).apply()
        if self._assert:
            TestAssert(self._assert).state()


@dataclass
class TestManifest:
    filename: str
    __test__ = False

    def apply(self, value):
        logger.info(f"Applies manifest {self.filename}")
        if not value:
            raise Exception(f"{self.__class__.__name__} failed to apply {self.filename}")
        return value


@dataclass
class TestAssert:
    filename: str
    __test__ = False

    def state(self, value):
        logger.info(f"Assert state {self.filename}")
        if not value:
            raise Exception(f"{self.__class__.__name__} failed to state {self.filename}")
        return value
