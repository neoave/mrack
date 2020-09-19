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

"""Podman provider module."""

import asyncio
import logging
from datetime import datetime, timedelta

from mrack.errors import ProvisioningError, ServerNotFoundError
from mrack.host import STATUS_ACTIVE, STATUS_DELETED, STATUS_ERROR, STATUS_OTHER, Host
from mrack.providers.provider import Provider
from mrack.providers.utils.podman import Podman
from mrack.utils import object2json

logger = logging.getLogger(__name__)

PROVISIONER_KEY = "podman"


class PodmanProvider(Provider):
    """Podman provisioning provider."""

    def __init__(self):
        """Initialize provider."""
        self._name = PROVISIONER_KEY
        self.podman = Podman()

    async def validate_hosts(self, hosts):
        """Validate that host requirements are well specified."""
        return True  # TODO

    async def can_provision(self, hosts):
        """Check that provider has enough resources to provision hosts."""
        return True  # TODO

    async def create_server(self, req):
        """Request and create resource on selected provider."""
        hostname = req["name"]
        logger.info(f"Creating container for host: {hostname}")
        hostname = req["name"]
        image = req["image"]
        network = req.get("network")
        container_id = await self.podman.run(image, hostname, network)
        return container_id

    async def wait_till_provisioned(self, resource):
        """Wait till resource is provisioned."""
        cont_id = resource

        start = datetime.now()
        timeout = 20
        timeout_time = start + timedelta(minutes=timeout)

        while datetime.now() < timeout_time:
            try:
                inspect = await self.podman.inspect(cont_id)
            except ProvisioningError as e:
                logger.error(object2json(e))
                raise ServerNotFoundError(cont_id)
            server = inspect[0]
            running = server["State"]["Running"]
            is_error = server["State"]["Error"]
            # TODO: this should be changed after provider refactoring stops working
            # with OpenStack based constants.
            if running:
                server["status"] = "ACTIVE"
                break
            if is_error:
                server["status"] = "ERROR"
                break

            await asyncio.sleep(1)

        done_time = datetime.now()
        prov_duration = (done_time - start).total_seconds()

        if datetime.now() >= timeout_time:
            logger.warning(
                f"{cont_id} was not provisioned within a timeout of" f" {timeout} mins"
            )
        else:
            logger.info(f"{cont_id} was provisioned in {prov_duration:.1f}s")

        logger.debug(object2json(server))
        return server

    async def delete_host(self, host):
        """Delete provisioned host."""
        uuid = host.id
        deleted = await self.podman.rm(uuid, force=True)
        return deleted

    def get_status(self, state):
        """Read status from inspect State object."""
        if state.get("Running"):
            return STATUS_ACTIVE
        elif state.get("Dead"):
            return STATUS_DELETED
        elif state.get("Error"):
            return STATUS_ERROR
        else:
            return STATUS_OTHER

    def to_host(self, prov_result, username=None):
        """Get needed host information from provisioning result."""
        # prov_results is output of inspect method.

        ip = None
        network_set = prov_result.get("NetworkSettings")
        if network_set:
            ip = network_set.get("IPAddress")

        status = self.get_status(prov_result.get("State"))
        error_obj = None
        if status == STATUS_ERROR:
            error_obj = prov_result.get("State")

        host = Host(
            self,
            prov_result.get("Id"),
            prov_result["Config"]["Hostname"],
            [ip],
            status,
            prov_result,
            username=username,
            error_obj=error_obj,
        )
        return host
