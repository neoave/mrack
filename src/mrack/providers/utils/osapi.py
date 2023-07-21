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

"""Additional client API wrappers for OpenStack."""

from asyncopenstackclient import NovaClient
from asyncopenstackclient.client import Client


class ExtraNovaClient(NovaClient):
    """Extension of NovaClient to provide additional methods.

    Added methods:
    * limits.show
    * quota.show
    * usage.show
    * keypairs.show
    * keypairs.create
    """

    def __init__(self, session=None, api_url=None):
        """Add new objects."""
        super().__init__(session, api_url)
        self.resources.extend(["limits", "quota", "usage", "keypairs"])

    async def init_api(self, timeout=60):
        """Initialize API.

        to add additional methods
        """
        await super().init_api(timeout)
        self.api.limits.actions["show"] = {"method": "GET", "url": "limits"}
        self.api.quota.actions["show"] = {"method": "GET", "url": "os-quota-sets/{}"}
        self.api.usage.actions["show"] = {
            "method": "GET",
            "url": "os-simple-tenant-usage/{}",
        }
        self.api.keypairs.actions["show"] = {"method": "GET", "url": "os-keypairs/{}"}
        self.api.keypairs.actions["create"] = {"method": "POST", "url": "os-keypairs"}
        self.api.limits.add_action("show")
        self.api.quota.add_action("show")
        self.api.usage.add_action("show")
        self.api.keypairs.add_action("show")
        self.api.keypairs.add_action("create")


class NeutronClient(Client):
    """Client API for working with Neutron (Networks).

    Available methods:
    * network.list - get all networks
    * ip.list - get network availibilities
    """

    def __init__(self, session=None, api_url=None):
        """Add new objects."""
        super().__init__("neutron", ["network", "ip"], session, api_url)

    async def init_api(self, timeout=60):
        """Initialize API.

        to add additional methods
        """
        await super().init_api(timeout)
        self.api.network.actions["list"] = {"method": "GET", "url": "networks"}
        self.api.ip.actions["list"] = {
            "method": "GET",
            "url": "network-ip-availabilities",
        }
        self.api.network.add_action("list")
        self.api.ip.add_action("list")
