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

"""Beaker transformer module."""
import re

from mrack.transformers.transformer import Transformer

CONFIG_KEY = "beaker"


class BeakerTransformer(Transformer):
    """Beaker transformer."""

    _config_key = CONFIG_KEY
    _required_config_attrs = [
        "distros",
        "pubkey",
        "reserve_duration",
        "max_attempts",
    ]  # List[str]

    async def init_provider(self):
        """Initialize associate provider and transformer display name."""
        self.dsp_name = "Beaker"
        await self._provider.init(
            distros=self.config["distros"].values(),
            max_attempts=self.config["max_attempts"],
            reserve_duration=self.config["reserve_duration"],
            pubkey=self.config["pubkey"],
        )

    def _get_bkr_variant(self, host):
        """Get variant for the host system to reqirement."""
        if "beaker_variant" in host:
            variant = host["beaker_variant"]
        elif re.match(r"(rhel-8)", host["os"]):
            variant = "BaseOS"
        else:  # Default to Server for RHEL7 and Fedora systems
            variant = "Server"
        return variant

    def create_host_requirement(self, host):
        """Create single input for Beaker provisioner."""
        required_distro = host.get("distro") or self._get_image(
            host["os"], config_key="distros"
        )
        return {
            "name": host["name"],
            "distro": required_distro,
            "meta_distro": "distro" in host,
            "arch": host.get("arch", "x86_64"),
            "variant": self._get_bkr_variant(host),
        }
