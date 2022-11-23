# Copyright 2021 Red Hat Inc.
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

"""Global mrack context object."""
import os
from typing import Dict

from mrack.config import MrackConfig, ProvisioningConfig
from mrack.dbdrivers.file import FileDBDriver
from mrack.errors import ConfigError
from mrack.utils import NoSuchFileHandler, load_yaml


class GlobalContext:
    """Global context class to store the mrack configuration."""

    def __init__(self) -> None:
        """Init empty GlobalContext class."""
        self.database = None
        self.mrack_conf = None
        self.provisioning_config = None
        self.metadata: Dict = {}

    @property
    def DB(self):  # pylint: disable=invalid-name
        """Get FileDBDriver object."""
        return self.database

    @property
    def CONFIG(self):  # pylint: disable=invalid-name
        """Get MrackConfig object."""
        return self.mrack_conf

    @property
    def PROV_CONFIG(self):  # pylint: disable=invalid-name
        """Get ProvisioningConfig object."""
        return self.provisioning_config

    @property
    def METADATA(self):  # pylint: disable=invalid-name
        """Get ProvisioningConfig object."""
        return self.metadata

    def init(self, mrack_config, provisioning_config=None, db_file=None):
        """Initialize Global Context object with all needed values."""
        self._init_mrack_config(mrack_config)
        self.mrack_conf.load()

        db_path = db_file or self.mrack_conf.db_path(default="./.mrackdb.json")
        p_config_path = provisioning_config or self.mrack_conf.provisioning_config_path(
            default="./provisioning-config.yaml"
        )

        self._init_db(db_path)
        self._init_prov_config(p_config_path)

    def _init_db(self, path):
        """Initialize file database."""
        self.database = FileDBDriver(path)

    @NoSuchFileHandler(error="Provisioning config file not found: {path}")
    def _init_prov_config(self, path):
        """Load and initialize provisioning configuration."""
        self.provisioning_config = ProvisioningConfig(load_yaml(path))

    def init_metadata(self, user_defined_path):
        """Load and initialize job metadata."""
        meta_path = user_defined_path or self.mrack_conf.metadata_path()

        if not meta_path:
            raise ConfigError("Job metadata file path not provided.")
        if not os.path.exists(meta_path):
            raise ConfigError(f"Job metadata file not found: {meta_path}")

        self.metadata = load_yaml(meta_path)

    def _init_mrack_config(self, mrack_config_path):
        """Load and initialize mrack configuration."""
        self.mrack_conf = MrackConfig(mrack_config_path)


# Singleton context holder
global_context = GlobalContext()
