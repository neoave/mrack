# Copyright 2023 Red Hat Inc.
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

"""Mrack session."""

import os
from typing import Dict, Optional

from mrack.config import MrackConfig, ProvisioningConfig
from mrack.dbdrivers.file import FileDBDriver
from mrack.domain import Domain
from mrack.errors import ConfigError
from mrack.host import Host
from mrack.utils import NoSuchFileHandler, load_yaml


class MrackSession:
    """A provisioning re-usable session."""

    _database: FileDBDriver
    _mrack_config: MrackConfig
    _provisioning_config: ProvisioningConfig
    _metadata: Dict
    _hosts: Dict[str, Host]
    _domains: Dict[str, Domain]

    def __init__(self) -> None:
        """Init session."""
        self._metadata = {}
        self._hosts = {}
        self._domains = {}

    @property
    def database(self) -> FileDBDriver:  # pylint: disable=invalid-name
        """Get FileDBDriver object."""
        return self._database

    @property
    def config(self) -> MrackConfig:  # pylint: disable=invalid-name
        """Get MrackConfig object."""
        return self._mrack_config

    @property
    def provisioning_config(self) -> ProvisioningConfig:  # pylint: disable=invalid-name
        """Get ProvisioningConfig object."""
        return self._provisioning_config

    @property
    def metadata(self) -> Dict:  # pylint: disable=invalid-name
        """Get ProvisioningConfig object."""
        return self._metadata

    @property
    def hosts(self) -> Dict[str, Host]:  # pylint: disable=invalid-name
        """Get dictionary of hosts where key is host name."""
        return self._hosts

    @property
    def domains(self) -> Dict[str, Domain]:  # pylint: disable=invalid-name
        """Get dictionary of domains where key is domain name."""
        return self._domains

    def init(
        self,
        mrack_config_path: str,
        provisioning_config: Optional[ProvisioningConfig] = None,
        db_file: Optional[str] = None,
    ):
        """Initialize MrackSession object with all needed values."""
        self._init_mrack_config(mrack_config_path)

        db_path = db_file or self._mrack_config.db_path(default="./.mrackdb.json")
        p_config_path = (
            provisioning_config
            or self._mrack_config.provisioning_config_path(
                default="./provisioning-config.yaml"
            )
        )

        self._init_db(db_path)
        self._init_prov_config(p_config_path)

    def _init_db(self, path: str):
        """Initialize file database."""
        self._database = FileDBDriver(path)

    @NoSuchFileHandler(error="Provisioning config file not found: {path}")
    def _init_prov_config(self, path: str):
        """Load and initialize provisioning configuration."""
        self._provisioning_config = ProvisioningConfig(load_yaml(path))

    def init_metadata(self, user_defined_path: Optional[str]):
        """Load and initialize job metadata."""
        meta_path = user_defined_path or self._mrack_config.metadata_path()

        if not meta_path:
            raise ConfigError("Job metadata file path not provided.")
        if not os.path.exists(meta_path):
            raise ConfigError(f"Job metadata file not found: {meta_path}")

        self._metadata = load_yaml(meta_path)

    def _init_mrack_config(self, mrack_config_path: str):
        """Load and initialize mrack configuration."""
        self._mrack_config = MrackConfig(mrack_config_path)
        self._mrack_config.load()
