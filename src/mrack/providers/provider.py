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

STRATEGY_ABORT = "abort"
STRATEGY_RETRY = "retry"


class Provider:
    """General Provider interface."""

    def __init__(self, provisioning_config, job_config):
        """Initialize provider."""
        self._name = "dummy"
        self.dsp_name = "Dummy"
        self.strategy = STRATEGY_ABORT
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

    async def _provision_base(self, reqs):
        """Provision hosts based on list of host requirements.

        Main function which does provisioning and not any validation.
        """
        logger.info(f"{self.dsp_name}: Host definitions valid")

        logger.info(f"{self.dsp_name}: Checking available resources")
        can = await self.can_provision(reqs)
        if not can:
            raise ValidationError(f"{self.dsp_name}: Not enough resources to provision")
        logger.info(f"{self.dsp_name}: Resource availability: OK")
        started = datetime.now()
        count = len(reqs)
        logger.info(f"{self.dsp_name}: Issuing provisioning of {count} hosts")
        create_servers = []
        for req in reqs:
            awaitable = self.create_server(req)
            create_servers.append(awaitable)
        create_resps = await asyncio.gather(*create_servers)
        logger.info(f"{self.dsp_name}: Provisioning issued")

        logger.info(f"{self.dsp_name}: Waiting for all hosts to be available")
        wait_servers = []
        for create_resp in create_resps:
            awaitable = self.wait_till_provisioned(create_resp)
            wait_servers.append(awaitable)

        server_results = await asyncio.gather(*wait_servers)
        provisioned = datetime.now()
        provi_duration = provisioned - started

        logger.info(
            f"{self.dsp_name}: "
            "All hosts reached provisioning final state (ACTIVE or ERROR)"
        )
        logger.info(f"{self.dsp_name}: Provisioning duration: {provi_duration}")

        hosts = [self.to_host(srv) for srv in server_results]
        error_hosts = self.parse_error_hosts(hosts)
        success_hosts = [h for h in hosts if h not in error_hosts]
        error_host_names = [host.name for host in error_hosts]
        missing_reqs = [req for req in reqs if req["name"] in error_host_names]
        return (success_hosts, error_hosts, missing_reqs)

    async def provision_hosts(self, reqs):
        """Provision hosts based on list of host requirements.

        Main provider method for provisioning.

        First it validates that host requirements are valid and that
        provider has enough resources(quota).

        Then issues provisioning and waits for it succeed. Raises exception if any of
        the servers was not successfully provisioned. If that happens it issues deletion
        of all already provisioned resources.

        Return list of information about provisioned servers.
        """
        logger.info(f"{self.dsp_name}: Validating hosts definitions")
        await self.validate_hosts(reqs)

        if self.strategy == STRATEGY_RETRY:
            success_hosts, error_hosts, missing_reqs = await self.strategy_retry(reqs)
        else:
            success_hosts, error_hosts, missing_reqs = await self.strategy_abort(reqs)

        if error_hosts:
            hosts_to_delete = success_hosts + error_hosts
            self.abort_and_delete(hosts_to_delete, error_hosts)

        logger.info(f"{self.dsp_name}: Printing provisioned hosts")
        for host in success_hosts:
            logger.info(f"{self.dsp_name}: {host}")

        return success_hosts

    async def strategy_retry(self, reqs):
        """Provisioning strategy to try multiple times to provision a host."""
        missing_reqs = reqs
        attempts = 0
        success_hosts = []
        error_hosts = []

        while missing_reqs:
            if attempts >= self.max_attempts:
                logger.error(f"Max attempts({self.max_attempts}) reached. Aborting.")
                break

            attempts += 1
            s_hosts, error_hosts, missing_reqs = await self._provision_base(
                missing_reqs
            )
            success_hosts.extend(s_hosts)

            if error_hosts:
                count = len(error_hosts)
                err = f"{count} hosts were not provisioned properly, deleting."
                logger.info(f"{self.dsp_name}: {err}")
                for host in error_hosts:
                    logger.error(f"{self.dsp_name}: Error: {str(host.error)}")
                await self.delete_hosts(error_hosts)
                logger.info("Retrying to provision these hosts.")

        return success_hosts, error_hosts, missing_reqs

    async def strategy_abort(self, reqs):
        """Provisioning strategy to try once and then abort."""
        return await self._provision_base(reqs)

    def parse_error_hosts(self, hosts):
        """Parse provisioning errors from provider result."""
        errors = []
        logger.debug(f"{self.dsp_name}: Checking provisioned hosts for errors")
        for host in hosts:
            logger.debug(f"{self.dsp_name}: Host - {host.id}\tStatus - {host.status}")
            if host.status == STATUS_ERROR:
                errors.append(host)
        return errors

    async def abort_and_delete(self, hosts_to_delete, error_hosts):
        """Delete hosts and abort provisioning with an error."""
        logger.info(f"{self.dsp_name}: Aborting provisioning due to error.")
        for host in error_hosts:
            logger.error(f"{self.dsp_name}: Error: {str(host.error)}")

        logger.info(f"{self.dsp_name}: Given the error, will delete hosts")
        await self.delete_hosts(hosts_to_delete)
        raise ProvisioningError(error_hosts)

    async def delete_host(self, host_id):
        """Delete provisioned host."""
        raise NotImplementedError()

    async def delete_hosts(self, hosts):
        """Issue deletion of all servers based on previous results from provisioning."""
        logger.info(f"{self.dsp_name}: Issuing deletion")

        delete_servers = []
        for host in hosts:
            awaitable = self.delete_host(host.id)
            delete_servers.append(awaitable)
        results = await asyncio.gather(*delete_servers)
        logger.info(f"{self.dsp_name}: All servers issued to be deleted")
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
