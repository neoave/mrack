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
import random
import socket
from datetime import datetime, timedelta

from mrack.context import global_context
from mrack.errors import ProvisioningError
from mrack.host import STATUS_ACTIVE, STATUS_OTHER, Host
from mrack.utils import (
    get_ssh_options,
    get_username_pass_and_ssh_key,
    object2json,
    ssh_to_host,
)

logger = logging.getLogger(__name__)

STRATEGY_ABORT = "abort"
STRATEGY_RETRY = "retry"
RET_CODE = 0  # index to access return code from _wait_for_ssh
HOST_OBJ = 1  # index to access host object from _wait_for_ssh
ERROR_OBJ = 0  # default index to access host error which caused ProvisioningError
SPECS = 1  # default index to access host specs which caused ProvisioningError


class Provider:
    """General Provider interface."""

    def __init__(self):
        """Initialize provider."""
        self._name = "dummy"
        self.dsp_name = "Dummy"
        self.timeout = 60
        self.max_retry = 1
        self.strategy = STRATEGY_ABORT
        self.status_map = {"OTHER": STATUS_OTHER}

    @property
    def name(self):
        """Get provider name."""
        return self._name

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
        raise NotImplementedError()

    async def can_provision(self, hosts):
        """Check that provider has enough resources to provision hosts."""
        raise NotImplementedError()

    async def utilization(self):
        """Check percentage utilization of given provider."""
        raise NotImplementedError()

    async def create_server(self, req):
        """Request and create resource on selected provider."""
        raise NotImplementedError()

    async def wait_till_provisioned(self, resource):
        """Wait till resource is provisioned."""
        raise NotImplementedError()

    async def prepare_provisioning(self, reqs):
        """Prepare provisioning."""
        raise NotImplementedError()

    async def _wait_for_ssh(self, host, timeout, port):
        """
        Wait until a port starts accepting TCP connections and is able to connect.

        Args:
            host (Host): Host object to get its address on which the port should exist.
            timeout (float): In minutes. How long to wait before raising errors.
            port (int): Port number.
        Raises:
            TimeoutError: The port isn't accepting connection after specified `timeout`.
        """
        log_msg_start = f"{self.dsp_name} [{host.name}]"
        start_time = datetime.now()
        info_msg = (
            f"{log_msg_start} Waiting for the port {port} on host "
            f"{host.ip_addr} to start accepting connections (up to {timeout} minutes)"
        )
        logger.info(info_msg)

        while True:
            try:
                with socket.create_connection(
                    (host.ip_addr, port), timeout=(timeout * 60)
                ):
                    logger.info(
                        f"{log_msg_start} Port {port} on host "
                        f" {host.ip_addr} is now open"
                    )
                    break
            except OSError:
                await asyncio.sleep(10)
                logger.debug(info_msg)
                if datetime.now() - start_time >= timedelta(seconds=(timeout * 60)):
                    logger.error(
                        f"{log_msg_start} Waited too long for the port "
                        f"{port} on host {host.ip_addr} to start accepting connections"
                    )
                    # do not continue to try ssh connection after port is not open
                    return False, host

        # Wait also for the ssh key to be accepted for a half timeout time
        start_ssh = datetime.now()
        # load stuff from configs: like:
        username, password, ssh_key = get_username_pass_and_ssh_key(
            host, global_context
        )

        info_msg = (
            f"{log_msg_start} Waiting for the host {host.ip_addr} "
            f"to accept the authentication method (up to {timeout} minutes)"
        )

        while True:
            ssh_options = get_ssh_options(
                host, global_context.METADATA, global_context.PROV_CONFIG
            )
            res = ssh_to_host(
                host,
                username=username,
                password=password,
                ssh_key=ssh_key,
                command="echo mrack",
                ssh_options=ssh_options,
            )
            duration = (datetime.now() - start_ssh).total_seconds()

            if res:
                logger.info(
                    f"{log_msg_start} SSH to host '{host.ip_addr}' successful "
                    f"after {duration:.1f}s"
                )
                break

            if datetime.now() - start_ssh >= timedelta(seconds=(timeout * 60)):
                logger.error(
                    f"{log_msg_start} SSH to host '{host.ip_addr}' "
                    f"timed out after {duration:.1f}s"
                )
                break

            # wait 10 seconds to retry the ssh connection
            await asyncio.sleep(10)

        return res, host

    async def _check_ssh_auth(self, default_check, active_hosts):
        """Check the ssh authentication functionality."""
        success_hosts = []
        error_hosts = []

        if not isinstance(default_check, dict):
            default_check = {}

        # check if default config is in place, if not use defaults
        req_keys = ("enabled", "port", "timeout")
        if not all(k in default_check for k in req_keys):
            logger.warning(
                f"{self.dsp_name} Missing complete default post provisioning "
                "ssh check configuration in provisioning config file."
            )
            # extend not complete configuration with defaults
            default_check = {
                "enabled": True,
                "port": 22,
                "timeout": 10,
            } | default_check

        # split dictionary into two default and based on host os/group
        req_keys += ("enabled_providers", "disabled_providers")
        based_check = {x: default_check[x] for x in default_check if x not in req_keys}
        default_check = {x: default_check[x] for x in default_check if x in req_keys}

        wait_ssh = []
        for host in active_hosts:
            # go host by host and load the group and os based configuration for ssh
            os_check = based_check.get("os", {}).get(host.operating_system, {})
            group_check = based_check.get("group", {}).get(host.group, {})
            opts = default_check | group_check | os_check  # sorted by priority

            logger.debug(
                f"{self.dsp_name} [{host.name}] "
                f"ssh check config: {object2json(opts)}"
            )

            if (
                not opts.get("enabled")
                and self.name not in opts.get("enabled_providers", [])
            ) or (
                opts.get("enabled") and self.name in opts.get("disabled_providers", [])
            ):
                success_hosts.append(host)
                logger.debug(
                    f"{self.dsp_name} Skipping ssh check for host '{host.name}'"
                )
                continue

            awaitable = self._wait_for_ssh(
                host,
                timeout=opts.get("timeout"),
                port=opts.get("port"),
            )
            wait_ssh.append(awaitable)

        ssh_results = await asyncio.gather(*wait_ssh)
        # We distinguish the success hosts and new error hosts from active by using:
        # res[RET_CODE] 0
        #   - the result of operation returned from self._wait_for_ssh()
        # res[HOST_OBJ] 1
        #   - the host object returned from self._wait_for_ssh()
        for res in ssh_results:
            if res[RET_CODE]:
                success_hosts.append(res[HOST_OBJ])
            else:
                res[HOST_OBJ].error = (
                    "Could not establish ssh connection to host "
                    f"{res[HOST_OBJ].host_id} with IP {res[HOST_OBJ].ip_addr}"
                )
                error_hosts.append(res[HOST_OBJ])

        return success_hosts, error_hosts

    async def _provision_base(
        self,
        reqs,
        timeout=None,
    ):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """Provision hosts based on list of host requirements.

        Main function which does provisioning and validation.
        Parameters:
            reqs - dictionary with requirements for provider
            timeout - base timeout (minutes) to wait for resources
        """
        if not timeout:
            timeout = self.timeout

        log_msg_start = f"{self.dsp_name}"  # use display name at log message beginning
        logger.info(f"{log_msg_start} Validating host(s) definitions")
        if not reqs:
            raise ProvisioningError(
                f"{log_msg_start} Can not continue with empty requirement for provider"
            )

        await self.validate_hosts(reqs)
        logger.info(f"{log_msg_start} Host(s) definitions valid")

        delta = abs(self.timeout - timeout)
        slow_down = random.choice(range(delta, self.timeout + delta))

        logger.debug(
            f"{log_msg_start} Slowing down the execution for {slow_down} s "
            "(This will help mrack to get better resource overview for concurrent runs)"
        )

        await asyncio.sleep(slow_down)
        # This slows down the provisioning at the beginning using a variable time
        # to sleep so we prevent mrack executions to provision at the same time.
        logger.info(
            f"{log_msg_start} Setting timeout to wait "
            f"for resources to {timeout} min(s)"
        )

        logger.info(f"{log_msg_start} Checking available resources")
        res_check_start = datetime.now()
        error_hosts = []

        while not await self.can_provision(reqs):
            if datetime.now() - res_check_start >= timedelta(minutes=timeout):
                # create error host object so retry strategy can continue
                # instead of throwing exception to fail at once without retry
                err_str = "Not enough resources to provision"
                logger.error(f"{log_msg_start} {err_str}")
                for req in reqs:
                    error_hosts.append(
                        Host(
                            provider=self,
                            host_id=req.get("name"),
                            name=req.get("name"),
                            operating_system=req.get("os"),
                            group=req.get("group"),
                            ip_addrs=[],
                            status=STATUS_OTHER,
                            rawdata=req,
                            error_obj=err_str,
                        )
                    )
                return ([], error_hosts, reqs)

            logger.info(
                f"{log_msg_start} Not enough resources to provision, "
                f"checking again in {timeout * 10} seconds(s)"
            )
            # Sleep time to wait to check if resources are available again.
            await asyncio.sleep(timeout * 10)

        logger.info(f"{log_msg_start} Resource availability: OK")
        started = datetime.now()

        logger.info(f"{log_msg_start} Issuing provisioning of {len(reqs)} host(s)")
        create_servers = []
        for req in reqs:
            awaitable = self.create_server(req)
            create_servers.append(awaitable)

        # expect the exception in return data to be parsed later
        create_resps = await asyncio.gather(*create_servers, return_exceptions=True)

        logger.info(f"{log_msg_start} Provisioning issued")

        logger.info(f"{log_msg_start} Waiting for all hosts to be active")

        wait_servers = []
        for response in create_resps:
            if isinstance(response, ProvisioningError):
                # use ProvisioningError arguments to create missing Host object
                # which we append to error hosts list for later usage
                error_hosts.append(
                    Host(
                        provider=self,
                        host_id=response.args[SPECS].get("host_id"),
                        name=response.args[SPECS].get("name"),
                        operating_system=response.args[SPECS].get("os"),
                        group=response.args[SPECS].get("group"),
                        ip_addrs=[],
                        status=STATUS_OTHER,
                        rawdata=response.args,
                        error_obj=response.args[ERROR_OBJ],
                    )
                )
            elif isinstance(response, Exception):
                logger.error("An unexpected exception occurred while provisioning")
                raise response
            else:
                # response might be okay so let us wait for result
                awaitable = self.wait_till_provisioned(response)
                wait_servers.append(awaitable)

        server_results = await asyncio.gather(*wait_servers)
        provisioned = datetime.now()

        logger.info(
            f"{log_msg_start} "
            "All hosts reached provisioning final state (ACTIVE or ERROR)"
        )
        logger.info(f"{log_msg_start} Provisioning duration: {provisioned - started}")

        hosts = [self.to_host(srv, req) for srv, req in server_results if srv]

        error_hosts += await self.parse_error_hosts(hosts)
        active_hosts = [h for h in hosts if h not in error_hosts]
        success_hosts = []

        ssh_check = global_context.PROV_CONFIG.get("post_provisioning_check", {}).get(
            "ssh", True
        )  # enable check by default

        # check ssh connectivity to hosts if not disabled per host or provider
        if bool(ssh_check):
            success_hosts, failed_hosts = await self._check_ssh_auth(
                ssh_check, active_hosts
            )
            error_hosts += failed_hosts
        else:  # we do not check the ssh connection to VMs
            success_hosts = active_hosts

        return (success_hosts, error_hosts, self._get_missing_reqs(reqs, error_hosts))

    async def provision_hosts(self, reqs):
        """Provision hosts based on list of host requirements.

        Main provider method for provisioning.

        Issues provisioning and waits for it succeed. Raises exception if any of
        the servers was not successfully provisioned. If that happens it issues deletion
        of all already provisioned resources.

        Return list of information about provisioned servers.
        """
        log_msg_start = self.dsp_name
        logger.info(f"{log_msg_start} Preparing provider resources")
        if not await self.prepare_provisioning(reqs):
            raise ProvisioningError("Failed to prepare resources", self.dsp_name)

        if self.strategy == STRATEGY_RETRY:
            success_hosts, error_hosts, _missing_reqs = await self.strategy_retry(reqs)
        else:
            success_hosts, error_hosts, _missing_reqs = await self.strategy_abort(reqs)

        if error_hosts:
            hosts_to_delete = success_hosts + error_hosts
            await self.abort_and_delete(hosts_to_delete, error_hosts)

        logger.info(f"{log_msg_start} Printing provisioned hosts")
        for host in success_hosts:
            logger.info(f"{log_msg_start} {host}")

        return success_hosts

    def _get_missing_reqs(self, reqs, error_hosts):
        """Return missing requirements based on reqs and error hosts."""
        return [
            req for req in reqs if req["name"] in [host.name for host in error_hosts]
        ]

    def _get_max_utilization(self):
        """Get max utilization value from context."""
        return global_context.CONFIG.max_utilization

    async def strategy_retry(self, reqs):
        """Provisioning strategy to try multiple times to provision a host."""
        log_msg_start = self.dsp_name
        missing_reqs = reqs
        attempts = 0
        success_hosts = []
        error_hosts = []
        delta_sleep = global_context.CONFIG.delta_sleep
        max_utilization = self._get_max_utilization()

        while missing_reqs:
            # number of attempts should be greater than max_retry
            # and not greater or equal than max_retry because
            # other way first attempt to provision will be
            # considered as first retry and provisioning will end
            # after reaching count 1 without reprovisioning retry
            if attempts > self.max_retry:
                logger.error(
                    f"{log_msg_start} Max retry attempts "
                    f"({self.max_retry}) reached. Aborting"
                )
                break

            attempts += 1

            # set the waiting timeout to vary from 45-75 minutes randomly
            # so if there are multiple parallel runs of mrack they wait
            # different amount time before poll and increase chance to get resources
            # quicker than other concurrent runs of mrack requests
            delta = random.choice(range(-delta_sleep, delta_sleep))
            res_check_timeout = self.timeout + delta

            s_hosts, error_hosts, missing_reqs = await self._provision_base(
                missing_reqs, timeout=res_check_timeout
            )

            success_hosts.extend(s_hosts)

            if s_hosts:
                logger.info(f"{log_msg_start} {len(s_hosts)} host(s) provisioned.")
                succ = f"{len(success_hosts)}/{len(reqs)} host(s) provisioned properly."
                logger.info(f"{log_msg_start} Provisioning progress: {succ}")

            # We need to cleanup the error hosts for the next retry run
            # in case of last attempt which is `self.max_retry`
            # we skip this part at it done in provision_hosts() method while
            # awaiting the self.abort_and_delete(error hosts)

            if error_hosts and attempts <= self.max_retry:
                count = len(error_hosts)
                err = f"{count} host(s) NOT provisioned properly, deleting."
                logger.info(f"{log_msg_start} {err}")
                server_error = False
                for host in error_hosts:
                    logger.error(f"{log_msg_start} Error: {str(host.error)}")
                    # if host.error is a dictionary and code is 500 = SERVER ERROR
                    if (
                        isinstance(host.error, dict)
                        and host.error.get("code", None) == 500
                        and not server_error  # add condition here to not repeat message
                    ):
                        logger.info(
                            f"{log_msg_start} Provider returned server error (500), "
                            "increasing cooldown time before another retry"
                        )
                        server_error = True

                error_hosts_share = (
                    len(error_hosts) / len(success_hosts + error_hosts) * 100
                )
                high_utilization = await self.utilization() >= max_utilization

                if high_utilization or (error_hosts_share > max_utilization):
                    # delete all hosts when there is high utilization of provider
                    # or error hosts share is exceeding the same utilization threshold
                    error_hosts += success_hosts
                    missing_reqs = self._get_missing_reqs(reqs, error_hosts)
                    success_hosts = []

                await self.delete_hosts(error_hosts)

                # increase the sleep time to extend the cooldown period
                # when internal error happens
                res_check_timeout += res_check_timeout * int(server_error)

                cooldown = random.choice(
                    range(res_check_timeout, 2 * res_check_timeout)
                )

                logger.info(
                    f"{log_msg_start} Retrying to provision these hosts in {cooldown}s"
                )
                # In this case we haven't been able to provision all resources
                # despite the previous waits, so we probably are in a race condition
                # with concurrent runs, and thus we free all resources and try again
                # in `cooldown` seconds to give chance other mrack requests.
                await asyncio.sleep(cooldown)

        return success_hosts, error_hosts, missing_reqs

    async def strategy_abort(self, reqs):
        """Provisioning strategy to try once and then abort."""
        return await self._provision_base(reqs)

    async def parse_error_hosts(self, hosts):
        """Parse provisioning errors from provider result."""
        log_msg_start = self.dsp_name
        errors = []
        logger.debug(f"{log_msg_start} Checking provisioned hosts for errors")
        for host in hosts:
            logger.debug(
                f"{log_msg_start} [{host.name}] ID {host.host_id}"
                f"\tSTATUS - {host.status}"
            )

            if host.status != STATUS_ACTIVE:
                errors.append(host)

        return errors

    async def abort_and_delete(self, hosts_to_delete, error_hosts):
        """Delete hosts and abort provisioning with an error."""
        log_msg_start = self.dsp_name
        logger.info(f"{log_msg_start} Aborting provisioning due to error.")
        for host in error_hosts:
            logger.error(f"{log_msg_start} [{host.name}] Error: {str(host.error)}")

        logger.info(f"{log_msg_start} Given the error, will delete hosts")
        await self.delete_hosts(hosts_to_delete)
        raise ProvisioningError(
            f"{log_msg_start} Failed to provision {len(error_hosts)} host(s) "
            "due to provisioning error",
            self.dsp_name,
        )

    async def delete_host(self, host_id, host_name):
        """Delete provisioned host."""
        raise NotImplementedError()

    async def delete_hosts(self, hosts):
        """Issue deletion of all servers based on previous results from provisioning."""
        log_msg_start = self.dsp_name
        logger.info(f"{log_msg_start} Issuing deletion")
        delete_servers = []
        for host in hosts:
            awaitable = self.delete_host(host.host_id, host.name)
            delete_servers.append(awaitable)
        results = await asyncio.gather(*delete_servers)
        logger.info(f"{log_msg_start} All servers issued to be deleted")
        return results

    def prov_result_to_host_data(self, prov_result, req):
        """Transform provisioning result to needed host data."""
        raise NotImplementedError()

    def to_host(self, provisioning_result, req, username=None):
        """Transform provisioning result into Host object."""
        host_info = self.prov_result_to_host_data(provisioning_result, req)

        host = Host(
            self,
            host_info.get("id"),
            host_info.get("name"),
            host_info.get("os"),
            host_info.get("group"),
            host_info.get("addresses"),
            self.status_map.get(host_info.get("status"), STATUS_OTHER),
            provisioning_result,
            username=username,
            password=host_info.get("password"),
            error_obj=host_info.get("fault"),
            meta_extra=host_info.get("meta_extra"),
        )
        return host
