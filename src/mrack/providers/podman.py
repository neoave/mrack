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
import os
from datetime import datetime, timedelta

from mrack.errors import ProvisioningError, ServerNotFoundError
from mrack.host import STATUS_ACTIVE, STATUS_DELETED, STATUS_ERROR, STATUS_OTHER
from mrack.providers.provider import STRATEGY_ABORT, Provider
from mrack.providers.utils.podman import Podman
from mrack.utils import object2json

logger = logging.getLogger(__name__)

PROVISIONER_KEY = "podman"


class PodmanProvider(Provider):
    """Podman provisioning provider."""

    def __init__(self):
        """Initialize provider."""
        self._name = PROVISIONER_KEY
        self.dsp_name = "Podman"
        self.strategy = STRATEGY_ABORT
        self.podman = Podman()
        self.status_map = {
            STATUS_ACTIVE: STATUS_ACTIVE,
            STATUS_DELETED: STATUS_DELETED,
            STATUS_ERROR: STATUS_ERROR,
        }

    async def init(self, container_images, default_network, ssh_key, container_options):
        """Initialize Podman provider with data from config."""
        logger.info(f"{self.dsp_name}: Initializing provider")
        login_start = datetime.now()
        self.images = container_images
        self.default_network = default_network
        self.ssh_key = ssh_key
        self.podman_options = container_options
        login_end = datetime.now()
        login_duration = login_end - login_start
        logger.info(f"{self.dsp_name}: Init duration {login_duration}")

    async def prepare_provisioning(self, reqs):
        """Prepare provisioning."""
        pass

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
        return bool(reqs)  # TODO

    async def can_provision(self, hosts):
        """Check that provider has enough resources to provision hosts."""
        return bool(hosts)  # TODO

    async def create_server(self, req):
        """Request and create resource on selected provider."""
        hostname = req["name"]
        logger.info(f"{self.dsp_name}: Creating container for host: {hostname}")

        image = req["image"]
        network = req.get("network", self.default_network)
        await self.podman.network_create(network)

        if not await self.podman.image_exists(image):
            logger.info(f"{self.dsp_name}: Pulling image {image}")
            if not await self.podman.pull(image):
                logger.error(f"{self.dsp_name}: Image {image} failed to pull")
        else:
            logger.info(f"{self.dsp_name}: Image {image} present")

        container_id = await self.podman.run(
            image,
            hostname,
            network,
            extra_options=self.podman_options,
            remove_at_stop=True,
        )
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
            except ProvisioningError as err:
                logger.error(f"{self.dsp_name}: {object2json(err)}")
                raise ServerNotFoundError(cont_id) from err
            server = inspect[0]
            running = server["State"]["Running"]
            is_error = server["State"]["Error"]
            if running or is_error:
                break
            await asyncio.sleep(1)

        done_time = datetime.now()
        prov_duration = (done_time - start).total_seconds()

        if datetime.now() >= timeout_time:
            logger.warning(
                f"{self.dsp_name}: {cont_id} was not provisioned within a timeout of"
                f" {timeout} mins"
            )
        else:
            logger.info(
                f"{self.dsp_name}: {cont_id} was provisioned in {prov_duration:.1f}s"
            )

        logger.debug(f"{self.dsp_name}: Resource: {object2json(server)}")

        with open(os.path.expanduser(self.ssh_key), "r") as key_file:
            key_content = key_file.read()

        if not await self.podman.exec_command(cont_id, "mkdir -p /root/.ssh/"):
            raise ProvisioningError(f"Could not copy public key to container {cont_id}")

        if not await self.podman.exec_command(
            cont_id, f'echo "{key_content}" >> /root/.ssh/authorized_keys'
        ):
            raise ProvisioningError(f"Could not copy public key to container {cont_id}")

        if not await self.podman.exec_command(cont_id, "systemctl restart sshd"):
            raise ProvisioningError(
                f"Failed restarting sshd service in container {cont_id}"
            )

        return server

    async def delete_host(self, host_id):
        """Delete provisioned host."""
        # first we inspect the container to find its networks
        insp_data = await self.podman.inspect(host_id)
        networks = insp_data[0]["NetworkSettings"]["Networks"]
        # then we destroy the container
        deleted = await self.podman.rm(host_id, force=True)  # TODO use stop and then rm
        # after that we cleanup the network
        for net in networks:
            if await self.podman.network_remove(net):
                logger.info(f"{self.dsp_name}: Removed network '{net}'")

        return deleted

    def get_status(self, state):
        """Read status from inspect State object."""
        if state.get("Running"):
            status = STATUS_ACTIVE
        elif state.get("Dead"):
            status = STATUS_DELETED
        elif state.get("Error"):
            status = STATUS_ERROR
        else:
            status = STATUS_OTHER

        return status

    def prov_result_to_host_data(self, prov_result):
        """Get needed host information from podman provisioning result."""
        result = {}

        result["id"] = prov_result.get("Id")
        result["name"] = prov_result["Config"]["Hostname"]

        network_set = prov_result.get("NetworkSettings")

        result["addresses"] = []
        if network_set:
            try:  # TODO self.network_name
                for net in network_set["Networks"]:
                    result["addresses"].append(
                        network_set["Networks"][net]["IPAddress"]
                    )
            except KeyError as kerror:
                raise ProvisioningError(
                    f"{self.dsp_name}: Container state improper"
                ) from kerror

        status = self.get_status(prov_result.get("State"))
        error_obj = None
        if status == STATUS_ERROR:
            error_obj = prov_result.get("State")

        result["fault"] = error_obj
        result["status"] = status

        return result
