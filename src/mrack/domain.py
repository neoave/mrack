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

"""Domain object."""

from typing import Dict, Set

from errors import MrackError

from mrack.host import Host
from mrack.session import MrackSession


class Domain:
    """Domain.

    Domain as defined in job metadata file
    """

    _session: MrackSession
    _name: str
    _type: str
    _network: str
    _hosts: Set[str]

    def __init__(
        self,
        session,
        name,
        type,
        network,
        hosts: Set[str],
    ):
        """Initialize domain object."""
        self._session = session
        self._name = name
        self._type = type
        self._network = network
        self._hosts = hosts

    def __str__(self):
        """Return string representation of domain."""
        host_count = len(self._hosts)
        out = f"{self._name} {self._type} {self._network}, hosts: {host_count}"

        return out

    def to_json(self) -> Dict:
        """Transform object into representation which is acceptable by `json.dump`."""
        return {
            "name": self._name,
            "type": self._type,
            "network": self._network,
            "hosts": self._hosts,
        }

    @property
    def name(self) -> str:
        """Get host provisioning provider."""
        return self._name

    @property
    def type(self) -> str:
        """Get host operating system."""
        return self._type

    @property
    def network(self) -> str:
        """Get host group."""
        return self._network

    @property
    def hosts(self) -> Set[Host]:
        """Get provider host id."""
        hosts: Set[Host] = set()
        for host in self._hosts:
            try:
                hosts.add(self._session.hosts[host])
            except ValueError:
                raise MrackError(f"Session is missing host: {host}")

        return hosts


def domain_from_json(session: MrackSession, data: Dict) -> Domain:
    """Reverse method to Host.__json__() after json.loads()."""
    domain = Domain(
        session,
        data["name"],
        data["type"],
        data["network"],
        data["hosts"],
    )
    return domain
