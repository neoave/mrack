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
import os
from copy import deepcopy
from unittest import mock
from unittest.mock import Mock, patch

import pytest

from mrack.context import global_context
from mrack.errors import MrackError, ProviderNotExists, ValidationError
from mrack.providers.openstack import OpenStackProvider

from .utils import get_data  # FIXME do not use relative import

predefined_hosts = [
    {
        "name": "f-latest-0.mrack.test",
        "os": "fedora-latest",
        "group": "ipaclient",
        "flavor": "ci.standard.xs",
        "image": "idm-Fedora-Cloud-Base-37-latest",
        "key_name": "idm-jenkins",
        "network": "IPv4",
        "config_drive": True,
    },
    {
        "name": "f-latest-1.mrack.test",
        "os": "fedora-latest",
        "group": "ipaclient",
        "flavor": "ci.standard.xs",
        "image": "idm-Fedora-Cloud-Base-37-latest",
        "key_name": "idm-jenkins",
        "network": "IPv4",
        "config_drive": True,
    },
    {
        "name": "f-latest-2.mrack.test",
        "os": "fedora-latest",
        "group": "ipaclient",
        "flavor": "ci.standard.xs",
        "image": "idm-Fedora-Cloud-Base-37-latest",
        "key_name": "idm-jenkins",
        "network": "IPv4",
        "config_drive": True,
    },
]

mocked_nets = get_data("network_availabilities.json")

net3_usable = deepcopy(mocked_nets)
networks = net3_usable["network_ip_availabilities"]
net_1 = networks[0]
net_1["used_ips"] = 999
net_1["subnet_ip_availability"][0]["used_ips"] = 999

low_availability_net1_prio = deepcopy(net3_usable)
networks = low_availability_net1_prio["network_ip_availabilities"]
net_3 = networks[2]
net_3["used_ips"] = 1000
net_3["subnet_ip_availability"][0]["used_ips"] = 1000

low_availability_net3_prio = deepcopy(net3_usable)
networks = low_availability_net3_prio["network_ip_availabilities"]
net_3 = networks[2]
net_3["used_ips"] = 989
net_3["subnet_ip_availability"][0]["used_ips"] = 989

net_2ips_left = deepcopy(mocked_nets)
networks = net_2ips_left["network_ip_availabilities"]
net_1 = networks[0]
net_1["used_ips"] = net_1["total_ips"] - 1
net_1["subnet_ip_availability"][0]["used_ips"] = net_1["total_ips"] - 1
net_3 = networks[2]
net_3["used_ips"] = net_3["total_ips"] - 1
net_3["subnet_ip_availability"][0]["used_ips"] = net_3["total_ips"] - 1

no_available_nets_traceback = deepcopy(mocked_nets)
networks = no_available_nets_traceback["network_ip_availabilities"]
net_1 = networks[0]
net_1["used_ips"] = net_1["total_ips"]
net_1["subnet_ip_availability"][0]["used_ips"] = net_1["total_ips"]
net_3 = networks[2]
net_3["used_ips"] = net_3["total_ips"]
net_3["subnet_ip_availability"][0]["used_ips"] = net_3["total_ips"]


net_pools = get_data("network_pools.json")
network_data = [
    (
        "tc-0-empty-hosts",  # test name
        [],  # hosts
        {},  # network pools
        {},  # networks
        [],  # result
    ),
    (
        "tc1-1-host_net3-usable",
        [deepcopy(predefined_hosts[0])],
        net_pools,
        net3_usable,
        [["net_3"]],
    ),
    (
        "tc2-2-hosts_net3-usable",
        [
            deepcopy(predefined_hosts[0]),
            deepcopy(predefined_hosts[1]),
        ],
        net_pools,
        net3_usable,
        [["net_3"], ["net_3"]],
    ),
    (
        "tc-3-3-hosts_net3-usable",
        [
            deepcopy(predefined_hosts[0]),
            deepcopy(predefined_hosts[1]),
            deepcopy(predefined_hosts[2]),
        ],
        net_pools,
        net3_usable,
        [["net_3"], ["net_3"], ["net_3"]],
    ),
    (
        "tc-4-3-hosts_low-availability_net1_prio",
        [
            deepcopy(predefined_hosts[0]),
            deepcopy(predefined_hosts[1]),
            deepcopy(predefined_hosts[2]),
        ],
        net_pools,
        low_availability_net1_prio,
        [["net_1"], ["net_1"], ["net_3"]],
    ),
    (
        "tc-5-3-hosts_low-availability_net3_prio",
        [
            deepcopy(predefined_hosts[0]),
            deepcopy(predefined_hosts[1]),
            deepcopy(predefined_hosts[2]),
        ],
        net_pools,
        low_availability_net3_prio,
        [["net_3"], ["net_3"], ["net_1"]],
    ),
    (
        "tc-6-3-hosts_no_usable_traceback_2ips_left",
        [
            deepcopy(predefined_hosts[0]),
            deepcopy(predefined_hosts[1]),
            deepcopy(predefined_hosts[2]),
        ],
        net_pools,
        net_2ips_left,
        ValidationError("no available networks"),
    ),
    (
        "tc-7-2-hosts_no_usable_2ips_left",
        [
            deepcopy(predefined_hosts[0]),
            deepcopy(predefined_hosts[1]),
        ],
        net_pools,
        net_2ips_left,
        [["net_1", "net_3"], ["net_1", "net_3"]],
    ),
    (
        "tc-8-1-host_low-availability",
        [deepcopy(predefined_hosts[0])],
        net_pools,
        low_availability_net3_prio,
        [["net_3", "net_1"]],
    ),
    (
        "tc-9-3-hosts_no_available_nets_traceback",
        [
            deepcopy(predefined_hosts[0]),
            deepcopy(predefined_hosts[1]),
            deepcopy(predefined_hosts[2]),
        ],
        net_pools,
        no_available_nets_traceback,
        ValidationError("no available networks"),
    ),
    (
        "tc-10-3-hosts_mocked_nets_should_not_spread",
        [
            deepcopy(predefined_hosts[0]),
            deepcopy(predefined_hosts[1]),
            deepcopy(predefined_hosts[2]),
        ],
        net_pools,
        mocked_nets,
        [["net_1", "net_3"], ["net_1", "net_3"], ["net_1", "net_3"]],
    ),
]

# In case of network spread set to no alg behaves differently and needs
# expected result update, which we expect as outcome from alg
no_spread_results = [deepcopy(d[4]) for d in network_data]  # we copy results
# index is tc number from network_data tc-NUMBER-TESTNAME
# and we change the test case result for each test case number when needed
no_spread_results[4] = ValidationError("Can not satisfy request")
no_spread_results[5] = ValidationError("Can not satisfy request")
no_spread_results[6] = ValidationError("no available networks")
no_spread_results[7] = ValidationError("Can not satisfy request")
no_spread_results[8] = ValidationError("Can not satisfy request")

network_data_no = []
# after that we just copy the values to new list of inputs for parametrized test
for i, in_data in enumerate(deepcopy(network_data)):
    network_data_no.append(
        (
            in_data[0],
            in_data[1],
            in_data[2],
            in_data[3],
            no_spread_results[i],
        )
    )

# In case of network spread set to force alg behaves differently and needs
# expected result update, which we expect as outcome from alg
force_spread_results = [deepcopy(d[4]) for d in network_data]  # we copy results
# index is tc number from network_data tc-NUMBER-TESTNAME
# and we change the test case result for each test case number when needed
force_spread_results[10] = [["net_3"], ["net_3"], ["net_1"]]


network_data_force = []
# after that we just copy the values to new list of inputs for parametrized test
for i, in_data in enumerate(deepcopy(network_data)):
    network_data_force.append(
        (
            in_data[0],
            in_data[1],
            in_data[2],
            in_data[3],
            force_spread_results[i],
        )
    )


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

    @pytest.mark.asyncio
    @pytest.mark.parametrize("x", network_data, ids=[x[0] for x in network_data])
    async def test_network_picking_default_allow_spread(self, x):
        (
            _name,
            hosts,
            pools,
            availability,
            exp_nets,
        ) = x
        reqs = deepcopy(hosts)
        mrack_conf = "mrack.conf"
        if availability:
            del self.mock_neutron
            self.mock_neutron = Mock()
            self.mock_neutron.init_api = AsyncMock(return_value=True)
            self.mock_neutron.network.list = AsyncMock(return_value=self.networks)
            self.mock_neutron.ip.list = AsyncMock(return_value=availability)

            self.mock_neutron_class = Mock(return_value=self.mock_neutron)
            self.neutron_patcher = patch(
                "mrack.providers.openstack.NeutronClient", new=self.mock_neutron_class
            )
            self.neutron_patcher.start()

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
            assert isinstance(global_context.CONFIG.max_network_utilization(), int)
            assert global_context.CONFIG.network_spread() == "allow"
            assert global_context.CONFIG.max_network_utilization() == 75
            # ignore that provider is not registered
            # as global_context contains needed values

        provider = OpenStackProvider()

        await provider.init(image_names=[], networks=pools)
        try:
            provider._translate_network_types(hosts)  # pylint: disable=protected-access
        except MrackError as no_nets:
            assert isinstance(exp_nets, ValidationError)
            assert exp_nets.args[0] in no_nets.args[0]
            assert str(len(hosts)) in str(no_nets)
            return True

        assert len(hosts) == len(reqs)
        for i, host in enumerate(hosts):
            assert host != reqs[i]
            assert host["network"] in pools.get(reqs[i]["network"])
            assert host["network"] in exp_nets[i]

        if exp_nets and all([len(e) > 1 for e in exp_nets]):
            unique_net_cnt = 2 if net_2ips_left == availability else 1
            assert len(set([h["network"] for h in hosts])) == unique_net_cnt

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "x", network_data_force, ids=[x[0] for x in network_data_force]
    )
    async def test_network_picking_force_spread(self, x):
        (
            _test_name,
            hosts,
            pools,
            availability,
            exp_nets,
        ) = x
        reqs = deepcopy(hosts)
        mrack_conf = "mrack_force_spread.conf"

        if availability:
            del self.mock_neutron
            self.mock_neutron = Mock()
            self.mock_neutron.init_api = AsyncMock(return_value=True)
            self.mock_neutron.network.list = AsyncMock(return_value=self.networks)
            self.mock_neutron.ip.list = AsyncMock(return_value=availability)

            self.mock_neutron_class = Mock(return_value=self.mock_neutron)
            self.neutron_patcher = patch(
                "mrack.providers.openstack.NeutronClient", new=self.mock_neutron_class
            )
            self.neutron_patcher.start()

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
            assert isinstance(global_context.CONFIG.max_network_utilization(), int)
            assert global_context.CONFIG.network_spread() == "force"
            assert global_context.CONFIG.max_network_utilization() == 75
            # ignore that provider is not registered
            # as global_context contains needed values

        provider = OpenStackProvider()

        await provider.init(image_names=[], networks=pools)
        try:
            provider._translate_network_types(hosts)  # pylint: disable=protected-access
        except MrackError as no_nets:
            assert isinstance(exp_nets, ValidationError) is True
            assert exp_nets.args[0] in no_nets.args[0]
            assert str(len(hosts)) in str(no_nets)
            return True

        assert len(hosts) == len(reqs)
        for i, host in enumerate(hosts):
            assert host != reqs[i]
            assert host["network"] in pools.get(reqs[i]["network"])
            assert host["network"] in exp_nets[i]

        if hosts:
            unique_net_cnt = 0 if net3_usable == availability else 1
            assert (
                len(set([h["network"] for h in hosts])) >= unique_net_cnt
            )  # only if spread is force

    @pytest.mark.asyncio
    @pytest.mark.parametrize("x", network_data_no, ids=[x[0] for x in network_data_no])
    async def test_network_picking_no_spread(self, x):
        (
            _test_name,
            hosts,
            pools,
            availability,
            exp_nets,
        ) = x
        reqs = deepcopy(hosts)
        mrack_conf = "mrack_no_spread.conf"

        if availability:
            del self.mock_neutron
            self.mock_neutron = Mock()
            self.mock_neutron.init_api = AsyncMock(return_value=True)
            self.mock_neutron.network.list = AsyncMock(return_value=self.networks)
            self.mock_neutron.ip.list = AsyncMock(return_value=availability)

            self.mock_neutron_class = Mock(return_value=self.mock_neutron)
            self.neutron_patcher = patch(
                "mrack.providers.openstack.NeutronClient", new=self.mock_neutron_class
            )
            self.neutron_patcher.start()

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
            assert isinstance(global_context.CONFIG.max_network_utilization(), int)
            assert global_context.CONFIG.network_spread() == "no"
            assert global_context.CONFIG.max_network_utilization() == 75
            # ignore that provider is not registered
            # as global_context contains needed values

        provider = OpenStackProvider()

        await provider.init(image_names=[], networks=pools)
        try:
            provider._translate_network_types(hosts)  # pylint: disable=protected-access
        except MrackError as no_nets:
            assert isinstance(exp_nets, ValidationError)
            assert str(exp_nets) in str(no_nets)
            assert str(len(hosts)) in str(no_nets)
            return True

        assert len(hosts) == len(reqs)
        for i, host in enumerate(hosts):
            assert host != reqs[i]
            assert host["network"] in pools.get(reqs[i]["network"])
            assert host["network"] in exp_nets[i]

        if hosts:
            assert len(set([h["network"] for h in hosts])) == 1  # only if spread is no
