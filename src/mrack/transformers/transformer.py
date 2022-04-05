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
from mrack.utils import (
    find_value_in_config_hierarchy,
    get_config_value,
    object2json,
    validate_dict_attrs,
)

DEFAULT_ATTEMPTS = 1

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
        except KeyError as key_err:
            error = f"No '{key}' entry in provisioning configuration"
            raise ConfigError(error) from key_err

    @property
    def hosts(self):
        """Get all host inputs this transformer is handling."""
        return self._hosts

    def add_host(self, host):
        """Add host input."""
        self._hosts.append(host)

    def _find_value(self, host, attr, dict_name, key, default=None):
        """Find value in config hierarchy."""
        value = find_value_in_config_hierarchy(
            self._config, self._config_key, None, host, attr, dict_name, key, default
        )
        return value

    def _get_image(self, host):
        """
        Get image name by OS name from provisioning config.

        The preferred solution is to create mappings between operating system
        and image present in the provisioning config - this only allows us
        to change the providers without changing the input metadata.

        host - dictionary with server requirements

        The host dictionary can contain following attributes:
        * 'os': operating system to find mapping to image from provisioning config
        * 'image': image to use (optional)

        Returns:
            An image to be used, if mapping is not found it defaults to the host['os']
            :rtype: str
        """
        operating_system = host["os"]
        image = self._find_value(
            host, "image", "images", operating_system, default=operating_system
        )

        logger.debug(
            f"{self.dsp_name} [{host.get('name')}] Using image "
            f"{image} for {operating_system}"
        )
        return image

    def _get_flavor(self, host):
        """
        Get VM flavor from host metadata definition or based on host group.

        Get the flavor from 'size' definition in host metadata.
        If 'size' is not specified, get the flavor based on host groups
        which are defined in provisioning config.
        """
        log_msg_start = f"{self.dsp_name} [{host.get('name')}]"

        if host.get("size"):  # allow to override size by pointing to group in metadata
            flavor = get_config_value(self.config["flavors"], host["size"])
        else:  # default action based on host group define the flavor of instance
            flavor = get_config_value(self.config["flavors"], host["group"])

        logger.debug(f"{log_msg_start} Loaded flavor '{flavor}'")
        return flavor

    def validate_config(self):
        """Validate provisioning configuration for this transformer/provider."""
        validate_dict_attrs(self.config, self._required_config_attrs, "config")

    def validate_host(self, host):
        """Validate host input that it contains everything needed by provider."""
        log_msg_start = f"{self.dsp_name} [{host.get('name')}]"
        # attribute check
        validate_dict_attrs(host, self._required_host_attrs, "host")
        # provider check
        provider = host.get("provider")

        if provider and provider not in providers.names:
            raise MetadataError(
                f"{log_msg_start} Error: Invalid host provider: {provider}"
            )

    def create_host_requirement(self, host):
        """Create single input for provisioner."""
        raise NotImplementedError()

    def create_host_requirements(self):
        """Create inputs for all host for provisioner."""
        reqs = [self.create_host_requirement(host) for host in self.hosts]
        logger.info(f"{self.dsp_name} Created requirement(s): {object2json(reqs)}")
        return reqs
