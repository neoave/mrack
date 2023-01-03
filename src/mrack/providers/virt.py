# Copyright 2021 Red Hat Inc.
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

"""Virt provider."""

import asyncio
import getpass
import grp
import logging
import os
from datetime import datetime

from testcloud.exceptions import TestcloudImageError

from mrack.errors import ProvisioningError, ValidationError
from mrack.host import STATUS_ACTIVE, STATUS_OTHER, STATUS_PENDING
from mrack.providers.provider import STRATEGY_ABORT, Provider
from mrack.providers.utils.testcloud import Testcloud
from mrack.utils import is_windows_host

logger = logging.getLogger(__name__)

PROVISIONER_KEY = "virt"


class VirtProvider(Provider):
    """Virt provisioning provider."""

    def __init__(self):
        """Initialize provider."""
        super().__init__()
        self._name = PROVISIONER_KEY
        self.dsp_name = "Virt"
        self.testcloud = Testcloud()
        self.max_retry = 1  # for retry strategy
        self.status_map = {
            "running": STATUS_ACTIVE,
            "shutoff": STATUS_OTHER,
            "undefined": STATUS_OTHER,
            "de-sync": STATUS_PENDING,
        }

    def _extract_err_msg(self, virt_err):
        """Extract Virt provider traceback error from message."""
        # split traceback string to find Error causing failure
        # index 1 should point to the Error string
        exc_str = "\n".join([f"\t{s}" for s in str(virt_err).splitlines()])
        logger.debug(f"{self.dsp_name} Exception occured:\n{exc_str}")
        err_sep = "Error:"
        if err_sep in exc_str:
            err_str = str(virt_err).split(err_sep)[1].strip()
        elif err_sep.upper() in exc_str:
            err_str = str(virt_err).split(err_sep.upper())[1].strip()
        else:
            err_str = exc_str
        # return first line of error as it could be more lines of traceback
        return err_str.split("\n")[0]

    async def init(self, strategy=STRATEGY_ABORT, max_retry=1):
        """Initialize Virt provider with data from config."""
        logger.info(f"{self.dsp_name} Initializing provider")
        login_start = datetime.now()
        self.strategy = strategy
        self.max_retry = max_retry
        login_end = datetime.now()
        login_duration = login_end - login_start
        logger.info(f"{self.dsp_name} Init duration {login_duration}")

    async def prepare_provisioning(self, reqs):
        """Prepare provisioning."""
        # Check that current user belongs to testcloud group
        group = "testcloud"
        uname = getpass.getuser()
        _name, _pass, gid, _members = grp.getgrnam(group)
        groups = os.getgroups()
        if gid not in groups:
            raise ValidationError(
                f"Error: Current user is not a member of a {group} group.\n"
                "Make sure that testcloud is installed and add the user to the "
                "group, e.g. by:\n"
                f"  sudo usermod -a -G {group} {uname}"
            )

        # Pulling images ahead so that the provider doesn't download the same
        # image more than once
        pull = set()
        for req in reqs:
            pull.add(req["image_url"])

        awaitables = []
        for url in pull:
            logger.info(f"{self.dsp_name} Pulling image '{url}'")
            awaitables.append(self.testcloud.pull_image(url))

        pull_results = await asyncio.gather(*awaitables, return_exceptions=True)
        success = all(pull_results)

        for pull in pull_results:
            if isinstance(pull, TestcloudImageError):
                logger.error(f"{self.dsp_name} {str(pull)}")
                success = False
            elif isinstance(pull, Exception):
                raise pull

        if not success:
            logger.error(f"{self.dsp_name} Pulling of images failed")
        else:
            logger.info(f"{self.dsp_name} Images prepared")

        return success

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
        return bool(reqs)  # no specific validation yet

    async def can_provision(self, hosts):
        """Check that provider has enough resources to provision hosts."""
        # We'd need to check available memory, this is TODO
        return bool(hosts)

    async def utilization(self):
        """Check percentage utilization of given provider."""
        return 0

    async def create_server(self, req):
        """Request and create resource on Virt provider."""
        hostname = req.get("name")
        logger.info(f"{self.dsp_name} [{hostname}] Creating virtual machine")

        host_id = req["run_id"] + "-" + hostname
        try:
            out, err, _proc = await self.testcloud.create(
                host_id,
                **req,
            )
        except ProvisioningError as virt_err:
            req.update({"host_id": host_id})
            raise ProvisioningError(self._extract_err_msg(virt_err), req) from virt_err

        info = self.testcloud.info(host_id)
        info["id"] = host_id
        info["name"] = hostname
        info["output"] = out
        if info["state"] != "running":
            info["error"] = err

        if is_windows_host(req):
            # testcloud can inject default password for the linux instances only so far
            del info["password"]

        return (info, req)

    async def wait_till_provisioned(self, resource):
        """Wait till resource is provisioned."""
        result, req = resource
        result.update({"mrack_req": req})
        return result, req

    async def delete_host(self, host_id, host_name):
        """Delete provisioned host."""
        log_msg_start = f"{self.dsp_name} [{host_name}]"
        logger.info(f"{log_msg_start} Removing VM {host_id}")
        try:
            _out, _err, _proc = await self.testcloud.destroy(host_id)
        except ProvisioningError as p_err:
            # just log error message when unable to delete VM
            logger.error(f"{log_msg_start} {self._extract_err_msg(p_err)}")

        return True

    def prov_result_to_host_data(self, prov_result, req):
        """Get needed host information from podman provisioning result."""
        result = {}
        result["id"] = prov_result.get("id")
        result["name"] = prov_result.get("name")
        result["addresses"] = [prov_result.get("ip")]
        result["status"] = prov_result["state"]
        result["fault"] = prov_result.get("error")
        result["password"] = prov_result.get("password")
        result["os"] = prov_result.get("mrack_req").get("os")
        result["group"] = prov_result.get("mrack_req").get("group")

        return result
