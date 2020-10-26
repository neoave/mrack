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

"""General Provider interface."""
import asyncio
import logging
from datetime import datetime

from mrack.errors import ProvisioningError, ValidationError
from mrack.host import STATUS_ERROR, STATUS_OTHER, Host

logger = logging.getLogger(__name__)


class Provider:
    """General Provider interface."""

    def __init__(self, provisioning_config, job_config):
        """Initialize provider."""
        self._name = "dummy"
        self.STATUS_MAP = {"OTHER": STATUS_OTHER}
        return

    @property
    def name(self):
        """Get provider name."""
        return self._name

    async def validate_hosts(self, hosts):
        """Validate that host requirements are well specified."""
        raise NotImplementedError()

    async def can_provision(self, hosts):
        """Check that provider has enough resources to provison hosts."""
        raise NotImplementedError()

    async def create_server(self, req):
        """Request and create resource on selected provider."""
        raise NotImplementedError()

    async def wait_till_provisioned(self, resource):
        """Wait till resource is provisioned."""
        raise NotImplementedError()

    async def provision_hosts(self, hosts):
        """Provision hosts based on list of host requirements.

        Main provider method for provisioning.

        First it validates that host requirements are valid and that
        provider has enough resources(quota).

        Then issues provisioning and waits for it succeed. Raises exception if any of
        the servers was not successfully provisioned. If that happens it issues deletion
        of all already provisioned resources.

        Return list of information about provisioned servers.
        """
        logger.info("Validating hosts definitions")
        await self.validate_hosts(hosts)
        logger.info("Host definitions valid")

        logger.info("Checking available resources")
        can = await self.can_provision(hosts)
        if not can:
            raise ValidationError("Not enough resources to provision")
        logger.info("Resource availability: OK")

        started = datetime.now()

        count = len(hosts)
        logger.info(f"Issuing provisioning of {count} hosts")
        create_servers = []
        for req in hosts:
            awaitable = self.create_server(req)
            create_servers.append(awaitable)
        create_resps = await asyncio.gather(*create_servers)
        logger.info("Provisioning issued")

        logger.info("Waiting for all hosts to be available")
        wait_servers = []
        for create_resp in create_resps:
            awaitable = self.wait_till_provisioned(create_resp)
            wait_servers.append(awaitable)

        server_results = await asyncio.gather(*wait_servers)
        provisioned = datetime.now()
        provi_duration = provisioned - started

        logger.info("All hosts reached provisioning final state (ACTIVE or ERROR)")
        logger.info(f"Provisioning duration: {provi_duration}")

        hosts = [self.to_host(srv) for srv in server_results]
        errors = self.parse_errors(hosts)

        if errors:
            logger.info("Some host did not start properly")
            for host_err in errors:
                logger.error(f"Error: {str(host_err)}")

            logger.info("Given the error, will delete all hosts")
            await self.delete_hosts(hosts)
            raise ProvisioningError(errors)

        logger.info("Printing provisioned hosts")
        for host in hosts:
            logger.info(host)

        return hosts

    def parse_errors(self, hosts):
        """Parse provisioning errors from provider result."""
        errors = []
        for host in hosts:
            logger.info(f"Host: {host.id}\tStatus: {host.status}")
            if self.STATUS_MAP.get(host.status, STATUS_OTHER) == STATUS_ERROR:
                errors.append(host.error)

        return errors

    async def delete_host(self, host_id):
        """Delete provisioned host."""
        raise NotImplementedError()

    async def delete_hosts(self, hosts):
        """Issue deletion of all servers based on previous results from provisioning."""
        logger.info("Issuing deletion")

        delete_servers = []
        for host in hosts:
            awaitable = self.delete_host(host.id)
            delete_servers.append(awaitable)
        results = await asyncio.gather(*delete_servers)
        logger.info("All servers issued to be deleted")
        return results

    def prov_result_to_host_data(self, prov_result):
        """Transform provisioning result to needed host data."""
        raise NotImplementedError()

    def to_host(self, provisioning_result, username=None):
        """Transform provisioning result into Host object."""
        host_info = self.prov_result_to_host_data(provisioning_result)

        host = Host(
            self,
            host_info.get("id"),
            host_info.get("name"),
            host_info.get("addresses"),
            self.STATUS_MAP.get(host_info.get("status"), STATUS_OTHER),
            provisioning_result,
            username=username,
            error_obj=host_info.get("fault"),
        )
        return host
