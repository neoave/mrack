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
import logging
import secrets
from copy import deepcopy
from datetime import datetime
from random import shuffle

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
        super().__init__()
        self._name = PROVISIONER_KEY
        self.dsp_name = "AWS"
        self.ssh_key = None
        self.instance_tags = None
        self.max_retry = 1  # for retry strategy
        self.subnets_capacity = {}
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
        log_msg_start = self.dsp_name
        logger.info(f"{log_msg_start} Initializing provider")
        login_start = datetime.now()
        self.strategy = strategy
        self.max_retry = max_retry
        try:
            self.ec2 = boto3.resource("ec2")
            self.client = boto3.client("ec2")
        except (NoRegionError, NoCredentialsError) as c_err:
            logger.debug(
                f"{log_msg_start} Failed loading credentials file with: {str(c_err)}"
            )
            raise NotAuthenticatedError(
                f"{log_msg_start} failed loading credentials. Load AWS credentials"
                " and try again. E.g.: $ export AWS_CONFIG_FILE=~/aws.key"
            ) from c_err

        self.amis = []
        self.ssh_key = ssh_key
        self.instance_tags = instance_tags
        login_end = datetime.now()
        login_duration = login_end - login_start
        logger.info(f"{log_msg_start} Login duration {login_duration}")

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

        Does also basic image definition validation.

        Return None if image is not yet loaded.
        """
        log_msg_start = f"{self.dsp_name} [{req.get('name')}]"
        image_def = req.get("image")

        if not image_def:
            raise ValidationError(f"{log_msg_start} Host doesn't have image defined.")

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
                f"{log_msg_start} Invalid image "
                f"definition. Must be 'tags' definition or AMI ID"
            )
        return None

    def load_image(self, req):
        """
        Load AMI information from EC2 based on image requirement.

        If more images match the search then the newest is returned.

        Raises validation error if no image is found.
        """
        log_msg_start = f"{self.dsp_name} [{req.get('name')}]"
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
            raise ValidationError(f"{log_msg_start} Cannot find image for host")

        amis.sort(key=lambda ami: parser.parse(ami.creation_date), reverse=True)
        self.amis.append(amis[0])
        return amis[0]

    def load_images(self, reqs):
        """
        Load AMI images for all requirements.

        Done sequentially, already loaded images are not loaded again. Basically also
        validates that images are available and that their definition is correct.
        """
        for req in reqs:
            ami = self.get_image(req)
            if not ami:
                self.load_image(req)

    async def prepare_provisioning(self, reqs):
        """Prepare provisioning."""
        try:
            self.load_images(reqs)
        except ValidationError as val_err:
            logger.error(val_err)
            return False

        return bool(reqs)

    async def validate_hosts(self, reqs):
        """Validate that host requirements are well specified."""
        return

    async def get_subnet_available_ips(self, subnet_id, log_msg_start):
        """Get number of IPs available in a subnet."""
        try:
            subnet = self.ec2.Subnet(subnet_id)
        except ClientError:
            logger.warning(
                f"{log_msg_start} Error retrieving info from subnet: {subnet_id}"
            )
            return 0

        logger.debug(f"{log_msg_start} Subnet {subnet_id}")
        logger.debug(
            f"{log_msg_start}   available: {subnet.available_ip_address_count}"
        )

        return subnet.available_ip_address_count

    async def can_provision(self, hosts):  # pylint: disable=too-many-branches
        """Check that all host can be provisioned.

        Checks:
        * Available IPv4 addresses are enough
        """
        log_msg_start = self.dsp_name

        ip_availabilities = {}  # Dict for storing available IPs in every subnet
        single_subnet_prov = []  # List for storing provided single subnets
        mult_subnets_prov = []  # List for storing lists of provided multiple subnets

        # For all hosts, get subnets in dict (with no repetitions) and list of
        # provided single & multiple subnets
        for host in hosts:
            subnet_ids = host.get("subnet_ids")
            if subnet_ids:
                if len(subnet_ids) == 1:
                    single_subnet_prov.append(subnet_ids[0])
                    if subnet_ids[0] not in ip_availabilities:
                        ip_availabilities[subnet_ids[0]] = 0
                else:
                    mult_subnets_prov.append(subnet_ids)
                    for subnet_id in subnet_ids:
                        if subnet_id not in ip_availabilities:
                            ip_availabilities[subnet_id] = 0
            else:
                logger.debug(
                    f"{log_msg_start} No subnet/s specified for host {host['name']}."
                )

        # Get available IPs from AWS for every subnet
        logger.info(f"{log_msg_start} Checking IP availability")
        ips_count_wait = [
            self.get_subnet_available_ips(subnet_id, log_msg_start)
            for subnet_id in ip_availabilities
        ]
        ips_count_result = await asyncio.gather(*ips_count_wait)
        ip_availabilities = dict(zip(ip_availabilities, ips_count_result))

        self.subnets_capacity = ip_availabilities.copy()

        # Discount hosts with single subnet specified from available IPs
        for subnet_id in single_subnet_prov:
            if ip_availabilities[subnet_id] > 0:
                ip_availabilities[subnet_id] -= 1
            else:
                logger.info(
                    f"{log_msg_start} Not enougn IP addresses available "
                    f"in subnet: {subnet_id}"
                )
                return False

        # Discount hosts with multiple subnets specified from available IPs
        for subnet_ids in mult_subnets_prov:
            for subnet_id in subnet_ids:
                if ip_availabilities[subnet_id] > 0:
                    ip_availabilities[subnet_id] -= 1
                    break
            else:
                logger.info(
                    f"{log_msg_start} Not enougn IP addresses available "
                    f"in subnet/s: {subnet_ids}"
                )
                return False

        return True

    async def utilization(self):
        """Check percentage utilization of given provider."""
        net_sizes = {
            "28": 14,
            "27": 30,
            "26": 62,
            "25": 126,
            "24": 254,
            "23": 510,
        }
        res = 0
        for net, _availability in self.subnets_capacity.items():
            subnet = self.ec2.Subnet(net)
            size = net_sizes[subnet.cidr_block.split("/")[-1]]
            self.subnets_capacity[net] = subnet.available_ip_address_count
            usage = (size - self.subnets_capacity[net]) / size * 100
            res = usage if usage > res else res

        return res

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
        log_msg_start = f"{self.dsp_name} [{req['name']}]"
        logger.info(f"{log_msg_start} Creating server")
        specs = deepcopy(req)  # work with own copy, do not modify the input

        del_vol = specs.get("delete_volume_on_termination", True)

        name = req.get("name")
        # creating unique name for instance (visible in aws ec2 WebUI)
        taglist = [{"Key": "Name", "Value": name}]
        taglist.append(
            {
                "Key": "Hostname",
                "Value": f"{name.split('.')[0]}-{secrets.token_hex()[:6]}",
            }
        )

        for key, value in self.instance_tags.items():
            taglist.append({"Key": key, "Value": value})

        if specs.get("metadata"):
            for key, value in specs.get("metadata").items():
                taglist.append({"Key": key, "Value": value})

        logger.debug(f"{log_msg_start} Tagging instance with: {object2json(taglist)}")

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
            "TagSpecifications": [{"ResourceType": "instance", "Tags": taglist}],
        }

        subnet_ids = specs.get("subnet_ids")
        if subnet_ids:
            shuffle(subnet_ids)  # Randomize subnets order
            for subnet_id in subnet_ids:
                if self.subnets_capacity[subnet_id] > 0:
                    self.subnets_capacity[subnet_id] -= 1
                    request["SubnetId"] = subnet_id
                    break
            if not request["SubnetId"]:
                raise ProvisioningError(
                    f"There are no subnets with IPs available"
                    f"for use from {subnet_ids}",
                    req,
                )
        else:
            logger.warning(f"{log_msg_start} No subnet/s specified. Using default...")

        if specs.get("spot"):
            request["InstanceMarketOptions"] = {
                "MarketType": "spot",
            }

        try:
            aws_res = self.ec2.create_instances(**request)
        except ClientError as creation_error:
            err_msg = (
                f"{log_msg_start} Requested image "
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

        # returns id of provisioned instance and required host name
        return (ids[0], req)

    def get_ip_addresses(self, prov_result):
        """Get IP address from a provisioning result."""
        addresses = []
        if prov_result.get("PublicIpAddress"):
            addresses.append(prov_result.get("PublicIpAddress"))
        if prov_result.get("PrivateIpAddress"):
            addresses.append(prov_result.get("PrivateIpAddress"))
        return addresses

    def prov_result_to_host_data(self, prov_result, req):
        """Transform provisioning result to needed host data."""
        # init the dict
        result = {}

        result["id"] = prov_result.get("InstanceId")
        for tag in prov_result.get("Tags"):
            if tag["Key"] == "Name":
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

    async def delete_host(self, host_id, host_name):
        """Delete provisioned hosts based on input from provision_hosts."""
        log_msg_start = f"{self.dsp_name} [{host_name}]"
        if not host_id:
            logger.debug(
                f"{log_msg_start} Skipping termination, because host was not created"
            )
            return False

        logger.info(f"{log_msg_start} Terminating host with ID {host_id}")
        try:
            self.ec2.instances.filter(InstanceIds=[host_id]).terminate()
        except ClientError as error:
            logger.error(f"{log_msg_start} Issue while terminating host {host_id}:")
            logger.error(error.response["Error"]["Message"])
            return False
        return True
