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

from mrack.actions.action import Action
from mrack.context import global_context
from mrack.errors import ApplicationError
from mrack.host import STATUS_ACTIVE
from mrack.utils import get_ssh_options, get_username_pass_and_ssh_key
from mrack.utils import ssh_to_host as utils_ssh_to_host

try:
    from mrack.providers.utils.podman import Podman
except ModuleNotFoundError:
    pass  # Ignore the module import error if plugin not available

logger = logging.getLogger(__name__)


class SSH(Action):
    """SSH action.

    SSH all still active provisioned host. Save the state to DB.
    """

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
        hosts = self._db_driver.hosts
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
        username, password, ssh_key = get_username_pass_and_ssh_key(
            host, global_context
        )
        ssh_options = get_ssh_options(
            host, global_context.METADATA, global_context.PROV_CONFIG
        )
        return utils_ssh_to_host(
            host,
            username=username,
            password=password,
            ssh_key=ssh_key,
            interactive=True,
            ssh_options=ssh_options,
        )

    def is_container_env(self, host):
        """Check if host is using local container technology."""
        return host.provider.name in ["docker", "podman"]

    def attach_interactive_container(self, host):
        """Simulate SSH by attaching an interactive session to a container."""
        if host.provider.name == "podman":
            podman = Podman()
            podman.interactive(host.host_id)
        else:
            raise NotImplementedError("Docker is not yet supported.")

    def ssh(self, hostname):
        """Execute the SSH action."""
        host = self.find_host(hostname)
        if self.is_container_env(host):
            self.attach_interactive_container(host)
        else:
            self.ssh_to_host(host)
