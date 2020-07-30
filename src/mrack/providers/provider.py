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

"""General Provider interface."""


class Provider:
    """General Provider interface."""

    def __init__(self, provisioning_config, job_config):
        """Initialize provider."""
        self._name = "dummy"
        return

    @property
    def name(self):
        """Get provider name."""
        return self._name

    async def validate_hosts(self, hosts):
        """Validate that host requirements are well specified."""
        return

    async def can_provision(self, hosts):
        """Check that provider has enough resources to provison hosts."""
        raise NotImplementedError()

    async def provision_hosts(self, hosts):
        """Provision hosts and wait for it to finish."""
        raise NotImplementedError()

    async def delete_hosts(self, provisioning_results):
        """Delete provisioned hosts based on input from provision_hosts."""
        raise NotImplementedError()
