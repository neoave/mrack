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

import logging
import typing
from copy import deepcopy
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from mrack.errors import ProvisioningError, ValidationError
from mrack.host import STATUS_ACTIVE, STATUS_DELETED, STATUS_ERROR, STATUS_PROVISIONING
from mrack.providers.provider import STRATEGY_ABORT, Provider

logger = logging.getLogger(__name__)

PROVISIONER_KEY = "aws"


class AWSProvider(Provider):
    """AWS Provider."""

    def __init__(self):
        """Object initialization."""
        self._name = PROVISIONER_KEY
        self.dsp_name = "AWS"
        self.strategy = STRATEGY_ABORT
        self.ami_ids: typing.List[str] = []
        self.ssh_key = None
        self.sec_group = None
        self.instance_tags = None
        self.status_map = {
            "running": STATUS_ACTIVE,
            "pending": STATUS_PROVISIONING,
            "terminated": STATUS_DELETED,
            "error": STATUS_ERROR,
            # there is much more we can treat it as STATUS_OTHER, see statuses:
            # pending | running | shutting-down | terminated | stopping | stopped
        }

    @property
    def name(self):
        """Get provider name."""
        return self._name

    async def init(self, ami_ids, ssh_key, sec_group, instance_tags):
        """Initialize provider with data from AWS."""
        # AWS_CONFIG_FILE=`readlink -f ./aws.key`
        logger.info(f"{self.dsp_name}: Initializing provider")
        login_start = datetime.now()
        self.ec2 = boto3.resource("ec2")
        self.client = boto3.client("ec2")
        login_end = datetime.now()
        login_duration = login_end - login_start
        logger.info(f"{self.dsp_name}: Login duration {login_duration}")
        self.ami_ids = ami_ids
        self.ssh_key = ssh_key
        self.sec_group = sec_group
        self.instance_tags = instance_tags

    async def prepare_provisioning(self, reqs):
        """Prepare provisioning."""
        pass

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
        for req in reqs:
            req_img = req.get("image")
            if not req.get("meta_image") and req_img not in self.ami_ids:
                raise ValidationError(
                    f"{self.dsp_name}: Provider does not support "
                    f"'{req_img}' image in provisioning config"
                )

            try:
                aws_image = self.ec2.Image(req_img)
                if not aws_image:  # user is not authorized to use ami - None returned
                    raise ValidationError(
                        f"{self.dsp_name}: User does not have enough permissions "
                        f"to use image: {req_img}"
                    )

                logger.info(
                    f"{self.dsp_name}: Requested provisioning of {aws_image.name} image"
                )
            except ClientError as image_err:
                err_msg = (
                    f"{self.dsp_name}: Requested image "
                    f"'{req_img}' can not be provisioned"
                )
                logger.error(err_msg)
                err_resp = image_err.response["Error"]["Message"]
                raise ValidationError(
                    f"{err_msg} Request failed with {err_resp}"
                ) from image_err

        return

    async def can_provision(self, hosts):
        """Check that hosts can be provisioned."""
        return True

    async def create_server(self, req):
        """Issue creation of a server.

        req - dict of server requirements

        The req object can contain following additional attributes:
        * 'image': ami or name of image
        * 'flavor': flavor to use
        """
        logger.info(f"{self.dsp_name}: Creating server")
        specs = deepcopy(req)  # work with own copy, do not modify the input

        aws_res = self.ec2.create_instances(
            ImageId=specs.get("image"),
            MinCount=1,
            MaxCount=1,
            InstanceType=specs.get("flavor"),
            KeyName=self.ssh_key,
            SecurityGroupIds=[self.sec_group],
        )

        ids = [srv.id for srv in aws_res]
        if len(ids) != 1:  # ids must be len of 1 as we provision one vm at the time
            raise ProvisioningError("Unexpected number of instances provisioned.", req)
        # creating name for instance (visible in aws ec2 WebUI)
        taglist = [{"Key": "name", "Value": specs.get("name")}]
        for key in self.instance_tags:
            taglist.append({"Key": key, "Value": self.instance_tags[key]})

        self.ec2.create_tags(Resources=ids, Tags=taglist)

        # returns id of provisioned instance
        return ids[0]

    def prov_result_to_host_data(self, prov_result):
        """Transform provisioning result to needed host data."""
        # init the dict
        result = {}

        result["id"] = prov_result.get("InstanceId")
        for tag in prov_result.get("Tags"):
            if tag["Key"] == "name":
                result["name"] = tag["Value"]  # should be one key "name"

        result["addresses"] = [prov_result.get("PublicIpAddress")]
        result["status"] = prov_result["State"]["Name"]

        return result

    async def wait_till_provisioned(self, aws_id):  # pylint: disable=arguments-differ
        """Wait for AWS provisioning result."""
        instance = self.ec2.Instance(aws_id)
        instance.wait_until_running()
        response = self.client.describe_instances(InstanceIds=[aws_id])
        result = {}
        try:  # returns dict with aws instance information
            result = response["Reservations"][0]["Instances"][0]
        except (KeyError, IndexError) as data_err:
            raise ProvisioningError(
                "Unexpected data format in response of provisioned instance."
            ) from data_err

        return result

    async def delete_host(self, host_id):
        """Delete provisioned hosts based on input from provision_hosts."""
        logger.info(f"{self.dsp_name}: Terminating host {host_id}")
        ids = [host_id]
        self.ec2.instances.filter(InstanceIds=ids).stop()
        self.ec2.instances.filter(InstanceIds=ids).terminate()
        return True
