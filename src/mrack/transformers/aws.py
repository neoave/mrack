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
        "security_group",
        "profile",
        "instance_tags",
    ]

    async def init_provider(self):
        """Initialize associate provider and transformer display name."""
        self.dsp_name = "AWS"
        await self._provider.init(
            ami_ids=self.config["images"].values(),
            ssh_key=self.config["keypair"],
            sec_group=self.config["security_group"],
            instance_tags=self.config["instance_tags"],
            strategy=self.config.get("strategy", STRATEGY_ABORT),
            max_retry=self.config.get("max_retry", DEFAULT_ATTEMPTS),
        )

    def create_host_requirement(self, host):
        """Create single input for AWS provisioner."""
        required_image = host.get("image") or self._get_image(host["os"])
        return {
            "name": host["name"],
            "os": host["os"],
            "group": host["group"],
            "flavor": self._get_flavor(host),
            "image": required_image,
            "meta_image": "image" in host,
        }
