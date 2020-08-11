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
from mrack.utils import get_config_value, print_obj

CONFIG_KEY = "beaker"


class BeakerTransformer(Transformer):
    """Beaker transformer."""

    _config_key = CONFIG_KEY
    _required_config_attrs = ["distros", "keypair", "reserve_duration", "max_attempts"]

    async def init_provider(self):
        """Initialize associate provider."""
        await self._provider.init(self.config)

    def _get_distro(self, os):
        """Get distro string by OS name from provisioning config."""
        return get_config_value(self.config["distros"], os)

    def _get_variant(self, host):
        if "beaker_variant" in host:
            variant = host["beaker_variant"]
        elif re.match(r"(rhel-8)", host["os"]):
            variant = "BaseOS"
        else:  # Default to Server for RHEL7 and Fedora systems
            variant = "Server"
        return variant

    def create_host_requirement(self, host):
        """Create single input for Beaker provisioner."""
        return {
            "name": host["name"],
            "distro": self._get_distro(host["os"]),
            "arch": host.get("arch", "x86_64"),
            "variant": self._get_variant(host)
        }

    def create_host_requirements(self):
        """Create inputs for all host for Beaker provisioner."""
        reqs = [self.create_host_requirement(host) for host in self.hosts]
        print_obj(reqs)
        return reqs
