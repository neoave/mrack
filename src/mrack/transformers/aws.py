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

"""AWS transformer module."""

from mrack.transformers.transformer import Transformer
from mrack.utils import get_config_value, print_obj

CONFIG_KEY = "aws"


class AWSTransformer(Transformer):
    """AWS transformer."""

    _config_key = CONFIG_KEY
    _required_config_attrs = [
        "flavors",
        "images",
        "credentials_file",
        "keypair",
        "security_group",
        "profile",
        "instance_tags",
    ]

    async def init_provider(self):
        """Initialize associate provider."""
        await self._provider.init(
            ami_ids=self.config["images"].values(),
            ssh_key=self.config["keypair"],
            sec_group=self.config["security_group"],
            instance_tags=self.config["instance_tags"],
        )

    def _get_flavor(self, host):
        """Get flavor by host group."""
        # TODO: add sizes

        return get_config_value(self.config["flavors"], host["group"])

    def _get_image(self, os):
        """
        Get image name by OS name from provisioning config.

        Returns:
            1. image by the os key
            2. default from the images if os is not found in keys
            3. os name if default is not specified for images.
        """
        return get_config_value(self.config["images"], os, os)

    def create_host_requirement(self, host):
        """Create single input for AWS provisioner."""
        required_image = host.get("image") or self._get_image(host["os"])
        return {
            "name": host["name"],
            "flavor": self._get_flavor(host),
            "image": required_image,
            "meta_image": "image" in host,
            "restraint_id": host.get("restraint_id"),
        }

    def create_host_requirements(self):
        """Create inputs for all host for AWS provisioner."""
        reqs = [self.create_host_requirement(host) for host in self.hosts]
        print_obj(reqs)
        return reqs
