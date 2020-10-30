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

"""Host object."""

from mrack.providers import providers
from mrack.utils import object2json

STATUS_PENDING = "pending"
STATUS_PROVISIONING = "provisioning"
STATUS_ACTIVE = "active"
STATUS_ERROR = "error"
STATUS_DELETED = "deleted"
STATUS_DELETING = "deleting"
STATUS_OTHER = "other"

STATUSES = [
    STATUS_PENDING,
    STATUS_PROVISIONING,
    STATUS_ACTIVE,
    STATUS_ERROR,
    STATUS_DELETED,
    STATUS_DELETING,
]


def host_from_json(host_data):
    """Reverse method to Host.__json__() after json.loads()."""
    provider_name = host_data["provider"]
    provider = providers.get(provider_name)
    host = Host(
        provider,
        host_data["id"],
        host_data["name"],
        host_data["ips"],
        host_data["status"],
        host_data["rawdata"],
        host_data["username"],
        host_data["password"],
        host_data["error"],
    )
    return host


class Host:
    """Provisioned host.

    Normalized values from providers to offer consistent interface.
    """

    def __init__(
        self,
        provider,
        id,
        name,
        ips,
        status,
        rawdata,
        username=None,
        password=None,
        error_obj=None,
    ):
        """Initialize host object."""
        self._provider = provider
        self._id = id
        self._name = name
        self._ips = ips
        self._status = status
        self._username = username
        self._password = password
        self._rawdata = rawdata
        self._error = error_obj

    def __str__(self):
        """Return string representation of host."""
        net_str = " ".join(self._ips)

        out = (
            f"{self._status} {self._id} {self._name} {net_str} {self._username} "
            f"{self._password}"
        )

        if self._error:
            o = [out, "Error:", object2json(self._error)]
            out = "\n".join(o)
        return out

    def to_json(self):
        """Transform object into representation which is acceptable by `json.dump`."""
        return {
            "provider": self._provider.name,
            "id": self._id,
            "name": self._name,
            "ips": self._ips,
            "status": self._status,
            "username": self._username,
            "password": self._password,
            "rawdata": self._rawdata,
            "error": self._error,
        }

    @property
    def provider(self):
        """Get host provisioning provider."""
        return self._provider

    @property
    def id(self):
        """Get provider host id."""
        return self._id

    @property
    def name(self):
        """Get host name."""
        return self._name

    @property
    def ips(self):
        """Get host IP addresses."""
        return self._ips

    @property
    def ip(self):
        """Get first host IP address."""
        if self._ips:
            return self._ips[0]

    @property
    def status(self):
        """Get host status."""
        return self._status

    @property
    def error(self):
        """Get host error object."""
        return self._error

    @property
    def username(self):
        """Get username for connecting to host."""
        return self._username

    @property
    def password(self):
        """Get password for connecting to host."""
        return self._password

    async def delete(self):
        """Issue host deletion via associated provider."""
        await self.provider.delete_host(self.id)
        self._status = STATUS_DELETED
        return True
