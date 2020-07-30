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

from mrack.errors import ConfigError, MetadataError
from mrack.providers import providers
from mrack.utils import validate_dict_attrs


class Transformer:
    """Base class for transformers."""

    _required_host_attrs = ["name", "os", "group"]
    _required_config_attrs = []
    _config_key = None

    async def init(self, cfg, metadata):
        """Initialize transformer."""
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
            raise MetadataError(f"Error: Invalid host provider: {provider}")
