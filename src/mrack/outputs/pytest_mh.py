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

"""pytest-mh configuration file output module."""

import logging

from mrack.outputs.utils import get_external_id, merge_dict
from mrack.utils import get_fqdn, get_os_type, get_password, get_username, save_yaml

DEFAULT_MHCFG_PATH = "pytest-mh.yaml"

logger = logging.getLogger(__name__)


class PytestMhOutput:
    """
    Create a configuration file for pytest-mh.

    From job metadata and provisioned information (DB).

    Structure of mh config file is almost the same as our topology in job
    metadata definition.
    """

    def __init__(self, config, db, metadata, path=None):
        """Init the output module."""
        self._config = config
        self._db = db
        self._metadata = metadata
        self._path = path or DEFAULT_MHCFG_PATH

    def create_mh_config(self):
        """
        Create configuration file for python-pytest-multihost.

        Return in form of dict.
        """
        cfg = {"domains": []}
        for domain in self._metadata.get("domains", []):
            cfgdom = {"id": domain["name"], "hosts": []}
            cfg["domains"].append(cfgdom)

            for host in domain.get("hosts", []):
                if "role" not in host:
                    continue

                provisioned_host = self._db.hosts.get(host["name"], None)
                if not provisioned_host:
                    logger.error(f"Host {host['name']} not found in the database.")
                    continue

                hostcfg = {
                    "hostname": get_fqdn(host["name"], domain.get("name", "")),
                    "os": {
                        "family": get_os_type(host),
                    },
                    "role": host["role"],
                    "conn": {
                        "type": "ssh",
                        "host": get_external_id(provisioned_host, host, self._config),
                    },
                }

                if get_os_type(host) == "windows":
                    username = get_username(provisioned_host, host, self._config)
                    if username:
                        hostcfg["conn"]["username"] = username

                    password = get_password(provisioned_host, host, self._config)
                    if password:
                        hostcfg["conn"]["password"] = password

                cfgdom["hosts"].append(merge_dict(hostcfg, host.get("pytest_mh", {})))

        return cfg

    def create_output(self):
        """Create the target output file."""
        mhcfg = self.create_mh_config()
        save_yaml(self._path, mhcfg, sort_keys=False)
        if self._path:
            logger.info(f"Created: {self._path}")
        return mhcfg
