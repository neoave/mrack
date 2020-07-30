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

"""Module to work with provisioning config.

Provisioning config is general project configuration shared between multiple jobs
"""


class ProvisioningConfig:
    """Represents loaded provisioning configuration."""

    def __init__(self, data):
        """Initialize provisioning configuration."""
        self._raw = data

    def raw(self):
        """Get raw configuration."""
        return self._raw()

    def __getitem__(self, key):
        """Get item from raw representation."""
        return self._raw[key]

    def get(self, key, default=None):
        """Get method as in dict for raw config."""
        return self._raw.get(key, default)
