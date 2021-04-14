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
from datetime import datetime
from xml.dom.minidom import Document as xml_doc

from bkr.client import BeakerJob, BeakerRecipe, BeakerRecipeSet
from bkr.common.hub import HubProxy
from bkr.common.pyconfig import PyConfigParser

from mrack.errors import ValidationError
from mrack.host import (
    STATUS_ACTIVE,
    STATUS_DELETED,
    STATUS_ERROR,
    STATUS_OTHER,
    STATUS_PROVISIONING,
)
from mrack.providers.provider import STRATEGY_ABORT, Provider

logger = logging.getLogger(__name__)

PROVISIONER_KEY = "beaker"


class BeakerProvider(Provider):
    """Beaker Provider."""

    def __init__(self):
        """Object initialization."""
        self._name = PROVISIONER_KEY
        self.dsp_name = "Beaker"
        self.strategy = STRATEGY_ABORT
        self.conf = PyConfigParser()
        self.poll_sleep = 30  # seconds
        self.pubkey = None
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
        }

    async def init(self, distros, max_attempts, reserve_duration, pubkey):
        """Initialize provider with data from Beaker configuration."""
        logger.info(f"{self.dsp_name}: Initializing provider")
        self.distros = distros
        # eg: 240 attempts * 30s timeout - 2h timeout for job to complete
        self.max_attempts = max_attempts
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

    def _req_to_bkr_job(self, req):
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
        """
        logger.info(f"{self.dsp_name}: Creating server")

        job = self._req_to_bkr_job(req)  # Generate the job

        job_id = self.hub.jobs.upload(job.toxml())  # schedule beaker job

        return (job_id, req["name"])

    def prov_result_to_host_data(self, prov_result):
        """Transform provisioning result to needed host data."""
        try:
            ip_address = socket.gethostbyname(prov_result["system"])
        except socket.gaierror:
            ip_address = None

        result = {
            "id": prov_result["JobID"],
            "name": prov_result["req_name"],
            "addresses": [ip_address],
            "status": prov_result["status"],
            "fault": prov_result["result"] if prov_result["result"] != "Pass" else None,
        }

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
        beaker_id, req_name = resource
        resource = {}
        attempts = 0
        prev_status = ""

        while attempts < self.max_attempts:
            attempts += 1
            resource = self._get_recipe_info(beaker_id)
            status = resource["status"]

            if prev_status != status:
                logger.info(
                    f"{self.dsp_name}: Job {beaker_id} has changed "
                    f"status ({prev_status} -> {status})"
                )
                prev_status = status

            if self.status_map.get(status) == STATUS_PROVISIONING:
                await asyncio.sleep(self.poll_sleep)
            elif self.status_map.get(status) == STATUS_ACTIVE:
                break
            elif self.status_map.get(status) in [STATUS_ERROR, STATUS_DELETED]:
                logger.warning(
                    f"{self.dsp_name}: Job {beaker_id} has errored with status "
                    f"{status} and result {resource['result']}"
                )
                break
            else:
                logger.error(
                    f"{self.dsp_name}: Job {beaker_id} has swithced to unexpected "
                    f"status {status} with result {resource['result']}"
                )
                break

        resource.update({"JobID": beaker_id, "req_name": req_name})
        return resource

    async def delete_host(self, host_id):
        """Delete provisioned hosts based on input from provision_hosts."""
        logger.info(f"{self.dsp_name}: Deleting host by cancelling Job {host_id}")
        return self.hub.taskactions.stop(
            host_id, "cancel", "Job has been stopped by mrack."
        )

    def to_host(self, provisioning_result, username=None):
        """Transform provisioning result into Host object."""
        return super().to_host(provisioning_result, username="root")
