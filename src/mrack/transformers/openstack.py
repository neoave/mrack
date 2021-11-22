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

from mrack.errors import ProvisioningConfigError
from mrack.providers.provider import STRATEGY_ABORT
from mrack.transformers.transformer import Transformer

logger = logging.getLogger(__name__)

CONFIG_KEY = "openstack"
DEFAULT_ATTEMPTS = 5


class OpenStackTransformer(Transformer):
    """OpenStack transformer."""

    _config_key = CONFIG_KEY
    _required_config_attrs = ["flavors", "networks", "images", "keypair"]  # List[str]

    def _get_cluster(self):
        """
        Get cluster name.

        Get cluster name from metadata if specified
        if not specified return default_cluster_name
        """
        for domain in self._metadata["domains"]:
            for host in domain["hosts"]:
                if CONFIG_KEY in host:
                    return host[CONFIG_KEY]["cluster"]

        return self.config.get("default_cluster_name")

    async def init_provider(self):
        """Initialize associate provider and transformer display name."""
        self.dsp_name = "OpenStack"

        cluster = self._get_cluster()
        # if cluster is not empty this feature is already being used.
        if cluster:
            # extract default openstack config from the config dictionary
            default_config = {
                x: self.config.get(x)
                for x in self.config
                if x in self._required_config_attrs
            }
            # store the cluster config
            cluster_config = self.config.get(cluster, {})

            # extend default config with cluster configuration by overriding defaults
            self.config = default_config | cluster_config

        await self._provider.init(
            image_names=self.config["images"].values(),
            networks=self.config["networks"],
            strategy=self.config.get("strategy", STRATEGY_ABORT),
            max_retry=self.config.get("max_retry", DEFAULT_ATTEMPTS),
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

    def create_host_requirement(self, host):
        """Create single input for OpenStack provisioner."""
        required_image = host.get("image") or self._get_image(host["os"])
        req = {
            "name": host["name"],
            "os": host["os"],
            "group": host["group"],
            "flavor": self._get_flavor(host),
            "image": required_image,
            "key_name": self.config["keypair"],
            "network": self._get_network_type(host),
        }

        # do not add this requirement at all if it is not required
        config_drive_req = self.config.get("enable_config_drive")
        if config_drive_req:
            req.update({"config_drive": config_drive_req})

        return req
