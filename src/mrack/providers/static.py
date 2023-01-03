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

import logging
from copy import deepcopy

from mrack.errors import ValidationError
from mrack.host import STATUS_ACTIVE
from mrack.providers.provider import STRATEGY_ABORT, Provider

PROVISIONER_KEY = "static"

logger = logging.getLogger(__name__)


class StaticProvider(Provider):
    """
    Static Provider.

    Doesn't provision anything. Only simulates provisioning so that
    we can track the server in output modules and other actions.
    """

    def __init__(self):
        """Object initialization."""
        super().__init__()
        self._name = PROVISIONER_KEY
        self.dsp_name = "Static"
        self.max_retry = 1  # for retry strategy
        self.strategy = STRATEGY_ABORT
        self.status_map = {STATUS_ACTIVE: STATUS_ACTIVE}

    async def prepare_provisioning(self, reqs):
        """Prepare provisioning."""
        return bool(reqs)

    async def create_server(self, req):
        """Request and create resource on selected provider."""
        # we shall return same tuple as with other providers
        return (req, deepcopy(req))

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
        for req in reqs:
            if "name" not in req:
                raise ValidationError("Name not found")
            if "ip" not in req:
                raise ValidationError("IP address (ip) not found")
        return bool(reqs)

    async def can_provision(self, hosts):
        """Behave as that we can."""
        return True

    async def utilization(self):
        """Check percentage utilization of given provider."""
        return 0

    async def provision_hosts(self, reqs):
        """Fake provision - behave as if it was provisioned."""
        await self.validate_hosts(reqs)
        hosts = [self.to_host(req, req) for req in reqs]
        return hosts

    async def wait_till_provisioned(self, resource):
        """Wait till resource is provisioned."""
        return resource

    def prov_result_to_host_data(self, prov_result, req):
        """Transform provisioning result to needed host data."""
        result = {}

        result["id"] = prov_result.get("name")
        result["name"] = req.get("name")
        result["addresses"] = [prov_result.get("ip")]
        result["fault"] = {}
        result["status"] = STATUS_ACTIVE
        result["os"] = prov_result.get("os")  # with static it stays os
        result["group"] = prov_result.get("group")  # with static it stays os

        return result

    async def delete_host(self, host_id, host_name):
        """Fake delete - pass but don't do anything."""
        log_msg_start = f"{self.dsp_name} [{host_name}]"
        logger.info(
            f"{log_msg_start} Host with ID {host_id} is static"
            " - not managed by mrack, ignoring removal"
        )
        return bool(host_id)
