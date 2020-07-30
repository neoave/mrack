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

"""SSH action module."""

import logging
import os
import subprocess

from mrack.errors import ApplicationError
from mrack.host import STATUS_ACTIVE
from mrack.utils import get_host_from_metadata, get_password, get_ssh_key, get_username

logger = logging.getLogger(__name__)


class SSH:
    """SSH action.

    SSH all still active provisioned host. Save the state to DB.
    """

    def init(self, config, metadata, db_driver):
        """Initialize the SSH action."""
        self._config = config
        self._metadata = metadata
        self._db = db_driver

    def pick_host_interactively(self, hosts):
        """Print list of host and let user to choose one."""
        # With only 1 host available, we can pick it and save time
        if len(hosts) == 1:
            return hosts[0].name

        for idx, host in enumerate(hosts):
            logger.info(f"{idx}: {host}")

        while True:
            try:
                host_idx = int(input("Enter a number of host to ssh into: "))
            except ValueError:
                logger.info("Entered value is not a number.")
                continue
            if host_idx < 0 or host_idx >= len(hosts):
                logger.info("Entered value is not a number of any host.")
                continue
            break

        return hosts[host_idx].name

    def find_host(self, hostname):
        """Find active host based on hostname or interactively."""
        hosts = self._db.hosts
        active_hosts = [h for h in hosts.values() if h.status == STATUS_ACTIVE]

        if not hosts:
            raise ApplicationError("No hosts provisioned.")

        if not active_hosts:
            raise ApplicationError("No active host available.")

        if not hostname:
            hostname = self.pick_host_interactively(active_hosts)

        host = hosts.get(hostname)
        if not host:
            raise ApplicationError("Specified host does not exist.")

        if host.status != STATUS_ACTIVE:
            raise ApplicationError("Selected host is not active.")

        return host

    def ssh_to_host(self, host):
        """SSH to the selected host."""
        my_env = os.environ.copy()

        run_args = {
            "env": my_env,
            "shell": True,
        }

        cmd = ["ssh"]
        cmd.extend(["-o", "'StrictHostKeyChecking=no'"])
        cmd.extend(["-o", "'UserKnownHostsFile=/dev/null'"])

        meta_host, domain = get_host_from_metadata(self._metadata, host.name)
        username = get_username(host, meta_host, self._config)
        password = get_password(host, meta_host, self._config)
        ssh_key = get_ssh_key(host, meta_host, self._config)

        if username:
            cmd.extend(["-l", username])
        if ssh_key:
            cmd.extend(["-i", ssh_key])
        psw_input = None
        if password and not ssh_key:
            cmd.extend("-o", "'PasswordAuthentication'")
            psw_input = f"{password}\n"

        cmd.append(host.ip)  # Destination

        cmd = " ".join(cmd)

        logger.info(cmd)
        process = subprocess.Popen(cmd, **run_args)
        process.communicate(input=psw_input)
        return process.returncode

    def ssh(self, hostname):
        """Execute the SSH action."""
        host = self.find_host(hostname)
        self.ssh_to_host(host)
