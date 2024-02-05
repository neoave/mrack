# Copyright 2021 Red Hat Inc.
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

"""Tests for mrack.providers.beaker"""

from unittest import mock
from unittest.mock import Mock, patch

import pytest

from mrack.providers.beaker import BeakerProvider

from .utils import get_content, get_file_path


class TestBeakerProvider:
    def setup_method(self):

        self.mock_hub = Mock()
        self.result_xml = get_content("result.xml")
        self.mock_hub.taskactions.to_xml = Mock(return_value=self.result_xml)
        self.mock_hub_class = Mock(return_value=self.mock_hub)
        self.hub_patcher = patch(
            "mrack.providers.beaker.HubProxy", new=self.mock_hub_class
        )
        self.hub_patcher.start()
        self.log_msg_start = "Beaker [client.testdomain.test]"
        self.beaker_id = 8874545
        self.distros = ["Fedora-32%", "Fedora-37%", "CentOS-Stream-9%"]
        self.timeout = 120
        self.reserve_duration = 86400

    def teardown_method(self):
        mock.patch.stopall()

    @pytest.mark.asyncio
    async def test_get_repo_info(self, monkeypatch):
        monkeypatch.setenv("BEAKER_CONF", get_file_path("client.conf"))
        provider = BeakerProvider()
        await provider.init(self.distros, self.timeout, self.reserve_duration)
        bkr_res = provider._get_recipe_info(self.beaker_id, self.log_msg_start)
        assert bkr_res["system"] == "test.example.com"
        assert bkr_res["status"] == "Completed"
        assert bkr_res["result"] == "Pass"
        assert bkr_res["rid"] == "15482633"
        assert bkr_res["id"] == "8874545"
        assert bkr_res["logs"] == {
            "console.log": "https://test.example.com/logs/console.log",
            "anaconda.log": "https://test.example.com/logs/anaconda.log",
        }
