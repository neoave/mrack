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

"""Static transformer module."""
import typing
from copy import deepcopy

from mrack.transformers.transformer import Transformer

CONFIG_KEY = "static"


class StaticTransformer(Transformer):
    """
    Static transformer.

    Does almost no operation as there is nothing to provision.
    """

    _config_key = CONFIG_KEY
    _required_config_attrs: typing.List[str] = []
    _required_host_attrs = ["name", "os", "group", "ip"]

    def create_host_requirement(self, host):
        """Create single input for Static provisioner."""
        self.dsp_name = "Static"
        return deepcopy(host)
