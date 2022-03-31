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

from mrack.providers.provider import STRATEGY_ABORT
from mrack.transformers.transformer import Transformer

CONFIG_KEY = "beaker"
DEFAULT_ATTEMPTS = 2


class BeakerTransformer(Transformer):
    """Beaker transformer."""

    _config_key = CONFIG_KEY
    _required_config_attrs = [
        "distros",
        "pubkey",
        "reserve_duration",
        "timeout",
    ]  # List[str]

    async def init_provider(self):
        """Initialize associate provider and transformer display name."""
        self.dsp_name = "Beaker"
        await self._provider.init(
            distros=self.config["distros"].values(),
            timeout=self.config["timeout"],
            reserve_duration=self.config["reserve_duration"],
            pubkey=self.config["pubkey"],
            strategy=self.config.get("strategy", STRATEGY_ABORT),
            max_retry=self.config.get("max_retry", DEFAULT_ATTEMPTS),
        )

    def _get_distro_and_variant(self, host):
        """Get distribution and its variant for the host system to requirement."""
        required_distro = self._find_value(
            host, "distro", "distros", host["os"], default=host["os"]
        )
        distro_variants = self.config.get("distro_variants")

        if "beaker_variant" in host:
            variant = host["beaker_variant"]
        elif distro_variants:
            variant = distro_variants.get(
                required_distro, distro_variants.get("default")
            )
        # keep this elif for backward compatibility wit mrack <= 1.2.0
        elif re.match(r"(rhel-[8|9])", host["os"]):
            variant = "BaseOS"
        else:  # Default to Server for RHEL7 and Fedora systems
            variant = "Server"

        return (required_distro, variant)

    def create_host_requirement(self, host):
        """Create single input for Beaker provisioner."""
        distro, variant = self._get_distro_and_variant(host)
        return {
            "name": host["name"],
            "distro": distro,
            "os": host["os"],
            "group": host["group"],
            "meta_distro": "distro" in host,
            "arch": host.get("arch", "x86_64"),
            "variant": variant,
            f"mrack_{CONFIG_KEY}": host.get(CONFIG_KEY, {}),
        }
