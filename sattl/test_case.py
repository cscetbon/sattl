import os
from typing import Dict
from collections import OrderedDict
from sattl.logger import logger
from sattl.salesforce import get_sf_connection
from sattl.test_step import TestStep


DELIMITER = "-"


def _get_files(path):
    return [
        filename for filename in sorted(os.listdir(path)) if (
                filename and DELIMITER in filename and os.path.isfile(filename)
        )
    ]


class TestCase:
    __test__ = False

    def __init__(self, path, timeout=30):
        if not os.access(path, os.R_OK):
            raise AttributeError(f"path {path} is not readable")
        self.path = path
        self.timeout = timeout
        self.content: Dict[str, TestStep] = OrderedDict()

    def setup(self):
        for filename in _get_files(self.path):
            prefix = filename.split(DELIMITER)[0]
            if not prefix:
                logger.warning(f"Prefix of file {filename} is empty")
                continue
            step = self.content.setdefault(prefix, TestStep(prefix, sf_connection=get_sf_connection()))
            if "assert" in filename.lower():
                step.set_assertion(filename)
                continue
            step.add_manifest(filename)

        if not self.content:
            raise AttributeError(f"path {self.path} is empty")

    def run(self):
        for step in self.content.values():
            step.run(self.timeout)
