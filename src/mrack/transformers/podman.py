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
from mrack.utils import get_config_value, print_obj

CONFIG_KEY = "podman"


class PodmanTransformer(Transformer):
    """Podman transformer."""

    _config_key = CONFIG_KEY
    _required_config_attrs = [
        "images",
    ]

    def _get_image(self, os):
        """Get image name by OS name from provisioning config."""
        return get_config_value(self.config["images"], os)

    def create_host_requirement(self, host):
        """Create single input for podman provisioner."""
        return {
            "name": host["name"],
            "image": self._get_image(host["os"]),
            "hostname": host["name"],
        }

    def create_host_requirements(self):
        """Create inputs for all host for AWS provisioner."""
        reqs = [self.create_host_requirement(host) for host in self.hosts]
        print_obj(reqs)
        return reqs
