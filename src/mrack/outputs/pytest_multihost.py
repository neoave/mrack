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

"""pytest-multihost configuration file output module."""

import logging
import os
from copy import deepcopy

from mrack.outputs.utils import get_external_id
from mrack.utils import get_password, get_username, is_windows_host, save_yaml

DEFAULT_MHCFG_PATH = "pytest-multihost.yaml"

logger = logging.getLogger(__name__)


class PytestMultihostOutput:
    """
    Create a configuration file for python-pytest-multihost.

    From job metadata and provisioned information (DB).

    Structure of multihost config file is almost the same as our topology in job
    metadata definition.
    """

    def __init__(self, config, db, metadata, path=None):  # pylint: disable=invalid-name
        """Init the output module."""
        self._config = config
        self._db = db
        self._metadata = metadata
        self._path = path or DEFAULT_MHCFG_PATH

    def create_multihost_config(self):  # pylint: disable=too-many-branches
        """
        Create configuration file for python-pytest-multihost.

        Return in form of dict.
        """
        mhcfg = deepcopy(self._metadata)

        if "phases" in mhcfg:
            del mhcfg["phases"]

        if "config" in mhcfg:
            del mhcfg["config"]

        # topology config in metadata contains more values (os, group) than the ones
        # needed by pytest multihost. They need to be removed in order to work.
        host_allowed_attrs = [
            "name",
            "role",
            "hostname",
            "shortname",
            "external_hostname",
            "ip",
            "domain",
            "username",
            "password",
            "host_type",
        ]

        # Use values from provisioning-config mhcfg section - as default values
        # options defined in metadata takes precedence over options in
        # provisioning-config as it is "closer" to user.
        mhcfg = self._config.get("mhcfg", {}) | mhcfg

        for domain in mhcfg["domains"]:
            for host in domain["hosts"]:
                provisioned_host = self._db.hosts.get(host["name"])
                if not provisioned_host:
                    logger.error(f"Host {host['name']} not found in the database.")
                    continue

                password = get_password(provisioned_host, host, self._config)
                # pytest-multihost doesn't support different ssh_keys per host

                if password:
                    host["password"] = password

                host["ip"] = provisioned_host.ip_addr

                # Using IP as backup for external host name as pytest-multihost is using
                # external_hostname as the host to use in ssh command.
                # If it is not available it uses hostname, but we assume here that
                # hostname is internal and thus not resolvable. IP should be resolvable.
                host["external_hostname"] = get_external_id(
                    provisioned_host, host, self._config
                )

                if is_windows_host(host):
                    # Set username for Windows, as default for multihost is often 'root'
                    # which doesn't usually work there. But do not set it for other OSes
                    # due to:
                    #  7bb230e170ac0a2373a2316ef23a26bfcb681ad9
                    # TODO: come up with a configurable mechanism which is not based on
                    # so many assumptions.
                    username = get_username(provisioned_host, host, self._config)
                    if username:
                        host["username"] = username

                group = host.get("group")
                if not group:
                    groups = host.get("groups")
                    if isinstance(groups, list) and len(groups):
                        group = groups[0]
                    else:
                        group = ""  # group is required, but not part of output

                if group == "ad_root":
                    mhcfg["ad_top_domain"] = domain["name"]
                    mhcfg["ad_hostname"] = host["name"]
                    mhcfg["ad_ip"] = host["ip"]
                elif group == "ad_subdomain":
                    mhcfg["ad_sub_domain"] = domain["name"]
                    mhcfg["ad_sub_hostname"] = host["name"]
                    mhcfg["ad_sub_ip"] = host["ip"]

                host_custom_attrs = deepcopy(host.get("pytest_multihost", {}))

                rm_keys = [key for key in host.keys() if key not in host_allowed_attrs]
                for key in rm_keys:
                    del host[key]

                if host_custom_attrs:
                    host.update(host_custom_attrs)

            domain_rm_keys = [
                key for key in domain.keys() if key not in ["name", "type", "hosts"]
            ]
            for key in domain_rm_keys:
                del domain[key]

        # ssh_key_filename must be absolute as it can be used from a different
        # working directory, e.g. running tests from git repo
        ssh_key_filename = mhcfg.get("ssh_key_filename")

        # Update with SSH key path only if not already defined in mhcfg
        if ssh_key_filename and not self._metadata.get("ssh_key_filename"):
            mhcfg["ssh_key_filename"] = os.path.abspath(ssh_key_filename)

        return mhcfg

    def create_output(self):
        """Create the target output file."""
        mhcfg = self.create_multihost_config()
        save_yaml(self._path, mhcfg)
        if self._path:
            logger.info(f"Created: {self._path}")
        return mhcfg
