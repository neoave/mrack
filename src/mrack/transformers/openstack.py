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

"""OpenStack transformer module."""
import logging
import os

from mrack.errors import ProvisioningConfigError
from mrack.providers.provider import STRATEGY_ABORT
from mrack.transformers.transformer import Transformer

logger = logging.getLogger(__name__)

CONFIG_KEY = "openstack"
DEFAULT_ATTEMPTS = 5
DEFAULT_CLOUD_PROFILE = "openstack"


class OpenStackTransformer(Transformer):
    """OpenStack transformer."""

    _config_key = CONFIG_KEY
    _required_config_attrs = [
        "flavors",
        "networks",
        "images",
        "keypair",
        "pubkey",
    ]  # List[str]

    async def init_provider(self):
        """Initialize associate provider and transformer display name."""
        self.dsp_name = "OpenStack"

        os_cloud = os.environ.get("OS_CLOUD")
        if not os_cloud:
            os_cloud = self.config.get("profile", DEFAULT_CLOUD_PROFILE)

        await self._provider.init(
            image_names=self.config["images"].values(),
            networks=self.config["networks"],
            strategy=self.config.get("strategy", STRATEGY_ABORT),
            max_retry=self.config.get("max_retry", DEFAULT_ATTEMPTS),
            cloud_profile=os_cloud,
            keypair=self.config["keypair"],
            pubkey=self.config["pubkey"],
        )

    def _get_network_type(self, host):
        """Get network type from host object definition.

        If host object doesn't have it defined, then get it from metadata or
        provisioning config.
        """
        network_type = host.get("network")
        default_network = self.config.get("default_network")
        if network_type is None:
            network_type = self._metadata.get("network", default_network)
        if not network_type:
            raise ProvisioningConfigError(
                "No network type specified and project doesn't have default "
                "network type (property 'default_network') specified in "
                "provisioning config."
            )
        return network_type

    def validate_host(self, host):
        """Validate host input that it contains what OpenStack needs."""
        super().validate_host(host)
        self.validate_ownership_and_lifetime(host)

    def create_host_requirement(self, host):
        """Create single input for OpenStack provisioner."""
        req = {
            "name": host["name"],
            "os": host["os"],
            "group": host["group"],
            "flavor": self._get_flavor(host),
            "image": self._get_image(host),
            "key_name": self.config["keypair"],
            "network": self._get_network_type(host),
        }

        # do not add this requirement at all if it is not required
        config_drive_req = self.config.get("enable_config_drive")
        if config_drive_req:
            req.update({"config_drive": config_drive_req})

        req = self.update_metadata_for_owner_lifetime(req)
        return req
