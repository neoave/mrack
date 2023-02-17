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
from typing import Dict, Optional

from mrack.domain import domain_from_json
from mrack.host import host_from_json
from mrack.session import MrackSession
from mrack.utils import load_json, save_to_json

DOMAINS_KEY = "domains"
HOSTS_KEY = "hosts"


class FileDBDriver:
    """File database driver.

    Serialize session's hosts and domains into JSON file.

    Or loads it from JSON file into session.
    """

    _session: MrackSession
    _path: str
    _raw_data: Optional[Dict]

    def __init__(self, session: MrackSession, file_path: str):
        """Initialize DB driver."""
        self._session = session
        self._path = file_path
        self._raw_data = None
        self.load()

    def load(self):
        """Load configuration from file."""
        self._hosts = {}
        if not path.exists(self._path):
            self._raw_data = {
                DOMAINS_KEY: [],
                HOSTS_KEY: [],
            }
            return

        self._raw_data = load_json(self._path)

        raw_hosts = self._raw_data.get(HOSTS_KEY, [])
        raw_domains = self._raw_data.get(DOMAINS_KEY, [])

        self._hosts = {}
        for raw_host in raw_hosts:
            host = host_from_json(self._session, raw_host)
            self._session.hosts[host.name] = host

        for raw_domain in raw_domains:
            domain = domain_from_json(self._session, raw_domain)
            self._session.domains[domain.name] = domain

    def save(self):
        """Save configuration to file."""
        hosts = [host.to_json() for host in self._session.hosts.values()]
        domains = [domain.to_json() for domain in self._session.domains.values()]
        self._raw_data[HOSTS_KEY] = hosts
        self._raw_data[DOMAINS_KEY] = domains
        save_to_json(self._path, self._raw_data)
