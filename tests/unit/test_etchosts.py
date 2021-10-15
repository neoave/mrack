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

import pytest
from unit.utils import copy_as_temp

from mrack.actions.etchosts import EtcHostsUpdater
from mrack.errors import ConfigError
from mrack.host import Host


def create_host(name, ip):
    return Host(None, None, name, None, None, [ip], None, None)


def hosts_data():
    return [
        create_host("host1.example.test", "192.168.125.20"),
        create_host("host2.example.test", "192.168.125.21"),
        create_host("host3.example.test", "192.168.125.22"),
    ]


@pytest.fixture
def etc_hosts(request):
    marker = request.node.get_closest_marker("etc_hosts")
    print(marker.args[0])
    test_path = copy_as_temp(marker.args[0])
    yield test_path
    os.remove(test_path)


START_MARK = "# Managed by mrack - start\n"
END_MARK = "# Managed by mrack - end\n"


class TestEtcHostsUpdater:
    def assert_updater_state(self, updater, hosts):
        # expected added data
        record1 = f"{hosts[0].ip_addr} {hosts[0].name}\n"
        record2 = f"{hosts[1].ip_addr} {hosts[1].name}\n"
        record3 = f"{hosts[2].ip_addr} {hosts[2].name}\n"
        lines = updater.lines

        assert len(updater.lines) == 2 + 5, "expecting 5 new lines"

        # lines contains
        assert START_MARK in lines
        assert END_MARK in lines
        start_pos = lines.index(START_MARK)
        end_pos = lines.index(END_MARK)
        assert start_pos < end_pos

        # records are present
        assert record1 in lines
        assert record2 in lines
        assert record3 in lines

        rec1_pos = lines.index(record1)
        rec2_pos = lines.index(record2)
        rec3_pos = lines.index(record3)

        # records are between marks
        assert rec1_pos > start_pos and rec1_pos < end_pos
        assert rec2_pos > start_pos and rec2_pos < end_pos
        assert rec3_pos > start_pos and rec3_pos < end_pos

    def assert_cleanup(self, updater):
        lines = updater.lines
        assert len(updater.lines) == 2
        assert START_MARK not in lines
        assert END_MARK not in lines

    @pytest.mark.etc_hosts("data/etc/etc.hosts")
    def test_expected_functionality(self, etc_hosts):
        updater = EtcHostsUpdater(etc_hosts)

        # test initial read
        assert len(updater.lines) == 2
        assert updater.lines[0].startswith("127.0.0.1")
        assert updater.lines[1].startswith("::1")

        hosts = hosts_data()
        updater.add_hosts(hosts)
        self.assert_updater_state(updater, hosts)

        # Running multiple times should result in the same state
        updater.add_hosts(hosts)
        self.assert_updater_state(updater, hosts)

        # save the changes to file
        updater.save()

        # load the file again and check if the saved value are there
        updater2 = EtcHostsUpdater(etc_hosts)
        self.assert_updater_state(updater2, hosts)

        # remove the added lines
        updater2.clear()
        self.assert_cleanup(updater2)
        updater2.save()

        updater3 = EtcHostsUpdater(etc_hosts)
        self.assert_cleanup(updater3)

    def test_default_path(self):
        updater = EtcHostsUpdater()
        assert updater.path == "/etc/hosts"

    @pytest.mark.etc_hosts("data/etc/hosts_missing_start")
    def test_invalid_missing_start(self, etc_hosts):
        with pytest.raises(ConfigError, match=r"Doesn't have start mark."):
            EtcHostsUpdater(etc_hosts)

    @pytest.mark.etc_hosts("data/etc/hosts_missing_end")
    def test_invalid_missing_end(self, etc_hosts):
        with pytest.raises(ConfigError, match=r"Doesn't have end mark."):
            EtcHostsUpdater(etc_hosts)

    @pytest.mark.etc_hosts("data/etc/hosts_multi_start")
    def test_invalid_multi_start(self, etc_hosts):
        with pytest.raises(ConfigError, match=r"Multiple start marks."):
            EtcHostsUpdater(etc_hosts)

    @pytest.mark.etc_hosts("data/etc/hosts_multi_end")
    def test_invalid_multi_end(self, etc_hosts):
        with pytest.raises(ConfigError, match=r"Multiple end marks."):
            EtcHostsUpdater(etc_hosts)

    @pytest.mark.etc_hosts("data/etc/hosts_order")
    def test_invalid_order(self, etc_hosts):
        with pytest.raises(ConfigError, match=r"End mark before start mark."):
            EtcHostsUpdater(etc_hosts)
