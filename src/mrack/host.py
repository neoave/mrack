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
        host_data["host_id"],
        host_data["name"],
        host_data["operating_system"],
        host_data["group"],
        host_data["ip_addrs"],
        host_data["status"],
        host_data["rawdata"],
        host_data["username"],
        host_data["password"],
        host_data["error"],
        host_data.get("meta_extra"),
    )
    return host


class Host:
    """Provisioned host.

    Normalized values from providers to offer consistent interface.
    """

    def __init__(
        self,
        provider,
        host_id,
        name,
        operating_system,
        group,
        ip_addrs,
        status,
        rawdata,
        username=None,
        password=None,
        error_obj=None,
        meta_extra=None,
    ):
        """Initialize host object."""
        self._provider = provider
        self._host_id = host_id
        self._name = name
        self._operating_system = operating_system
        self._group = group
        self._ip_addrs = ip_addrs
        self._status = status
        self._username = username
        self._password = password
        self._rawdata = rawdata
        self._error = error_obj
        self._meta_extra = meta_extra

    def __str__(self):
        """Return string representation of host."""
        net_str = " ".join(self._ip_addrs)

        out = (
            f"{self._status} {self._operating_system} {self._host_id} {self._name} "
            f"{net_str} {self._username} {self._password}"
        )

        if self._error:
            out = "\n".join(
                [
                    out,
                    f"Error: Host finished with error(s): {object2json(self._error)}",
                ]
            )
        return out

    def to_json(self):
        """Transform object into representation which is acceptable by `json.dump`."""
        return {
            "provider": self._provider.name,
            "host_id": self._host_id,
            "name": self._name,
            "operating_system": self._operating_system,
            "group": self._group,
            "ip_addrs": self._ip_addrs,
            "status": self._status,
            "username": self._username,
            "password": self._password,
            "rawdata": self._rawdata,
            "error": self._error,
            "meta_extra": self._meta_extra,
        }

    @property
    def provider(self):
        """Get host provisioning provider."""
        return self._provider

    @property
    def operating_system(self):
        """Get host operating system."""
        return self._operating_system

    @property
    def group(self):
        """Get host group."""
        return self._group

    @property
    def host_id(self):
        """Get provider host id."""
        return self._host_id

    @property
    def name(self):
        """Get host name."""
        return self._name

    @property
    def ip_addrs(self):
        """Get host IP addresses."""
        return self._ip_addrs

    @property
    def ip_addr(self):
        """Get first host IP address."""
        return self._ip_addrs[0] if self._ip_addrs else ""

    @property
    def status(self):
        """Get host status."""
        return self._status

    @property
    def error(self):
        """Get host error object."""
        return self._error

    @error.setter
    def error(self, value):
        """Set host error object."""
        self._error = value

    @property
    def username(self):
        """Get username for connecting to host."""
        return self._username

    @property
    def password(self):
        """Get password for connecting to host."""
        return self._password

    @property
    def meta_extra(self):
        """Get host extra meta information."""
        return self._meta_extra

    async def delete(self):
        """Issue host deletion via associated provider."""
        await self.provider.delete_host(self.host_id, self.name)
        self._status = STATUS_DELETED
        return True
