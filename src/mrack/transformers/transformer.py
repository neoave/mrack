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

"""Generic Transformer."""

import logging
import typing

from mrack.errors import ConfigError, MetadataError
from mrack.providers import providers
from mrack.utils import get_config_value, object2json, validate_dict_attrs

logger = logging.getLogger(__name__)


class Transformer:
    """Base class for transformers."""

    _required_host_attrs: typing.List[str] = ["name", "os", "group"]
    _required_config_attrs: typing.List[str] = []
    _config_key = ""

    async def init(self, cfg, metadata):
        """Initialize transformer."""
        self.dsp_name = "Transformer"
        self._hosts = []
        self._config = cfg
        self._metadata = metadata
        if self._config_key:
            self.validate_config()

        self._provider = providers.get(self._config_key)
        await self.init_provider()

    async def init_provider(self):
        """Initialize associated provider."""
        pass

    @property
    def config(self):
        """Get transformer/provider configuration from provisioning configuration."""
        key = self._config_key
        try:
            return self._config[key]
        except KeyError:
            error = f"No '{key}' entry in provisioning configuration"
            raise ConfigError(error)

    @property
    def hosts(self):
        """Get all host inputs this transformer is handling."""
        return self._hosts

    def add_host(self, host):
        """Add host input."""
        self._hosts.append(host)

    def _get_image(self, os, config_key="images"):
        """
        Get image name by OS name from provisioning config.

        Returns:
            1. image by the os key
            2. default from the images if os is not found in keys
            3. os name if default is not specified for images.
        """
        image = get_config_value(self.config[config_key], os, os)
        logger.debug(
            f"{self.dsp_name}: Loaded image for {os} from {config_key}: '{image}'"
        )
        return image

    def _get_flavor(self, host):
        """Get flavor by host group."""
        # TODO: add sizes
        flavor = get_config_value(self.config["flavors"], host["group"])
        logger.debug(f"{self.dsp_name}: Loaded flavor for {host['name']}: '{flavor}'")
        return flavor

    def validate_config(self):
        """Validate provisioning configuration for this transformer/provider."""
        validate_dict_attrs(self.config, self._required_config_attrs, "config")

    def validate_host(self, host):
        """Validate host input that it contains everything needed by provider."""
        # attribute check
        validate_dict_attrs(host, self._required_host_attrs, "host")
        # provider check
        provider = host.get("provider")
        if provider and provider not in providers.names:
            raise MetadataError(
                f"{self.dsp_name}: Error: Invalid host provider: {provider}"
            )

    def create_host_requirement(self, host):
        """Create single input for provisioner."""
        raise NotImplementedError()

    def create_host_requirements(self):
        """Create inputs for all host for provisioner."""
        reqs = [self.create_host_requirement(host) for host in self.hosts]
        logger.info(f"{self.dsp_name}: Created requirement(s): {object2json(reqs)}")
        return reqs
