import os
from enum import Enum
from collections import OrderedDict
from sattl.logger import logger
from typing import List
from dataclasses import dataclass, field

DELIMITER = "-"


class TestCase:

    def __init__(self, path):
        if not os.access(path, os.R_OK):
            raise AttributeError(f"path {path} is not readable")
        self.path = path
        self.content = OrderedDict()

    def setup(self):
        for f in sorted(os.listdir(self.path)):
            if not os.path.isfile(f) or not len(f) or DELIMITER not in f:
                continue
            prefix = f.split(DELIMITER)[0]
            if not len(prefix):
                logger.warning(f"Prefix of file {f} is empty")
                continue
            step_type = StepType.Assert
            if "assert" not in f.lower():
                step_type = StepType.Manifest
            self.content.setdefault(prefix, {}).setdefault(step_type, Step(step_type)).append(f)

    def run(self):
        pass


class StepType(Enum):
    Manifest = 1
    Assert = 2


@dataclass
class Step:
    _type: StepType
    content: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.content is None:
            self.content = []

    def append(self, f):
        self.content.append(f)
