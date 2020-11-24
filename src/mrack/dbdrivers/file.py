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

"""File database driver module."""

from os import path

from mrack.host import host_from_json
from mrack.utils import load_json, save_to_json

HOSTS_KEY = "hosts"


class FileDBDriver:
    """File database driver.

    Serialize and load information into JSON file.
    """

    def __init__(self, file_path):
        """Initialize DB driver."""
        self._path = file_path
        self._hosts = {}
        self._raw_data = None
        self.save_on_change = True
        self.load()

    def load(self):
        """Load configuration from file."""
        self._hosts = {}
        if not path.exists(self._path):
            self._raw_data = {HOSTS_KEY: {}}
            return self._hosts

        self._raw_data = load_json(self._path)
        raw_hosts = self._raw_data.get(HOSTS_KEY, [])

        self._hosts = {}
        for raw_host in raw_hosts:
            host = host_from_json(raw_host)
            self._hosts[host.name] = host

        return self._hosts

    def save(self):
        """Save configuration to file."""
        hosts = [host.to_json() for host in self._hosts.values()]
        self._raw_data[HOSTS_KEY] = hosts
        save_to_json(self._path, self._raw_data)

    @property
    def hosts(self):
        """Get all host objects loaded or to be saved."""
        return self._hosts

    def add_hosts(self, hosts):
        """Add a host object.

        Save it to file automatically if `save_on_change` is set to True.
        """
        for host in hosts:
            self.hosts[host.name] = host

        if self.save_on_change:
            self.save()

    def update_hosts(self, hosts):
        """Update managed host objects.

        Only adds.
        """
        self.add_hosts(hosts)

    def delete_host(self, host):
        """Delete host object."""
        if host.name in self.hosts:
            del self.hosts[host.name]
