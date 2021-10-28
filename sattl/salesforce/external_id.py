from dataclasses import dataclass
from typing import Any
from urllib.parse import quote


@dataclass
class SalesforceExternalID:
    field: str
    value: Any

    def __post_init__(self):
        if not (self.field and self.value):
            raise Exception(f"ExternalID field and value must be non empty. {self!r}")

    def as_dict(self):
        return {self.field: self.value}

    @property
    def quoted_value(self):
        return quote(self.value, safe=' ')
