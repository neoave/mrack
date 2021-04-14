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

"""Podman transformer module."""

from mrack.transformers.transformer import Transformer
from mrack.utils import get_host_from_metadata

CONFIG_KEY = "podman"


class PodmanTransformer(Transformer):
    """Podman transformer."""

    _config_key = CONFIG_KEY
    _required_config_attrs = [
        "images",
        "pubkey",
        "default_network",
        "podman_options",
    ]

    async def init_provider(self):
        """Initialize associate provider and transformer display name."""
        self.dsp_name = "Podman"

        await self._provider.init(
            container_images=self.config["images"].values(),
            ssh_key=self.config["pubkey"],
            default_network=self.config["default_network"],
            container_options=self.config["podman_options"],
        )

    def create_host_requirement(self, host):
        """Create single input for podman provisioner."""
        _host, domain = get_host_from_metadata(self._metadata, host["name"])
        return {
            "name": host["name"],
            "image": self._get_image(host["os"]),
            "hostname": host["name"],
            "domain": domain["name"],
        }
