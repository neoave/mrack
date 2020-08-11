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
from bkr.common.hub import HubProxy
from bkr.common.pyconfig import PyConfigParser
from bkr.client import BeakerRecipeSet, BeakerRecipe, BeakerJob
from xml.dom.minidom import Document as xml_doc


from mrack.host import (
    STATUS_ACTIVE,
    STATUS_DELETED,
    STATUS_ERROR,
    STATUS_OTHER,
    STATUS_PROVISIONING,
    Host,
)
from mrack.providers.provider import Provider

logger = logging.getLogger(__name__)

PROVISIONER_KEY = "beaker"

STATUS_MAP = {
    "Reserved": STATUS_ACTIVE,
    "New": STATUS_PROVISIONING,
    "Processed": STATUS_PROVISIONING,
    "Waiting": STATUS_PROVISIONING,
    "Installing": STATUS_PROVISIONING,
    "Running": STATUS_PROVISIONING,
    "Cancelled": STATUS_DELETED,
    "Aborted": STATUS_ERROR,
    "Completed": STATUS_OTHER,
}


class BeakerProvider(Provider):
    """Beaker Provider."""

    def __init__(self):
        """Object initialization."""
        self._name = PROVISIONER_KEY
        self.conf = PyConfigParser()
        self.poll_sleep = 30  # seconds

    async def init(self, prov_config):
        """Initialize provider with data from Beaker configuration."""
        self.prov_config = prov_config
        logger.info("Initializing Beaker provider")
        # eg: 240 attempts * 30s timeout - 2h timeout for job to complete
        self.max_attempts = prov_config["max_attempts"]
        login_start = datetime.now()
        default_config = os.path.expanduser(
            os.environ.get("BEAKER_CONF", "/etc/beaker/client.conf")  # TODO use provc
        )  # get the beaker config for initialization of hub
        self.conf.load_from_file(default_config)
        self.hub = HubProxy(logger=logger, conf=self.conf)
        login_end = datetime.now()
        login_duration = login_end - login_start
        logger.info(f"Login duration {login_duration}")

    async def validate_hosts(self, hosts):
        """Validate that host requirements are well specified."""
        return

    def _allow_ssh_key(self, ssh_key):

        with open(ssh_key, "r") as key_file:
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
        specs = deepcopy(req)  # work with own copy, do not modify the input

        # Job attributes:
        specs.update({"retention_tag": "audit"})
        specs.update({"product": "[internal]"})
        specs.update({"whiteboard": "This job has been created using mrack."})

        # RecipeSet attributes
        specs.update({"priority": "Normal"})

        # Add allowed keys
        keypair = self.prov_config.get("keypair", None)
        if keypair:
            specs.update({"ks_append": self._allow_ssh_key(keypair)})

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
        recipe.addReservesys(duration=str(self.prov_config["reserve_duration"]))

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
        logger.info("Creating Beaker server")

        job = self._req_to_bkr_job(req)  # Generate the job

        job_id = self.hub.jobs.upload(job.toxml())  # schedule beaker job

        return (job_id, req["name"])

    def _get_host_info_from_prov_result(self, prov_result):
        """Get needed host infromation from Beaker provisioning result."""
        # init the dict
        try:
            ip_address = socket.gethostbyname(prov_result["system"])
        except socket.gaierror:
            ip_address = None

        result = {
            "id": prov_result["JobID"],
            "name": prov_result["hname"],
            "addresses": [ip_address],
            "status": prov_result["status"],
            "fault": prov_result["result"] if prov_result["result"] != "Pass" else None,
        }

        return result

    def _get_recipe_info(self, beaker_id):
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

    async def wait_till_provisioned(
        self, bkr_id_name, timeout=None, poll_sleep=None, max_attempts=None
    ):
        """Wait for Beaker provisioning result."""
        beaker_id, req_hname = bkr_id_name

        if not poll_sleep:
            poll_sleep = self.poll_sleep
        if not max_attempts:
            max_attempts = self.max_attempts

        resource = {}
        attempts = 0
        prev_status = ""

        while attempts < self.max_attempts:
            attempts += 1
            resource = self._get_recipe_info(beaker_id)
            status = resource["status"]

            if prev_status != status:
                logger.info(
                    f"Job {beaker_id} has changed status ("
                    f"{prev_status} -> {status})"
                )
                prev_status = status

            if STATUS_MAP.get(status) == STATUS_ACTIVE:
                break
            elif STATUS_MAP.get(status) == STATUS_PROVISIONING:
                await asyncio.sleep(self.poll_sleep)
            elif STATUS_MAP.get(status) in [STATUS_ERROR, STATUS_DELETED]:
                logger.warning(
                    f"Job {beaker_id} has errored with status "
                    f"{status} with result {resource['result']}"
                )
                break
            else:
                logger.error(
                    f"Job {beaker_id} has swithced to status "
                    f"{status} with result {resource['result']}"
                )
                break

        resource.update({"JobID": beaker_id, "hname": req_hname})
        return resource

    async def provision_hosts(self, hosts):
        """Provision hosts based on list of host requirements.

        Issues provisioning and waits for it succeed. Raises exception if any of
        the servers was not successfully provisioned. If that happens it issues deletion
        of all already provisioned resources.

        Return list of information about provisioned servers.
        """
        started = datetime.now()

        count = len(hosts)
        logger.info(f"Issuing provisioning of {count} hosts")
        create_res = []
        for req in hosts:
            resource = self.create_server(req)
            create_res.append(resource)

        create_resps = await asyncio.gather(*create_res)
        logger.info("Provisioning issued")

        logger.info("Waiting for all Beaker hosts to be available")
        wait_res = []
        for resp in create_resps:
            resource = self.wait_till_provisioned(resp)
            wait_res.append(resource)

        server_results = await asyncio.gather(*wait_res)

        provisioned = datetime.now()
        provi_duration = provisioned - started

        logger.info("All Beaker hosts reached provisioning final state (Reserved)")
        logger.info(f"Provisioning duration: {provi_duration}")

        hosts = [self.to_host(srv) for srv in server_results]
        for host in hosts:
            logger.info(host)

        return hosts

    async def delete_host(self, host):
        """Delete provisioned hosts based on input from provision_hosts."""
        logger.info(f"Deleting Beaker host from Job {host.id}")
        return self.hub.taskactions.stop(
            host.id, "cancel", "Job has been cancelled by mrack."
        )

    async def delete_hosts(self, hosts):
        """Issue deletion of all servers based on previous results from provisioning."""
        logger.info("Issuing Beaker deletion")

        delete_bkr = []
        for host in hosts:
            awaitable = self.delete_host(host)
            delete_bkr.append(awaitable)
        results = await asyncio.gather(*delete_bkr)
        logger.info("All Beaker servers issued to be deleted")

        return results

    def to_host(self, provisioning_result):
        """Transform provisioning result into Host object."""
        host_info = self._get_host_info_from_prov_result(provisioning_result)

        host = Host(
            self,
            host_info.get("id"),
            host_info.get("name"),
            host_info.get("addresses"),
            STATUS_MAP.get(host_info.get("status"), STATUS_OTHER),
            provisioning_result,
            error_obj=host_info.get("fault"),
        )

        return host
