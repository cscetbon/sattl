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
            logger.info(f"Applies manifest {manifest}")
        if self._assert:
            logger.info(f"Assert state {self._assert}")
