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

"""AWS Provider interface."""

import asyncio
import boto3
import logging

from copy import deepcopy
from datetime import datetime
from aiohabit.providers.provider import Provider
from aiohabit.host import (
    Host,
    STATUS_ACTIVE,
    STATUS_PROVISIONING,
    STATUS_DELETED,
    STATUS_ERROR,
    STATUS_OTHER,
)

logger = logging.getLogger(__name__)

PROVISIONER_KEY = "aws"

STATUS_MAP = {
    "running": STATUS_ACTIVE,
    "pending": STATUS_PROVISIONING,
    "terminated": STATUS_DELETED,
    "error": STATUS_ERROR,
    # there is much more we can treat it as STATUS_OTHER, see statuses:
    # pending | running | shutting-down | terminated | stopping | stopped
}


class AWSProvider(Provider):
    """AWS Provider."""

    def __init__(self):
        """Object initialization."""
        self._name = PROVISIONER_KEY
        self.flavors = {}
        self.flavors_by_ref = {}
        self.images = {}
        self.images_by_ref = {}
        self.limits = {}
        self.networks = {}
        self.networks_by_ref = {}
        self.ips = {}
        self.ips_by_ref = {}
        self.timeout = 60  # minutes
        self.poll_sleep_initial = 15  # seconds
        self.poll_sleep = 7  # seconds

    @property
    def name(self):
        """Get provider name."""
        return self._name

    async def init(self, image_names):
        """Initialize provider with data from AWS."""
        # AWS_CONFIG_FILE=`readlink -f ./aws.key`
        logger.info("Initializing AWS provider")
        login_start = datetime.now()
        self.ec2 = boto3.resource("ec2")
        self.client = boto3.client("ec2")
        login_end = datetime.now()
        login_duration = login_end - login_start
        logger.info(f"Login duration {login_duration}")

    async def validate_hosts(self, hosts):
        """Validate that host requirements are well specified."""
        return

    async def create_server(self, req):
        """Issue creation of a server.

        req - dict of server requirements

        The req object can contain following additional attributes:
        * 'image': ami or name of image
        * 'flavor': flavor to use
        """
        logger.info("Creating AWS server")
        specs = deepcopy(req)  # work with own copy, do not modify the input

        aws_res = self.ec2.create_instances(
            ImageId=specs.get("image"),
            MinCount=1,
            MaxCount=1,
            InstanceType=specs.get("flavor"),
        )

        ids = [srv.id for srv in aws_res]
        assert len(ids) == 1  # ids must be len of 1 as we provision one vm at the time

        # creating name for instance (visible in aws ec2 WebUI)
        self.ec2.create_tags(
            Resources=ids,
            Tags=[
                {"Key": "Name", "Value": "IDM-CI-runner"},
                {"Key": "name", "Value": specs.get("name")},
                {"Key": "IDM-CI", "Value": "True"},
            ],
        )
        # returns id of provisioned instance
        return ids[0]

    def _get_host_info_from_prov_result(self, prov_result):
        """Get needed host infromation from AWS provisioning result."""
        # init the dict
        result = {
            "id": None,
            "name": None,
            "addresses": None,
            "status": None,
            "fault": None,
        }
        result["id"] = prov_result.get("InstanceId")
        for tag in prov_result.get("Tags"):
            if tag["Key"] == "name":
                result["name"] = tag["Value"]  # should be one key "name"
        interfaces = prov_result.get("NetworkInterfaces")
        int_addr = [inter.get("PrivateIpAddresses") for inter in interfaces]
        result["addresses"] = [
            addr.get("PrivateIpAddress") for addr_list in int_addr for addr in addr_list
        ]
        result["status"] = prov_result["State"]["Name"]

        return result

    async def wait_till_provisioned(self, aws_id):
        """Wait for AWS provisioning result."""
        instance = self.ec2.Instance(aws_id)
        instance.wait_until_running()
        response = self.client.describe_instances(InstanceIds=[aws_id])
        assert len(response["Reservations"]) == 1
        assert len(response["Reservations"][0]["Instances"]) == 1
        result = response["Reservations"][0]["Instances"][0]
        # returns dict with aws instance information
        return result

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
        create_aws = []
        for req in hosts:
            aws = self.create_server(req)
            create_aws.append(aws)
        create_resps = await asyncio.gather(*create_aws)
        logger.info("Provisioning issued")
        logger.info(create_resps)

        logger.info("Waiting for all AWS hosts to be available")
        wait_aws = []
        for create_resp in create_resps:
            aws = self.wait_till_provisioned(create_resp)
            wait_aws.append(aws)

        server_results = await asyncio.gather(*wait_aws)

        provisioned = datetime.now()
        provi_duration = provisioned - started

        logger.info("All AWS hosts reached provisioning final state (running)")
        logger.info(f"Provisioning duration: {provi_duration}")

        hosts = [self.to_host(srv) for srv in server_results]
        for host in hosts:
            logger.info(host)

        return hosts

    async def delete_host(self, host):
        """Delete provisioned hosts based on input from provision_hosts."""
        logger.info(f"Deleting AWS host {host.id}")
        ids = [host._id]
        self.ec2.instances.filter(InstanceIds=ids).stop()
        self.ec2.instances.filter(InstanceIds=ids).terminate()
        return True

    async def delete_hosts(self, hosts):
        """Issue deletion of all servers based on previous results from provisioning."""
        logger.info("Issuing AWS deletion")
        delete_aws = []
        for host in hosts:
            aws = self.delete_host(host)
            delete_aws.append(aws)
        results = await asyncio.gather(*delete_aws)
        logger.info("All AWS servers issued to be deleted")
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
