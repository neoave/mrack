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
from copy import deepcopy
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError
from dateutil import parser

from mrack.errors import NotAuthenticatedError, ProvisioningError, ValidationError
from mrack.host import STATUS_ACTIVE, STATUS_DELETED, STATUS_ERROR, STATUS_PROVISIONING
from mrack.providers.provider import STRATEGY_ABORT, Provider
from mrack.utils import object2json

logger = logging.getLogger(__name__)

PROVISIONER_KEY = "aws"


class AWSProvider(Provider):
    """AWS Provider."""

    def __init__(self):
        """Object initialization."""
        self._name = PROVISIONER_KEY
        self.dsp_name = "AWS"
        self.ssh_key = None
        self.instance_tags = None
        self.max_retry = 1  # for retry strategy
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

    async def init(
        self,
        ssh_key,
        instance_tags,
        strategy=STRATEGY_ABORT,
        max_retry=1,
    ):
        """Initialize provider with data from AWS."""
        # AWS_CONFIG_FILE=`readlink -f ./aws.key`
        logger.info(f"{self.dsp_name}: Initializing provider")
        login_start = datetime.now()
        self.strategy = strategy
        self.max_retry = max_retry
        try:
            self.ec2 = boto3.resource("ec2")
            self.client = boto3.client("ec2")
        except (NoRegionError, NoCredentialsError) as c_err:
            logger.debug(
                f"{self.dsp_name}: Failed loading credentials file with: {str(c_err)}"
            )
            raise NotAuthenticatedError(
                f"{self.dsp_name}: failed loading credentials. Load AWS credentials"
                " and try again. E.g.: $ export AWS_CONFIG_FILE=~/aws.key"
            ) from c_err

        self.amis = []
        self.ssh_key = ssh_key
        self.instance_tags = instance_tags
        login_end = datetime.now()
        login_duration = login_end - login_start
        logger.info(f"{self.dsp_name}: Login duration {login_duration}")

    def raise_image_def_error(self, definition):
        """Raise error that image definition is incorrect."""
        json_str = object2json(definition)
        error = f"Not a valid image definition:\n{json_str}"
        raise ValidationError(error)

    def validate_tags_image_def(self, image_def):
        """Validate that tag definition for image is correct."""
        if not isinstance(image_def, dict) or "tag" not in image_def:
            self.raise_image_def_error(image_def)

        tag_def = image_def.get("tag")
        if (
            not isinstance(tag_def, dict)
            or "name" not in tag_def
            or "value" not in tag_def
            or not isinstance(tag_def.get("name"), str)
            or not isinstance(tag_def.get("value"), str)
        ):
            self.raise_image_def_error(image_def)

        return True

    def get_image(self, req):
        """
        Get a loaded image.

        Does also basic image defintion validation.

        Return None if image is not yet loaded.
        """
        image_def = req.get("image")

        if not image_def:
            raise ValidationError(
                f"{self.dsp_name}: Host {req.get('name')} doesn't have image defined."
            )

        # by tag
        if isinstance(image_def, dict) and "tag" in image_def:
            self.validate_tags_image_def(image_def)
            tag_def = image_def.get("tag")
            for ami in self.amis:
                if not ami.tags:
                    continue
                for tag in ami.tags:
                    if (
                        tag["Key"] == tag_def["name"]
                        and tag["Value"] == tag_def["value"]
                    ):
                        return ami
        # by AMI ID
        elif isinstance(image_def, str):
            for ami in self.amis:
                if ami.image_id == image_def:
                    return ami
        else:
            raise ValidationError(
                f"{self.dsp_name}: Host {req.get('name')}: invalid image "
                f"definion. Must be 'tags' definition or AMI ID"
            )
        return None

    def load_image(self, req):
        """
        Load AMI information from EC2 based on image requirement.

        If more images match the search then the newest is returned.

        Raises validation error if no image is found.
        """
        image_def = req.get("image")
        filters = []

        # by tag
        if isinstance(image_def, dict) and "tag" in image_def:
            tag_def = image_def.get("tag")
            name = tag_def["name"]
            filters.append({"Name": f"tag:{name}", "Values": [tag_def["value"]]})

        # by AMI ID
        elif isinstance(image_def, str):
            filters.append({"Name": "image-id", "Values": [image_def]})

        amis = list(self.ec2.images.filter(Filters=filters))

        if not amis:
            raise ValidationError(
                f"{self.dsp_name}: Cannot find image for host: {req['name']}"
            )

        amis.sort(key=lambda ami: parser.parse(ami.creation_date), reverse=True)
        self.amis.append(amis[0])
        return amis[0]

    def load_images(self, reqs):
        """
        Load AMI images for all reqs.

        Done sequentially, already loaded images are not loaded again. Basically also
        validates that images are available and that their definition is correct.
        """
        for req in reqs:
            ami = self.get_image(req)
            if not ami:
                self.load_image(req)

    async def prepare_provisioning(self, reqs):
        """Prepare provisioning."""
        self.load_images(reqs)
        return bool(reqs)

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
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

        Returns:
            A tuple containing, respectively, a string (<aws machine id>)
            and a dict (<requirements for the VM>)
            :rtype: (str, dict)
        """
        logger.info(f"{self.dsp_name}: Creating server")
        specs = deepcopy(req)  # work with own copy, do not modify the input

        del_vol = specs.get("delete_volume_on_termination", True)
        request = {
            "ImageId": self.get_image(specs).image_id,
            "MinCount": 1,
            "MaxCount": 1,
            "InstanceType": specs.get("flavor"),
            "KeyName": self.ssh_key,
            "SecurityGroupIds": specs.get("security_group_ids", []),
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": {
                        "DeleteOnTermination": del_vol,
                    },
                },
            ],
        }
        if specs.get("subnet_id"):
            request["SubnetId"] = specs.get("subnet_id")

        if specs.get("spot"):
            request["InstanceMarketOptions"] = {
                "MarketType": "spot",
            }

        try:
            aws_res = self.ec2.create_instances(**request)
        except ClientError as creation_error:
            err_msg = (
                f"{self.dsp_name}: Requested image "
                f"'{specs.get('image')}' can not be provisioned"
            )
            logger.error(err_msg)
            err_resp = creation_error.response["Error"]["Message"]
            raise ProvisioningError(
                f"{err_msg} Request failed with: {err_resp}", req
            ) from creation_error

        ids = [srv.id for srv in aws_res]
        if len(ids) != 1:  # ids must be len of 1 as we provision one vm at the time
            raise ProvisioningError("Unexpected number of instances provisioned.", req)
        # creating name for instance (visible in aws ec2 WebUI)
        taglist = [{"Key": "name", "Value": specs.get("name")}]
        for key in self.instance_tags:
            taglist.append({"Key": key, "Value": self.instance_tags[key]})

        self.ec2.create_tags(Resources=ids, Tags=taglist)

        # returns id of provisioned instance and required host name
        return (ids[0], req)

    def get_ip_addresses(self, prov_result):
        """Get IP address from a provisioning result."""
        addresess = []
        if prov_result.get("PublicIpAddress"):
            addresess.append(prov_result.get("PublicIpAddress"))
        if prov_result.get("PrivateIpAddress"):
            addresess.append(prov_result.get("PrivateIpAddress"))
        return addresess

    def prov_result_to_host_data(self, prov_result, req):
        """Transform provisioning result to needed host data."""
        # init the dict
        result = {}

        result["id"] = prov_result.get("InstanceId")
        for tag in prov_result.get("Tags"):
            if tag["Key"] == "name":
                result["name"] = tag["Value"]  # should be one key "name"

        result["addresses"] = self.get_ip_addresses(prov_result)
        result["status"] = prov_result["State"]["Name"]
        result["os"] = prov_result.get("mrack_req").get("os")
        result["group"] = prov_result.get("mrack_req").get("group")

        return result

    async def wait_till_provisioned(self, resource):
        """Wait for AWS provisioning result."""
        aws_id, req = resource
        instance = self.ec2.Instance(aws_id)
        instance.wait_until_running()
        response = self.client.describe_instances(InstanceIds=[aws_id])
        result = {}
        try:  # returns dict with aws instance information
            result = response["Reservations"][0]["Instances"][0]
            result.update({"mrack_req": req})
        except (KeyError, IndexError) as data_err:
            raise ProvisioningError(
                "Unexpected data format in response "
                f"of provisioned instance '{req['name']}'"
            ) from data_err

        return result, req

    async def delete_host(self, host_id):
        """Delete provisioned hosts based on input from provision_hosts."""
        if not host_id:
            logger.debug(
                f"{self.dsp_name}: Skipping termination, because host was not created"
            )
            return False

        logger.info(f"{self.dsp_name}: Terminating host {host_id}")
        try:
            self.ec2.instances.filter(InstanceIds=[host_id]).terminate()
        except ClientError as error:
            logger.error(f"{self.dsp_name}: Issue while terminating host {host_id}:")
            logger.error(error.response["Error"]["Message"])
            return False
        return True
