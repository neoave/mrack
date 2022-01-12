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
        }
        if self.config.get("subnet_id"):
            req["subnet_id"] = self.config.get("subnet_id")
        return req
