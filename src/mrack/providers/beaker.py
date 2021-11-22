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

from mrack.context import global_context
from mrack.errors import ProvisioningError, ValidationError
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
    """Parse exception string and return more readable string for mrack error."""
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
        return str(exc_str)

    # because of expected format we split by ":" and use last 2 values from list
    # in above example it would be
    # [
    #   '\tNo distro tree matches Recipe',
    #   '\t<distroRequires><and><distro_name op="like" value="Fedora-33%"/> ...
    # ]
    fault = [f"\t{f.strip()}" for f in exc_str.faultString.split(":")[-2:]]
    return "\n".join(fault)


class BeakerProvider(Provider):
    """Beaker Provider."""

    def __init__(self):
        """Object initialization."""
        self._name = PROVISIONER_KEY
        self.dsp_name = "Beaker"
        self.conf = PyConfigParser()
        self.poll_sleep = 45  # seconds
        self.pubkey = None
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
        pubkey,
        strategy=STRATEGY_ABORT,
        max_retry=1,
    ):
        """Initialize provider with data from Beaker configuration."""
        logger.info(f"{self.dsp_name}: Initializing provider")
        self.strategy = strategy
        self.max_retry = max_retry
        self.distros = distros
        self.timeout = timeout
        self.reserve_duration = reserve_duration
        self.pubkey = pubkey
        login_start = datetime.now()
        default_config = os.path.expanduser(
            os.environ.get("BEAKER_CONF", "/etc/beaker/client.conf")  # TODO use provc
        )  # get the beaker config for initialization of hub
        self.conf.load_from_file(default_config)
        self.hub = HubProxy(logger=logger, conf=self.conf)
        login_end = datetime.now()
        login_duration = login_end - login_start
        logger.info(f"{self.dsp_name}: Init duration {login_duration}")

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
        for req in reqs:
            req_dstr = req.get("distro")
            if not req.get("meta_distro") and req_dstr not in self.distros:
                raise ValidationError(
                    f"{self.dsp_name} provider does not support "
                    f"'{req_dstr}' distro in provisioning config"
                )
        return

    async def prepare_provisioning(self, reqs):
        """Prepare provisioning."""
        pass

    async def can_provision(self, hosts):
        """Check that hosts can be provisioned."""
        return True

    def _allow_ssh_key(self, pubkey):

        with open(os.path.expanduser(pubkey), "r") as key_file:
            key_content = key_file.read()

        return [
            """%%post
mkdir -p /root/.ssh
cat >>/root/.ssh/authorized_keys << "__EOF__"
%s__EOF__
restorecon -R /root/.ssh
chmod go-w /root /root/.ssh /root/.ssh/authorized_keys
%%end"""
            % "".join(key_content)
        ]

    def _req_to_bkr_job(self, req):  # pylint: disable=too-many-locals
        """Transform requirement to beaker job xml."""
        specs = deepcopy(req)  # work with own copy, do not modify the input

        # Job attributes:
        specs.update({"retention_tag": "audit"})
        specs.update({"product": "[internal]"})
        specs.update({"whiteboard": "This job has been created using mrack."})

        # RecipeSet attributes
        specs.update({"priority": "Normal"})

        # Add allowed keys
        specs.update({"ks_append": self._allow_ssh_key(self.pubkey)})

        # Use ks_meta
        specs.update({"ks_meta": "harness='restraint-rhts beakerlib-redhat'"})

        # Recipe task definition
        specs.update(
            {  # we use dummy task because beaker reuire a task in recipe
                "tasks": [{"name": "/distribution/dummy", "role": "STANDALONE"}]
            }
        )

        # Create recipe with the specifications
        recipe = BeakerRecipe(**specs)
        recipe.addBaseRequires(**specs)

        # Specify the architecture
        arch_node = xml_doc().createElement("distro_arch")
        arch_node.setAttribute("op", "=")
        arch_node.setAttribute("value", specs["arch"])
        recipe.addDistroRequires(arch_node)

        host_requires = global_context.PROV_CONFIG[PROVISIONER_KEY].get(
            "hostRequires",
            specs.get(f"mrack_{PROVISIONER_KEY}", {}).get("hostRequires", {}),
        )

        if host_requires:  # suppose to be dict like {"or": [dict()], "and": [dict()]}
            for operand, operand_value in host_requires.items():
                if operand.startswith("_"):
                    recipe.node.getElementsByTagName("hostRequires")[0].setAttribute(
                        operand[1:],
                        operand_value,
                    )
                    continue
                # known operands are ["and", "or"]
                req_node = xml_doc().createElement(operand)
                for dct in operand_value:
                    req_node = add_dict_to_node(req_node, dct)

                recipe.node.getElementsByTagName("hostRequires")[0].appendChild(
                    req_node
                )

        # Specify the custom xml distro_tag node with values from provisioning config
        distro_tags = global_context.PROV_CONFIG["beaker"].get("distro_tags")
        if distro_tags:
            for tag in distro_tags.get(specs["distro"], []):
                tag_node = xml_doc().createElement("distro_tag")
                tag_node.setAttribute("op", "=")
                tag_node.setAttribute("value", tag)
                recipe.addDistroRequires(tag_node)

        # Add ReserveSys element to reserve system after provisioning
        recipe.addReservesys(duration=str(self.reserve_duration))

        for task in specs["tasks"]:
            recipe.addTask(task=task["name"], role=task["role"])

        # Create RecipeSet and add our Recipe to it.
        recipe_set = BeakerRecipeSet(**specs)
        recipe_set.addRecipe(recipe)

        # Create job instance and inject created RecipeSet to it
        job = BeakerJob(**specs)
        job.addRecipeSet(recipe_set)

        return job

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
        logger.info(f"{self.dsp_name}: Creating server")

        job = self._req_to_bkr_job(req)  # Generate the job
        try:
            job_id = self.hub.jobs.upload(job.toxml())  # schedule beaker job
        except Fault as bkr_fault:
            # use the name as id for the logging purposes
            req["host_id"] = req["name"]
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

    def _get_recipe_info(self, beaker_id):
        """Get info about the recipe for beaker job id."""
        bkr_job_xml = self.hub.taskactions.to_xml(beaker_id).encode("utf8")

        resources = []
        for recipe in eTree.fromstring(bkr_job_xml).iter("recipe"):
            resources.append(
                {
                    "system": recipe.get("system"),
                    "status": recipe.get("status"),
                    "result": recipe.get("result"),
                    "rid": recipe.get("id"),
                    "id": recipe.get("job_id"),
                }
            )

        return resources[0] if len(resources) == 1 else []

    async def wait_till_provisioned(self, resource):
        """Wait for Beaker provisioning result."""
        beaker_id, req = resource
        resource = {}
        prev_status = ""
        job_url = ""

        # let us use timeout variable which is in minutes to define
        # maximum time to wait for beaker recipe to provide VM
        timeout_time = datetime.now() + timedelta(minutes=self.timeout)

        while datetime.now() < timeout_time:
            resource = self._get_recipe_info(beaker_id)
            status = resource["status"]
            job_url = (
                f"{self.hub._hub_url}"  # pylint: disable=protected-access
                f"/jobs/{resource['id']}"
            )

            if prev_status != status:
                logger.info(
                    f"{self.dsp_name}: Job {job_url} "
                    f"has changed status ({prev_status} -> {status})"
                )
                prev_status = status
            else:
                logger.info(
                    f"{self.dsp_name}: Job {job_url} has not changed status "
                    f"({status}), waiting another {self.poll_sleep:.1f}s"
                )

            if self.status_map.get(status) == STATUS_PROVISIONING:
                await asyncio.sleep(self.poll_sleep)
            elif self.status_map.get(status) == STATUS_ACTIVE:
                break
            elif self.status_map.get(status) in [STATUS_ERROR, STATUS_DELETED]:
                logger.warning(
                    f"{self.dsp_name}: Job {job_url} has errored with status "
                    f"{status} and result {resource['result']}"
                )
                resource.update({"result": f"Job {job_url} failed to provision"})
                break
            else:
                logger.error(
                    f"{self.dsp_name}: Job {job_url} has switched to unexpected "
                    f"status {status} with result {resource['result']}"
                )
                resource.update({"result": f"Job {job_url} failed to provision"})
                break

        else:
            # In this case we failed to provision host in time:
            # we need to create failed host object for mrack
            # to delete the resource by cancelling the beaker job.
            logger.error(
                f"{self.dsp_name}: Job {job_url} failed to provide resource in"
                f" the timeout of {self.timeout} minutes"
            )
            resource.update(
                {
                    "status": "MRACK_REACHED_TIMEOUT",
                    "result": f"Job {job_url} reached timeout",
                }
            )

        resource.update(
            {
                "JobID": beaker_id,
                "mrack_req": req,
            }
        )
        return resource, req

    async def delete_host(self, host_id):
        """Delete provisioned hosts based on input from provision_hosts."""
        # host_id should start with 'J:' this way we know job has been scheduled
        # and proper response from beaker hub has beed returned.
        # Other way (In case of hub error or invalid host definition)
        # the provider uses hostname from metadata of the VM which has failed
        # to validate the requirements for the provider
        if not host_id.startswith("J:"):
            logger.warning(
                f"{self.dsp_name}: Job for host '{host_id}' does not exist yet"
            )
            return True

        logger.info(
            f"{self.dsp_name}: Deleting host by cancelling Job "
            f"{self.hub._hub_url}"  # pylint: disable=protected-access
            f"/jobs/{host_id.split(':')[1]}"
        )
        return self.hub.taskactions.stop(
            host_id, "cancel", "Job has been stopped by mrack."
        )

    def to_host(self, provisioning_result, req, username="root"):
        """Transform provisioning result into Host object."""
        return super().to_host(provisioning_result, req, username)
