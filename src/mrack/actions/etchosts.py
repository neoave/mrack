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

"""Etc-Hosts actions."""

import getpass
import logging

from mrack.actions.action import DBAction
from mrack.errors import ApplicationError, ConfigError
from mrack.host import STATUS_ACTIVE

logger = logging.getLogger(__name__)

MRACK_START = "# Managed by mrack - start\n"
MRACK_END = "# Managed by mrack - end\n"


class EtcHostsUpdater:
    """Object to manipulate with /etc/hosts file."""

    def __init__(self, path="/etc/hosts"):
        """Init the updater."""
        self.path = path
        with open(self.path, "r", encoding="utf-8") as etc_hosts:
            self.lines = etc_hosts.readlines()

        # Trigger validation
        self._locate_mrack_section()

    def _locate_mrack_section(self):
        """Locate mrack managed section."""
        start = -1
        end = -1
        mrack_lines = []
        errors = []
        for index, line in enumerate(self.lines):
            if MRACK_START in line:
                if start != -1:
                    errors.append("Multiple start marks.")
                start = index
            if MRACK_END in line:
                if end != -1:
                    errors.append("Multiple end marks.")
                end = index
            if start != -1 and end == -1 and index > start:
                mrack_lines.append([index, line])

        # Check errors:
        if start == -1 and end != -1:
            errors.append("Doesn't have start mark.")
        if start != -1 and end == -1:
            errors.append("Doesn't have end mark.")
        if end < start:
            errors.append("End mark before start mark.")

        if errors:
            error = "/etc/hosts has broken mrack managed section and needs fixing:\n"
            for err in errors:
                error += f"   {err}\n"
            raise ConfigError(error)

        return (start, end, mrack_lines)

    def add_hosts(self, hosts):
        """Add lines for hosts."""
        start, end, mrack_lines = self._locate_mrack_section()

        if start == -1:
            start = len(self.lines)
            self.lines.append(MRACK_START)
            end = start + 1
            self.lines.append(MRACK_END)

        for host in hosts:
            new_line = f"{host.ip_addr} {host.name}\n"
            for mrack_line in mrack_lines:
                idx, line = mrack_line
                # update: /etc/hosts has already a line for the host
                if host.name in line:
                    self.lines[idx] = new_line
                    mrack_line[1] = new_line
                    break
            else:
                mrack_lines.append([end, new_line])
                self.lines.insert(end, new_line)
                end += 1

    def clear(self):
        """Remove mrack managed lines."""
        start, end, _mrack_lines = self._locate_mrack_section()
        if start:
            del self.lines[start : end + 1]

    def save(self):
        """Save changes into /etc/hosts."""
        try:
            with open(self.path, "w", encoding="utf-8") as etc_file:
                etc_file.writelines(self.lines)
        except PermissionError as perm_err:
            name = getpass.getuser()
            err = (
                f"Error: Not enough permissions to write into file: {self.path}.\n\n"
                "Consider running mrack as root for this command e.g. via sudo "
                "or add yourself the necessary rights, e.g. by: \n"
                f"  $ sudo setfacl -m {name}:rw {self.path}"
            )
            raise ApplicationError(err) from perm_err


class EtcHostsUpdate(DBAction):
    """Add active vms to /etc/hosts file."""

    def __init__(self, db_driver=None):
        """Initialize the /etc/hosts update action."""
        super().__init__(db_driver=db_driver)
        self.updater = EtcHostsUpdater()

    def update(self):
        """Update /etc/hosts."""
        logger.info("Adding hosts to /etc/hosts file")

        hosts = [h for h in self._db_driver.hosts.values() if h.status == STATUS_ACTIVE]
        self.updater.add_hosts(hosts)
        self.updater.save()

        logger.info("Done")

    def clear(self):
        """Clear mrack records in /etc/hosts."""
        logger.info("Clearing mrack records in /etc/hosts.")

        self.updater.clear()
        self.updater.save()

        logger.info("Done")
