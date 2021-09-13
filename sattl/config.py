import json
import os

_OVERRIDE_FILENAME = 'config.json'
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OVERRIDE_FILE_PATH = os.path.join(_ROOT_DIR, _OVERRIDE_FILENAME)
_SF_PASSWORD = 'sf_password'
_SF_USERNAME = 'sf_username'


def _read_from_config_file():
    return json.load(open(_OVERRIDE_FILE_PATH))


class Config:

    def __init__(self, is_sandbox, domain):
        self._is_sandbox = is_sandbox
        self._domain = domain
        config = _read_from_config_file()
        if self.domain not in config:
            raise Exception(f"domain {self.domain} can't be found in configuration file")
        self._config = config[self.domain]

    @property
    def domain(self):
        return self._domain

    @property
    def is_sandbox(self):
        return self._is_sandbox

    @property
    def sf_username(self):
        return self._config.get(_SF_USERNAME)

    @property
    def sf_password(self):
        return self._config.get(_SF_PASSWORD)
