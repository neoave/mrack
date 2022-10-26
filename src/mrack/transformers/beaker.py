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
import os
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

    def _get_ks_meta(self, host):
        """
        Get `ks_meta` value from host or provisioning config or default if not defined.

        The priority is following:
            - host
            - provisioning-config.yaml
            - default from provisioning config
            - empty if not defined in provisioning config

        """
        res = self._find_value(
            host.get(CONFIG_KEY, {}),
            "ks_meta",
            "kickstart_metadata",
            host["os"],
        )
        return res

    def _construct_ks_append_script(self, ks_append, pubkeys=None):
        """Create ks_appdend from requirements."""
        if not ks_append and not pubkeys:
            return []

        res_ks_append = ["%post"]
        if pubkeys:
            ks_append += self._allow_ssh_keys(pubkeys)

        res_ks_append += ks_append

        res_ks_append.append("%end")
        return ["\n".join(res_ks_append)]

    def _allow_ssh_keys(self, pubkeys):
        """Create ssh key content to be injected to xml."""
        keys_content = []
        keys_content.append("mkdir -p /root/.ssh")
        keys_content.append('cat >>/root/.ssh/authorized_keys << "__EOF__"')
        keys_content.append("# keys added by mrack:")

        for key in set(pubkeys):
            with open(os.path.expanduser(key), "r", encoding="utf-8") as key_file:
                keys_content.append(f"{key_file.read().strip()}")

        keys_content.append("# end section of keys added by mrack")
        keys_content.append("__EOF__")
        keys_content.append("restorecon -R /root/.ssh")
        keys_content.append("chmod go-w /root /root/.ssh /root/.ssh/authorized_keys")

        return keys_content

    def _get_pubkeys(self, host):
        """Get public keys list defined per host."""
        host_beaker_config = host.get(CONFIG_KEY, {})
        pubkey = self._find_value(host_beaker_config, "pubkey", "pubkey", None, None)

        # add support for more keys defined in list
        pubkeys = self._find_value(
            host_beaker_config, "pubkeys", "pubkeys", host["os"], None
        )

        # normalize and merge them
        if not pubkeys:
            pubkeys = []
        if pubkey:
            pubkeys.append(pubkey)

        return pubkeys

    def create_host_requirement(self, host):
        """Create single input for Beaker provisioner."""
        distro, variant = self._get_distro_and_variant(host)
        specs = {
            "name": host["name"],
            "distro": distro,
            "os": host["os"],
            "group": host["group"],
            "meta_distro": "distro" in host,
            "arch": host.get("arch", "x86_64"),
            "variant": variant,
            "ks_meta": self._get_ks_meta(host),
            "retention_tag": self._find_value(
                host.get(CONFIG_KEY, {}),
                "retention_tag",
                "retention_tag",
                host["os"],
                default="audit",
            ),
            "product": self._find_value(
                host.get(CONFIG_KEY, {}),
                "product",
                "product",
                host["os"],
                default="[internal]",
            ),
            "whiteboard": self._find_value(
                host.get(CONFIG_KEY, {}),
                "whiteboard",
                "whiteboard",
                host["os"],
                default="This job has been created using mrack.",
            ),
            "priority": self._find_value(
                host.get(CONFIG_KEY, {}),
                "priority",
                "priority",
                host["os"],
                default="Normal",
            ),
            # Recipe task definition
            "tasks": self._find_value(
                host.get(CONFIG_KEY, {}),
                "tasks",
                "tasks",
                host["os"],
                default=[  # we use dummy task because beaker require a task in recipe
                    {"name": "/distribution/dummy", "role": "STANDALONE"}
                ],
            ),
            "ks_append": self._construct_ks_append_script(
                self._find_value(
                    host.get(CONFIG_KEY, {}),
                    "ks_append",
                    "ks_append",
                    host["os"],
                    default=[],
                ),
                self._get_pubkeys(host),
            ),
            # TODO: should have similar logic as _get_flavor
            "hostRequires": self._find_value(
                host.get(CONFIG_KEY, {}),
                "hostRequires",
                "hostRequires",
                host["group"],
                default=None,
            ),
            "distro_tags": self._find_value(
                host.get(CONFIG_KEY, {}),
                "distro_tags",
                "distro_tags",
                distro,
                default=[],
            ),
        }

        return specs
