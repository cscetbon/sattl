import os
import re
from dataclasses import dataclass, field
from typing import Dict
from collections import OrderedDict
from sattl.logger import logger
from sattl.salesforce import get_sf_connection
from sattl.test_step import TestStep
from sattl.retry_with_timeout import TimeoutException


DELIMITER = "-"
RE_IS_YAML = re.compile(r"\.ya?ml$")


def _is_yaml_file(path, filename):
    return filename and RE_IS_YAML.search(filename) and os.path.isfile(os.path.join(path, filename))


def _get_files(path):
    return [
        os.path.join(path, filename) for filename in sorted(os.listdir(path))
        if _is_yaml_file(path, filename) and DELIMITER in filename
    ]


@dataclass
class TestCase:
    path: str
    sf_org: str
    timeout: int
    is_sandbox: bool = True
    content: Dict[str, TestStep] = field(default_factory=OrderedDict)

    __test__ = False

    def setup(self):
        for filename in _get_files(self.path):
            prefix = os.path.basename(filename).split(DELIMITER)[0]
            if not prefix:
                logger.warning(f"Prefix of file {filename} is empty")
                continue
            step = self.content.setdefault(
                prefix, TestStep(prefix, assert_timeout=self.timeout,
                                 sf_connection=get_sf_connection(self.is_sandbox, self.sf_org))
            )
            if "assert" in filename.lower():
                step.set_assertion(filename)
                continue

            if "delete" in filename.lower():
                step.set_delete(filename)
                continue

            step.add_manifest(filename)

        if not self.content:
            raise AttributeError(f"path {self.path} is empty")

    def run(self):
        try:
            for step in self.content.values():
                step.run()
        except TimeoutException as exc:
            print(f"\n{exc}")
            exit(1)
