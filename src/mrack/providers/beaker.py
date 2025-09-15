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

"""Beaker Provider interface."""

import asyncio
import logging
import os
import socket
import xml.etree.ElementTree as eTree
from copy import deepcopy
from datetime import datetime, timedelta
from xml.dom.minidom import Document as xml_doc
from xmlrpc.client import Fault

from bkr.client import BeakerJob, BeakerRecipe, BeakerRecipeSet
from bkr.common.hub import HubProxy
from bkr.common.pyconfig import PyConfigParser
from gssapi.exceptions import MissingCredentialsError
from gssapi.raw.misc import GSSError

from mrack.errors import NotAuthenticatedError, ProvisioningError, ValidationError
from mrack.host import (
    STATUS_ACTIVE,
    STATUS_DELETED,
    STATUS_ERROR,
    STATUS_OTHER,
    STATUS_PROVISIONING,
)
from mrack.providers.provider import STRATEGY_ABORT, Provider
from mrack.utils import add_dict_to_node

logger = logging.getLogger(__name__)

PROVISIONER_KEY = "beaker"


def parse_bkr_exc_str(exc_str):
    """Parse exception string and return response dictionary for mrack error."""
    # we expect exception string to look like following:
    # '<class \'bkr.common.bexceptions.BX\'>:No distro tree matches Recipe:
    # <distroRequires>
    #   <and>
    #     <distro_name op="like" value="Fedora-33%"/>
    #   </and>
    # </distroRequires>'
    if (
        ":" not in exc_str.faultString
        and "bkr.common.bexceptions" not in exc_str.faultString
    ):
        # we got string we do not expect so just use the traceback
        return {"response": str(exc_str)}

    # because of expected format we split by ":" and use last 2 values from list
    # in above example it would be
    # [
    #   '\tNo distro tree matches Recipe',
    #   '\t<distroRequires><and><distro_name op="like" value="Fedora-33%"/> ...
    # ]
    fault = [f"\t{f.strip()}" for f in exc_str.faultString.split(":")[-2:]]
    return {"response": "\n".join(fault)}


class BeakerProvider(Provider):
    """Beaker Provider."""

    def __init__(self):
        """Object initialization."""
        super().__init__()
        self._name = PROVISIONER_KEY
        self.dsp_name = "Beaker"
        self.conf = PyConfigParser()
        self.poll_sleep = 45  # seconds
        self.max_retry = 1  # for retry strategy
        self.status_map = {
            "Reserved": STATUS_ACTIVE,
            "New": STATUS_PROVISIONING,
            "Scheduled": STATUS_PROVISIONING,
            "Queued": STATUS_PROVISIONING,
            "Processed": STATUS_PROVISIONING,
            "Waiting": STATUS_PROVISIONING,
            "Installing": STATUS_PROVISIONING,
            "Running": STATUS_PROVISIONING,
            "Cancelled": STATUS_DELETED,
            "Aborted": STATUS_ERROR,
            "Completed": STATUS_OTHER,
            "MRACK_REACHED_TIMEOUT": STATUS_ERROR,
            "MRACK_RESULT_NOT_PASSED": STATUS_ERROR,
        }

    async def init(
        self,
        distros,
        timeout,
        reserve_duration,
        strategy=STRATEGY_ABORT,
        max_retry=1,
    ):
        """Initialize provider with data from Beaker configuration."""
        logger.info(f"{self.dsp_name} Initializing provider")
        self.strategy = strategy
        self.max_retry = max_retry
        self.distros = distros
        self.timeout = timeout
        self.reserve_duration = reserve_duration
        self.hub = None

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
        for req in reqs:
            req_dstr = req.get("distro")
            if not req.get("meta_distro") and req_dstr not in self.distros:
                raise ValidationError(
                    f"{self.dsp_name} provider does not support "
                    f"'{req_dstr}' distro in provisioning config",
                    self.dsp_name,
                )
        return

    async def prepare_provisioning(self, reqs):
        """Prepare provisioning."""
        return bool(reqs)

    async def can_provision(self, hosts):
        """Check that hosts can be provisioned."""
        return True

    async def utilization(self):
        """Check percentage utilization of given provider."""
        return 0

    def _translate_constraint(self, host_requires, host_recipe):
        """Transform host requires dict to xml."""
        for operand, operand_value in host_requires.items():
            if operand.startswith("_"):
                host_recipe.setAttribute(
                    operand[1:],
                    operand_value,
                )
                continue
            if operand not in ["and", "or"]:
                req_node = xml_doc().createElement(operand)
                req_node = add_dict_to_node(req_node, operand_value)
                host_recipe.appendChild(req_node)
                continue
            # known operands are ["and", "or"]
            req_node = xml_doc().createElement(operand)
            for dct in operand_value:
                if dct.get("or") or dct.get("and"):
                    self._translate_constraint(dct, req_node)
                else:
                    req_node = add_dict_to_node(req_node, dct)
            host_recipe.appendChild(req_node)

    def _req_to_bkr_job(self, req):  # pylint: disable=too-many-locals
        """Transform requirement to beaker job xml."""
        specs = deepcopy(req)  # work with own copy, do not modify the input

        # Create recipe with the specifications
        recipe = BeakerRecipe(**specs)
        recipe.addBaseRequires(**specs)

        # Specify the architecture
        arch_node = xml_doc().createElement("distro_arch")
        arch_node.setAttribute("op", "=")
        arch_node.setAttribute("value", specs["arch"])
        recipe.addDistroRequires(arch_node)

        host_requires = specs.get("hostRequires")
        if host_requires:
            host_recipe = recipe.node.getElementsByTagName("hostRequires")[0]
            self._translate_constraint(host_requires, host_recipe)

        # Specify the custom xml distro_tag node with values from provisioning config
        distro_tags = specs.get("distro_tags")
        if distro_tags:
            for tag in distro_tags:
                tag_node = xml_doc().createElement("distro_tag")
                tag_node.setAttribute("op", "=")
                tag_node.setAttribute("value", tag)
                recipe.addDistroRequires(tag_node)

        # Add ReserveSys element to reserve system after provisioning
        recipe.addReservesys(duration=str(self.reserve_duration))

        # Add watchdog element if configured
        watchdog_config = specs.get("watchdog")
        if watchdog_config and isinstance(watchdog_config, dict):
            watchdog_node = xml_doc().createElement("watchdog")
            for key, value in watchdog_config.items():
                watchdog_node.setAttribute(key, str(value))
            recipe.node.appendChild(watchdog_node)

        for task in specs["tasks"]:
            recipe.addTask(
                task=task["name"],
                role=task["role"],
                taskParams=task.get("params"),
                fetch_url=task.get("fetch_url"),
            )

        # Create RecipeSet and add our Recipe to it.
        recipe_set = BeakerRecipeSet(**specs)
        recipe_set.addRecipe(recipe)

        # Create job instance and inject created RecipeSet to it
        job = BeakerJob(**specs)
        job.addRecipeSet(recipe_set)

        return job

    def login_beaker(self):
        """Login to the beaker hub."""
        login_start = datetime.now()
        default_config = os.path.expanduser(
            os.environ.get("BEAKER_CONF", "/etc/beaker/client.conf")  # TODO use provc
        )  # get the beaker config for initialization of hub
        self.conf.load_from_file(default_config)
        try:
            self.hub = HubProxy(logger=logger, conf=self.conf)
        except MissingCredentialsError as kinit_err:
            raise NotAuthenticatedError(
                f"{self.dsp_name} needs Kerberos ticket to authenticate to BeakerHub. "
                "Run 'kinit $USER' command to obtain Kerberos credentials."
            ) from kinit_err
        except GSSError as hub_err:
            raise NotAuthenticatedError(
                f"{self.dsp_name} Unable to Create session: {hub_err}"
            ) from hub_err

        login_end = datetime.now()
        login_duration = login_end - login_start
        logger.info(f"{self.dsp_name} Init duration {login_duration}")

    async def create_server(self, req):
        """Issue creation of a server.

        req - dict of server requirements

        The req object can contain following additional attributes:
        * 'name':       name for the VM
        * 'distro':     beaker distribution to use
        * 'arch':       architecture to request from beaker
        * 'variant':    variant of the system

        Returns:
            A tuple containing, respectively, a string (<created beaker job id>)
            and a dict (<requirements for VM>)
            :rtype: (str, dict)
        """
        logger.info(f"{self.dsp_name} [{req.get('name')}] Creating server")

        job = self._req_to_bkr_job(req)  # Generate the job
        if not self.hub:
            self.login_beaker()
        try:
            job_id = self.hub.jobs.upload(job.toxml())  # schedule beaker job
        except Fault as bkr_fault:
            # use the name as id for the logging purposes
            req["host_id"] = req.get("name")
            raise ProvisioningError(
                parse_bkr_exc_str(bkr_fault),
                req,
            ) from bkr_fault

        return (job_id, req)

    def prov_result_to_host_data(self, prov_result, req):
        """Transform provisioning result to needed host data."""
        try:
            ip_address = socket.gethostbyname(prov_result["system"])
        except (TypeError, socket.gaierror):
            ip_address = None

        result = {
            "id": prov_result["JobID"],
            "name": prov_result.get("mrack_req").get("name"),
            "addresses": [ip_address],
            "status": prov_result["status"],
            "fault": None,
            "os": prov_result.get("mrack_req").get("os"),
            "group": prov_result.get("mrack_req").get("group"),
        }

        if prov_result["result"] != "Pass":
            result.update(
                {
                    "fault": prov_result["result"],
                    "status": "MRACK_RESULT_NOT_PASSED",
                }
            )

        return result

    def _get_recipe_info(self, beaker_id, log_msg_start):
        """Get info about the recipe for beaker job id."""
        if not self.hub:
            self.login_beaker()
        bkr_job_xml = self.hub.taskactions.to_xml(beaker_id).encode("utf8")
        logs_dict = {}
        resources = []
        for recipe in eTree.fromstring(bkr_job_xml).iter("recipe"):
            for logs in recipe.iter("logs"):
                for log in logs.iter("log"):
                    logs_dict[log.get("name")] = log.get("href")
            resources.append(
                {
                    "system": recipe.get("system"),
                    "status": recipe.get("status"),
                    "result": recipe.get("result"),
                    "rid": recipe.get("id"),
                    "id": recipe.get("job_id"),
                    "logs": logs_dict,
                }
            )

        logger.debug(
            f"{log_msg_start} has status:{resources[0]['status']}, "
            f"result:{resources[0]['result']}, waiting another {self.poll_sleep:.1f}s"
        )

        return resources[0]

    async def wait_till_provisioned(self, resource):
        """Wait for Beaker provisioning result."""
        beaker_id, req = resource
        log_msg_start = f"{self.dsp_name} [{req.get('name')}]"
        bkr_res = {}
        prev_status = ""
        job_url = ""
        if not self.hub:
            self.login_beaker()
        hub_url = self.hub._hub_url  # pylint: disable=protected-access

        # let us use timeout variable which is in minutes to define
        # maximum time to wait for beaker recipe to provide VM
        timeout_time = datetime.now() + timedelta(minutes=self.timeout)

        while datetime.now() < timeout_time:
            prev_bkr_res = bkr_res
            try:
                bkr_res = self._get_recipe_info(beaker_id, log_msg_start=log_msg_start)
            except TimeoutError as timeout:
                logger.warning(
                    f"{log_msg_start} Can not connect to {hub_url}: {timeout}"
                )
                logger.debug(
                    f"{log_msg_start} Using previous result "
                    f"and retrying in {self.poll_sleep:.1f}s"
                )
                bkr_res = prev_bkr_res

            status = bkr_res.get("status", "")
            job_url = f"{hub_url}/jobs/{bkr_res.get('id', None)}"

            status_changed = prev_status != status
            if status_changed:
                logger.info(
                    f"{log_msg_start} Job {job_url} "
                    f"has changed status ({prev_status} -> {status})"
                )
                prev_status = status

            # if we have problem contacting hub from beginning: status will not change
            if self.status_map.get(status) == STATUS_PROVISIONING or not status_changed:
                await asyncio.sleep(self.poll_sleep)
            elif self.status_map.get(status) == STATUS_ACTIVE:
                break
            elif self.status_map.get(status) in [STATUS_ERROR, STATUS_DELETED]:
                logger.warning(
                    f"{log_msg_start} Job {job_url} has errored with status "
                    f"{status} and result {bkr_res['result']}"
                )
                bkr_res.update({"result": f"Job {job_url} failed to provision"})
                break
            else:
                logger.error(
                    f"{log_msg_start} Job {job_url} has switched to unexpected "
                    f"status {status} with result {bkr_res['result']}"
                )
                bkr_res.update({"result": f"Job {job_url} failed to provision"})
                break

        else:
            # In this case we failed to provision host in time:
            # we need to create failed host object for mrack
            # to delete the resource by cancelling the beaker job.
            logger.error(
                f"{log_msg_start} Job {job_url} failed to provide bkr_res in"
                f" the timeout of {self.timeout} minutes"
            )
            bkr_res.update(
                {
                    "status": "MRACK_REACHED_TIMEOUT",
                    "result": f"Job {job_url} reached timeout",
                }
            )

        bkr_res.update(
            {
                "JobID": beaker_id,
                "mrack_req": req,
            }
        )
        return bkr_res, req

    async def delete_host(self, host_id, host_name):
        """Delete provisioned hosts based on input from provision_hosts."""
        # host_id should start with 'J:' this way we know job has been scheduled
        # and proper response from beaker hub has beed returned.
        # Other way (In case of hub error or invalid host definition)
        # the provider uses hostname from metadata of the VM which has failed
        # to validate the requirements for the provider
        log_msg_start = f"{self.dsp_name} [{host_name}]"
        if host_id.isdigit():
            host_id = "J:" + host_id
        if not host_id.startswith("J:"):
            logger.warning(
                f"{log_msg_start} Job for host '{host_id}' does not exist yet"
            )
            return True

        if not self.hub:
            self.login_beaker()

        logger.info(
            f"{log_msg_start} Deleting host by cancelling Job "
            f"{self.hub._hub_url}"  # pylint: disable=protected-access
            f"/jobs/{host_id.split(':')[1]}"
        )
        return self.hub.taskactions.stop(
            host_id, "cancel", "Job has been stopped by mrack."
        )

    def to_host(self, provisioning_result, req, username="root"):
        """Transform provisioning result into Host object."""
        return super().to_host(provisioning_result, req, username)
