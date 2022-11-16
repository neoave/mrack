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

"""AWS transformer module."""

from mrack.providers.provider import STRATEGY_ABORT
from mrack.transformers.transformer import DEFAULT_ATTEMPTS, Transformer

CONFIG_KEY = "aws"


class AWSTransformer(Transformer):
    """AWS transformer."""

    _config_key = CONFIG_KEY
    _required_config_attrs = [
        "flavors",
        "images",
        "credentials_file",
        "keypair",
        "security_groups",
        "profile",
        "instance_tags",
    ]

    async def init_provider(self):
        """Initialize associate provider and transformer display name."""
        self.dsp_name = "AWS"
        await self._provider.init(
            ssh_key=self.config["keypair"],
            instance_tags=self.config["instance_tags"],
            strategy=self.config.get("strategy", STRATEGY_ABORT),
            max_retry=self.config.get("max_retry", DEFAULT_ATTEMPTS),
        )

    def _get_security_groups(self):
        """
        Get Security Group IDs.

        Works with both single `subnet_id` definition as well as with newer
        `subnet_ids` which allows to defined multiple.
        """
        sc_ids = set(self.config.get("security_groups", []))
        sc_id = self.config.get("security_group")
        if sc_id:
            sc_ids.add(sc_id)
        return list(sc_ids)

    def _find_subnet_ids(self, host):
        """Get subnet id/s from config.

        Note: 'subnet_ids' has preference against legacy way 'subnet_id'.

        Returns: List of found subnet ids
        """
        subnet_ids = self._find_value(
            host.get(CONFIG_KEY, {}),
            "subnet_ids",
            "subnet_ids",
            host["os"],
            default=[],
        )
        subnet_id = self._find_value(
            host.get(CONFIG_KEY, {}),
            "subnet_id",
            None,
            None,
            default="",
        )

        if "subnet_ids" in host.get(CONFIG_KEY, {}):
            return subnet_ids
        if "subnet_id" in host.get(CONFIG_KEY, {}):
            return [subnet_id]
        if subnet_ids:
            return subnet_ids
        if subnet_id:
            return [subnet_id]

        return []

    def validate_host(self, host):
        """Validate host input that it contains what AWS needs."""
        super().validate_host(host)
        self.validate_ownership_and_lifetime(host)

    def create_host_requirement(self, host):
        """Create single input for AWS provisioner."""
        del_vol = self._find_value(
            host, "delete_volume_on_termination", None, None, True
        )
        req = {
            "name": host["name"],
            "os": host["os"],
            "group": host["group"],
            "flavor": self._get_flavor(host),
            "image": self._get_image(host),
            "security_group_ids": self._get_security_groups(),
            "spot": self._find_value(host, "spot", None, None),
            "delete_volume_on_termination": del_vol,
            "subnet_ids": self._find_subnet_ids(host),
        }

        req = self.update_metadata_for_owner_lifetime(req)
        return req
