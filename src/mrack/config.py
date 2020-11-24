# Copyright 2020 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module to work with provisioning config.

Provisioning config is general project configuration shared between multiple jobs
"""

import logging
import os
from configparser import ConfigParser, NoOptionError, ParsingError

from mrack.errors import ConfigError

logger = logging.getLogger(__name__)


class ProvisioningConfig:
    """Represents loaded provisioning configuration."""

    def __init__(self, data):
        """Initialize provisioning configuration."""
        self._raw = data

    def raw(self):
        """Get raw configuration."""
        return self._raw()

    def __getitem__(self, key):
        """Get item from raw representation."""
        return self._raw[key]

    def get(self, key, default=None):
        """Get method as in dict for raw config."""
        return self._raw.get(key, default)


class MrackConfig:
    """Configuration for mrack itself."""

    def __init__(self, user_provided_path=None):
        """Init Mrack Config."""
        self._user_provided_path = user_provided_path
        self.config_name = "mrack.conf"
        self.section = "mrack"

    def get_config_paths(self):
        """Get possible mrack configuration file paths ordered by priority."""
        cwd = os.path.abspath(".")
        home = os.path.expanduser("~")
        paths = [
            f"{cwd}/{self.config_name}",
            f"{home}/.mrack/{self.config_name}",
            f"/etc/mrack/{self.config_name}",
        ]
        if self._user_provided_path:
            paths.insert(0, self._user_provided_path)
        return paths

    def load(self):
        """Load mrack configuration, first config file wins, rest is ignored."""
        cfg_paths = self.get_config_paths()
        self._parser = ConfigParser()
        chosen = None
        for cfg_path in cfg_paths:
            if os.path.exists(cfg_path):
                chosen = cfg_path
                break

        if not chosen:
            logger.debug("No config file found.")
            self._parser.read_dict({"mrack": {}})  # empty mrack section
            return

        try:
            logger.debug(f"Loading config file: {chosen}.")
            self._parser.read(chosen)
        except ParsingError:
            raise ConfigError(f"Invalid syntax in configuration file {chosen}.")

        if not self._parser.has_section(self.section):
            raise ConfigError(
                f"Configuration file {chosen} doesn't have "
                f"required section [{self.section}]."
            )

        return

    def __getitem__(self, key):
        """Get configuration value."""
        try:
            value = self._parser.get(self.section, key)
            return value
        except NoOptionError:
            raise KeyError(f"Configuration file doesn't have key: {key}")

    def get(self, key, default=None):
        """Get configuration value."""
        try:
            value = self._parser.get(self.section, key)
            logger.debug(f"Config key: {key}, value: {value}")
            return value
        except NoOptionError:
            return default

    def provisioning_config_path(self, default=None):
        """Return configured provisioning config path."""
        return self.get("provisioning-config", default)

    def db_path(self, default=None):
        """Return configured Mrack database path."""
        return self.get("mrackdb", default)

    def metadata_path(self, default=None):
        """Return configured job metadata path."""
        return self.get("metadata", default)

    def ansible_inventory_path(self, default=None):
        """Return configured path to Ansible inventory output."""
        return self.get("ansible-inventory", default)

    def pytest_multihost_path(self, default=None):
        """Return configured path to pytest-multihost configuration output."""
        return self.get("pytest-multihost", default)
