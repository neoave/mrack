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

"""Static provider."""

from mrack.errors import ValidationError
from mrack.host import STATUS_ACTIVE, Host
from mrack.providers.provider import STRATEGY_ABORT, Provider

PROVISIONER_KEY = "static"


class StaticProvider(Provider):
    """
    Static Provider.

    Doesn't provision anything. Only simulates provisioning so that
    we can track the server in output modules and other actions.
    """

    def __init__(self):
        """Object initialization."""
        self._name = PROVISIONER_KEY
        self.strategy = STRATEGY_ABORT

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
        for req in reqs:
            if "name" not in req:
                raise ValidationError("Name not found")
            if "ip" not in req:
                raise ValidationError("IP address (ip) not found")
        return True

    async def can_provision(self, hosts):
        """Behave as that we can."""
        return True

    async def provision_hosts(self, reqs):
        """Fake provision - behave as if it was provisioned."""
        await self.validate_hosts(reqs)
        hosts = [self.to_host(req) for req in reqs]
        return hosts

    async def delete_host(self, host):
        """Fake delete - pass but don't do anything."""
        return True

    def to_host(self, req):
        """Transform req into Host object."""
        host = Host(
            self,
            req.get("name"),
            req.get("name"),
            [req.get("ip")],
            STATUS_ACTIVE,
            req,
            error_obj={},
        )
        return host
