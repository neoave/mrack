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
import asyncio
import os
from copy import deepcopy
from unittest import mock
from unittest.mock import Mock, patch

import pytest
from simple_rest_client.exceptions import ServerError

from mrack.context import global_context
from mrack.errors import (
    MrackError,
    ProviderNotExists,
    ProvisioningError,
    ValidationError,
)
from mrack.providers.openstack import OpenStackProvider

from .mock_networks import (
    mock_network_ip_availabilities,
    mock_networks_from_availabilities,
    mock_pools,
)
from .utils import get_data  # FIXME do not use relative import


def hostX(x):
    return {
        "name": f"host{x}.mrack.test",
        "os": "fedora-latest",
        "group": "ipaclient",
        "flavor": "ci.standard.xs",
        "image": "idm-Fedora-Cloud-Base-37-latest",
        "key_name": "idm-jenkins",
        "network": "IPv4",
        "config_drive": True,
    }


def host1():
    return hostX(1)


def host2():
    return hostX(2)


def host3():
    return hostX(3)


def net_availability(network_name, total_ips, used_ips, ip_version):
    return {
        "network": network_name,
        "total": total_ips,
        "used": used_ips,
        "version": ip_version,
    }


def init_global_context(mrack_conf="mrack.conf"):
    try:
        global_context.init(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                f"conf/{mrack_conf}",
            ),
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "conf/provisioning-config.yaml",
            ),
        )
    except ProviderNotExists:
        assert global_context.CONFIG is not None


def assert_global_network_config(spread, utilization):
    """
    Check that network allocation settings in global config are set as expected.
    """
    assert isinstance(global_context.CONFIG.usable_network_threshold, int)
    assert global_context.CONFIG.network_spread == spread
    assert global_context.CONFIG.usable_network_threshold == utilization


def assert_network_alloc_exception(expected, raised, hosts):
    """
    Check that allocation of networks raises excepted exception
    """
    assert isinstance(expected, ValidationError), f"Unexpected exception: {raised}"
    assert str(expected).lower() in str(raised).lower(), "Unexpected exception string"
    assert str(len(hosts)) in str(raised)


def assert_network_allocation(hosts, reqs, pools, expected):
    assert len(hosts) == len(reqs)

    allocation = [h["network"] for h in hosts]

    for i, host in enumerate(hosts):
        assert host != reqs[i]
        picked = host["network"]
        assert picked in pools.get(reqs[i]["network"])
        if "OR" in expected[i]:
            assert (
                picked in expected[i]
            ), f"host: '{i}', expected: '{expected[i]}'. Allocation: {allocation}"
        else:
            assert (
                picked == expected[i]
            ), f"host: '{i}', expected: '{expected[i]}'. Allocation: {allocation}"

    return allocation


def AsyncMock(*args, **kwargs):
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


class TestOpenStackProvider:
    def setup_method(self):
        self.limits = get_data("limits.json")
        self.flavors = get_data("flavors.json")
        self.images = get_data("images.json")
        self.availabilities = get_data("network_availabilities.json")
        self.network_pools = get_data("network_pools.json")
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

    def teardown_method(self):
        mock.patch.stopall()

    def mock_osp_network_calls(self, availabilities, networks):
        del self.mock_neutron
        self.mock_neutron = Mock()
        self.mock_neutron.init_api = AsyncMock(return_value=True)
        self.mock_neutron.network.list = AsyncMock(return_value=networks)
        self.mock_neutron.ip.list = AsyncMock(return_value=availabilities)

        self.mock_neutron_class = Mock(return_value=self.mock_neutron)
        self.neutron_patcher = patch(
            "mrack.providers.openstack.NeutronClient", new=self.mock_neutron_class
        )
        self.neutron_patcher.start()

    @pytest.mark.asyncio
    async def test_init_provider(self):
        provider = OpenStackProvider()
        await provider.init(image_names=[])

        # Provider loaded networks
        for network in self.networks["networks"]:
            name = network["name"]
            uuid = network["id"]
            net = provider._get_network(name)  # pylint: disable=protected-access
            assert net["id"] == uuid
            net = provider._get_network(ref=uuid)  # pylint: disable=protected-access
            assert net["name"] == name

        # Provider loaded images
        for image in self.images["images"]:
            name = image["name"]
            uuid = image["id"]
            im = provider._get_image(name)  # pylint: disable=protected-access
            assert im["id"] == uuid
            im = provider._get_image(ref=uuid)  # pylint: disable=protected-access
            assert im["name"] == name

        # Provider loaded flavors
        for flavor in self.flavors["flavors"]:
            name = flavor["name"]
            uuid = flavor["id"]
            fla = provider._get_flavor(name)  # pylint: disable=protected-access
            assert fla["id"] == uuid
            fla = provider._get_flavor(ref=uuid)  # pylint: disable=protected-access
            assert fla["name"] == name

        # Provider loaded limits
        limits = provider.limits
        for key in self.limits:
            assert self.limits[key] == limits[key]

        # Provider loaded IP availabilities
        for net_ava in self.availabilities["network_ip_availabilities"]:
            name = net_ava["network_name"]
            uuid = net_ava["network_id"]
            net = provider._get_ips(name)  # pylint: disable=protected-access
            assert net["network_id"] == uuid
            net = provider._get_ips(ref=uuid)  # pylint: disable=protected-access
            assert net["network_name"] == name

    @pytest.mark.asyncio
    async def test_provision(self):
        provider = OpenStackProvider()
        await provider.init(image_names=[])

    async def translate_network_types_test_core(
        self, x, mrack_conf, spread, utilization
    ):
        hosts = x["hosts"]
        reqs = deepcopy(hosts)
        availabilities_data = x["availabilities_data"]
        expected = x["expected"]

        availabilities = mock_network_ip_availabilities(availabilities_data)
        networks = mock_networks_from_availabilities(availabilities)
        pools = mock_pools(availabilities)
        self.mock_osp_network_calls(availabilities, networks)

        init_global_context(mrack_conf)
        assert_global_network_config(spread, utilization)
        provider = OpenStackProvider()
        await provider.init(image_names=[], networks=pools)

        try:
            provider._translate_network_types(hosts)  # pylint: disable=protected-access
        except MrackError as raised:
            assert_network_alloc_exception(expected, raised, hosts)
            return raised

        allocation = assert_network_allocation(hosts, reqs, pools, expected)

        unique = x.get("unique_network_count", 1)
        assert (
            len(set(allocation)) == unique
        ), f"Number of unique networks in allocation should be {unique}"

    network_spread_data = [
        {
            "name": "prefer_single_from_all",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                # way below treshold, prefers single network
                net_availability("net1", 100, 50, 4),
                net_availability("net2", 100, 51, 4),
                net_availability("net3", 100, 52, 4),
            ],
            "expected": [
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
            ],
        },
        {
            "name": "prefer_single_from_first_2",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                # way below treshold, prefers single network
                net_availability("net1", 100, 51, 4),
                net_availability("net2", 100, 50, 4),
                net_availability("net3", 100, 96, 4),
            ],
            "expected": [
                "net1 OR net2",
                "net1 OR net2",
                "net1 OR net2",
            ],
        },
        {
            "name": "spread_between_first_2",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                # all over treshold, spreads the networks equally
                net_availability("net1", 100, 97, 4),
                net_availability("net2", 100, 96, 4),
                net_availability("net3", 100, 99, 4),
            ],
            "expected": ["net2", "net2", "net1"],
            "unique_network_count": 2,
        },
        {
            "name": "equal_spread",
            # in this case each host will have different network
            # however the algorithm randomizes their order
            # so we can not tell in which order hosts
            # will get the network assigned.
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                # all over threshold, spreads the networks equally
                # when networks are equally
                net_availability("net1", 100, 96, 4),
                net_availability("net2", 100, 96, 4),
                net_availability("net3", 100, 96, 4),
            ],
            "expected": [
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
            ],
            "unique_network_count": 3,
        },
        {
            "name": "picks_single_almost_full",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 97, 4),
                net_availability("net2", 100, 100, 4),
            ],
            "expected": ["net1", "net1", "net1"],
        },
        {
            "name": "spread_in_usable",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 98, 4),
                net_availability("net2", 100, 100, 4),
                net_availability("net3", 100, 98, 4),
            ],
            "expected": [
                "net1 OR net3",
                "net1 OR net3",
                "net1 OR net3",
            ],
            "unique_network_count": 2,
        },
        {
            "name": "no_aval",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 99, 4),
                net_availability("net2", 100, 100, 4),
                net_availability("net3", 100, 99, 4),
            ],
            "expected": ValidationError("No available networks"),
        },
        {
            "name": "can_fit",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 99, 4),
                net_availability("net2", 100, 100, 4),
                net_availability("net3", 100, 98, 4),
            ],
            "expected": ["net3", "net3", "net1"],
            "unique_network_count": 2,
        },
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "x", network_spread_data, ids=[x["name"] for x in network_spread_data]
    )
    async def test_network_picking_default_allow_spread(self, x):
        await self.translate_network_types_test_core(x, "mrack.conf", "allow", 95)

    network_force_spread_data = [
        {
            "name": "spread1",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 50, 4),
                net_availability("net2", 100, 51, 4),
                net_availability("net3", 100, 52, 4),
            ],
            "expected": ["net1", "net1", "net2"],
            "unique_network_count": 2,
        },
        {
            "name": "spread2",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 51, 4),
                net_availability("net2", 100, 50, 4),
                net_availability("net3", 100, 52, 4),
            ],
            "expected": ["net2", "net2", "net1"],
            "unique_network_count": 2,
        },
        {
            "name": "equal_spread",
            # in this case each host will have different network
            # however the algorithm randomizes their order
            # so we can not tell in which order hosts
            # will get the network assigned.
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                # all over threshold, spreads the networks equally
                # when networks are equally
                net_availability("net1", 100, 90, 4),
                net_availability("net2", 100, 90, 4),
                net_availability("net3", 100, 90, 4),
            ],
            "expected": [
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
            ],
            "unique_network_count": 3,
        },
        {
            "name": "picks_single_almost_full",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 97, 4),
                net_availability("net2", 100, 100, 4),
            ],
            "expected": ["net1", "net1", "net1"],
        },
        {
            "name": "spread_in_first_2_usable",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 80, 4),
                net_availability("net2", 100, 90, 4),
                net_availability("net3", 100, 99, 4),
            ],
            "expected": [
                "net1 OR net2",
                "net1 OR net2",
                "net1 OR net2",
            ],
            "unique_network_count": 2,
        },
        {
            "name": "no_aval",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 99, 4),
                net_availability("net2", 100, 100, 4),
                net_availability("net3", 100, 99, 4),
            ],
            "expected": ValidationError("No available networks"),
        },
        {
            "name": "spread_between_first_2",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                # all over threshold, spreads the networks equally
                net_availability("net1", 100, 90, 4),
                net_availability("net2", 100, 92, 4),
                net_availability("net3", 100, 96, 4),
            ],
            "expected": ["net1", "net1", "net2"],
            "unique_network_count": 2,
        },
        {
            "name": "can_fit",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 99, 4),
                net_availability("net2", 100, 100, 4),
                net_availability("net3", 100, 98, 4),
            ],
            "expected": ["net3", "net3", "net1"],
            "unique_network_count": 2,
        },
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "x",
        network_force_spread_data,
        ids=[x["name"] for x in network_force_spread_data],
    )
    async def test_network_picking_force_spread(self, x):
        await self.translate_network_types_test_core(
            x, "mrack_force_spread.conf", "force", 95
        )

    network_data_no = [
        {
            "name": "picks_one_from_all",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 51, 4),
                net_availability("net2", 100, 51, 4),
                net_availability("net3", 100, 50, 4),
            ],
            "expected": [
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
            ],
        },
        {
            "name": "picks_one_from_all_2",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 54, 4),
                net_availability("net2", 100, 50, 4),
            ],
            "expected": [
                "net1 OR net2",
                "net1 OR net2",
                "net1 OR net2",
            ],
        },
        {
            "name": "picks_first",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 90, 4),
                net_availability("net2", 100, 90, 4),
                net_availability("net3", 100, 90, 4),
            ],
            "expected": [
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
                "net1 OR net2 OR net3",
            ],
        },
        {
            "name": "picks_single_almost_full",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 97, 4),
                net_availability("net2", 100, 100, 4),
            ],
            "expected": ["net1", "net1", "net1"],
        },
        {
            "name": "no_aval",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 99, 4),
                net_availability("net2", 100, 100, 4),
                net_availability("net3", 100, 99, 4),
            ],
            "expected": ValidationError("No available networks"),
        },
        {
            "name": "fails_even_if_spread_possible",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 98, 4),
                net_availability("net2", 100, 98, 4),
                net_availability("net3", 100, 98, 4),
            ],
            "expected": ValidationError("Can not satisfy request"),
        },
        {
            "name": "fails_even_if_spread_possible2",
            "hosts": [host1(), host2(), host3()],
            "availabilities_data": [
                net_availability("net1", 100, 99, 4),
                net_availability("net2", 100, 100, 4),
                net_availability("net3", 100, 98, 4),
            ],
            "expected": ValidationError("Can not satisfy request"),
        },
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "x", network_data_no, ids=[x["name"] for x in network_data_no]
    )
    async def test_network_picking_no_spread(self, x):
        await self.translate_network_types_test_core(
            x, "mrack_no_spread.conf", "no", 95
        )

    @pytest.mark.asyncio
    async def test_openstack_gather_responses(self):
        error_flag = True

        async def coro1():
            await asyncio.sleep(0.1)
            return "result1"

        async def coro2():
            nonlocal error_flag
            await asyncio.sleep(0.2)
            if error_flag:
                error_flag = False
                raise ServerError("Oops!", 503)
            else:
                return "result2"

        async def coro3():
            await asyncio.sleep(0.3)
            raise ServerError("Oops!", 503)

        provider = OpenStackProvider()

        # Test successful outcome
        result = await provider._openstack_gather_responses([coro1, [], {}])
        assert result[0] == "result1"

        # Test that we get successful outcome after getting a ServerError
        error_flag = True
        result = await provider._openstack_gather_responses(
            [coro1, [], {}], [coro2, [], {}]
        )
        assert result[0] == "result1"
        assert result[1] == "result2"

        # Test that ProvisioningError is raised when we repeatedly get ServerError
        with pytest.raises(ProvisioningError):
            await provider._openstack_gather_responses([coro1, [], {}], [coro3, [], {}])
