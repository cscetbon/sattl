import os
from typing import Dict
from collections import OrderedDict
from sattl.logger import logger
from sattl.test_step import TestStep


DELIMITER = "-"


class TestCase:
    __test__ = False

    def __init__(self, path):
        if not os.access(path, os.R_OK):
            raise AttributeError(f"path {path} is not readable")
        self.path = path
        self.content: Dict[str, TestStep] = OrderedDict()

    def setup(self):
        for f in sorted(os.listdir(self.path)):
            if not os.path.isfile(f) or not len(f) or DELIMITER not in f:
                continue
            prefix = f.split(DELIMITER)[0]
            if not prefix:
                logger.warning(f"Prefix of file {f} is empty")
                continue
            step = self.content.setdefault(prefix, TestStep(prefix))
            if "assert" not in f.lower():
                step.append(f)
                continue
            step._asserts = f

    def run(self):
        for _, step in self.content.items():
            step.run()
