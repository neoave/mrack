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
from unittest import mock
from unittest.mock import Mock, patch

import pytest

from mrack.providers.openstack import OpenStackProvider

from .utils import get_data  # FIXME do not use relative import


def AsyncMock(*args, **kwargs):
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


class TestOpenStackProvider:
    def setup(self):
        self.limits = get_data("limits.json")
        self.flavors = get_data("flavors.json")
        self.images = get_data("images.json")
        self.availabilities = get_data("network_availabilities.json")
        self.networks = get_data("networks.json")

        self.auth_patcher = patch("mrack.providers.openstack.AuthPassword")
        self.mock_auth = self.auth_patcher.start()

        self.mock_nova = Mock()
        self.mock_nova.init_api = AsyncMock(return_value=True)
        self.mock_nova.limits.show = AsyncMock(return_value=self.limits)
        self.mock_nova.flavors.list = AsyncMock(return_value=self.flavors)

        self.mock_nova_class = Mock(return_value=self.mock_nova)
        self.nova_patcher = patch(
            "mrack.providers.openstack.ExtraNovaClient", new=self.mock_nova_class
        )
        self.nova_patcher.start()

        self.mock_neutron = Mock()
        self.mock_neutron.init_api = AsyncMock(return_value=True)
        self.mock_neutron.network.list = AsyncMock(return_value=self.networks)
        self.mock_neutron.ip.list = AsyncMock(return_value=self.availabilities)

        self.mock_neutron_class = Mock(return_value=self.mock_neutron)
        self.neutron_patcher = patch(
            "mrack.providers.openstack.NeutronClient", new=self.mock_neutron_class
        )
        self.neutron_patcher.start()

        self.mock_glance = Mock()
        self.mock_glance.init_api = AsyncMock(return_value=True)
        self.mock_glance.images.list = AsyncMock(return_value=self.images)

        self.mock_glance_class = Mock(return_value=self.mock_glance)
        self.glance_patcher = patch(
            "mrack.providers.openstack.GlanceClient", new=self.mock_glance_class
        )
        self.glance_patcher.start()

    def teardown(self):
        mock.patch.stopall()

    @pytest.mark.asyncio
    async def test_init_provider(self):
        provider = OpenStackProvider()
        await provider.init(image_names=[])

        # Provider loaded networks
        for network in self.networks["networks"]:
            name = network["name"]
            uuid = network["id"]
            net = provider.get_network(name)
            assert net["id"] == uuid
            net = provider.get_network(ref=uuid)
            assert net["name"] == name

        # Provider loaded images
        for image in self.images["images"]:
            name = image["name"]
            uuid = image["id"]
            im = provider.get_image(name)
            assert im["id"] == uuid
            im = provider.get_image(ref=uuid)
            assert im["name"] == name

        # Provider loaded flavors
        for flavor in self.flavors["flavors"]:
            name = flavor["name"]
            uuid = flavor["id"]
            fla = provider.get_flavor(name)
            assert fla["id"] == uuid
            fla = provider.get_flavor(ref=uuid)
            assert fla["name"] == name

        # Provider loaded limits
        limits = provider.limits
        for key in self.limits:
            assert self.limits[key] == limits[key]

        # Provider loaded IP availabilities
        for net_ava in self.availabilities["network_ip_availabilities"]:
            name = net_ava["network_name"]
            uuid = net_ava["network_id"]
            net = provider.get_ips(name)
            assert net["network_id"] == uuid
            net = provider.get_ips(ref=uuid)
            assert net["network_name"] == name

    @pytest.mark.asyncio
    async def test_provision(self):
        provider = OpenStackProvider()
        await provider.init(image_names=[])
