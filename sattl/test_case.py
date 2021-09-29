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
        for filename in sorted(os.listdir(self.path)):
            if not (filename and DELIMITER in filename and os.path.isfile(filename)):
                continue
            prefix = filename.split(DELIMITER)[0]
            if not prefix:
                logger.warning(f"Prefix of file {filename} is empty")
                continue
            step = self.content.setdefault(prefix, TestStep(prefix))
            if "assert" not in filename.lower():
                step.add_manifest(filename)
                continue
            step._asserts = filename

        if not self.content:
            raise AttributeError(f"path {self.path} is empty")

    def run(self):
        for step in self.content.values():
            step.run()
