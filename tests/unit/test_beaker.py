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
from xml.dom.minidom import Document as xml_doc

import pytest

from mrack.providers import providers
from mrack.providers.beaker import BeakerProvider

from .mock_data import MockedBeakerTransformer, provisioning_config
from .utils import get_content, get_file_path


@pytest.fixture
def mock_beaker_conf(monkeypatch):
    monkeypatch.setenv("BEAKER_CONF", get_file_path("client.conf"))


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
    async def test_get_repo_info(self, mock_beaker_conf):
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

    @pytest.mark.asyncio
    async def test_beaker_job_creation(self, mock_beaker_conf):
        # Given initialized beaker provider and transformer with real beaker
        # calls mocked
        providers.register("beaker", BeakerProvider)
        provider = providers.get("beaker")
        await provider.init(self.distros, self.timeout, self.reserve_duration)
        bkr_transformer = MockedBeakerTransformer()

        await bkr_transformer.init(provisioning_config(), {})
        bkr_transformer.add_host(
            {
                "name": "host.example.test",
                "group": "client",
                "os": "Fedora-31%",
            }
        )

        # When having a host requirement and creating a Beaker job
        req = bkr_transformer.create_host_requirements()[0]
        job = provider._req_to_bkr_job(req)

        # Then the job contains param to supress 10_avc_check restraint plugin
        # so that provisioning won't fail on AVC denials
        xml = job.toxml()
        assert '<param name="RSTRNT_DISABLED" value="10_avc_check"/>' in xml

    def test_translate_constraint_basic_operands(self, mock_beaker_conf):
        """Test _translate_constraint with basic operands (no and/or)."""
        provider = BeakerProvider()

        # Create a mock host_recipe node
        doc = xml_doc()
        host_recipe = doc.createElement("hostRequires")

        # Test with basic operands (not 'and' or 'or')
        host_requires = {
            "memory": {"_op": ">=", "_value": "4096"},
            "key_value": {"_key": "NETBOOT_METHOD", "_op": "like", "_value": "grub2"},
        }

        provider._translate_constraint(host_requires, host_recipe)

        # Verify the XML structure
        xml_output = host_recipe.toxml()
        assert '<memory op="&gt;=" value="4096"/>' in xml_output
        assert '<key_value key="NETBOOT_METHOD" op="like" value="grub2"/>' in xml_output

    def test_translate_constraint_and_operand(self, mock_beaker_conf):
        """Test _translate_constraint with 'and' operand."""
        provider = BeakerProvider()

        # Create a mock host_recipe node
        doc = xml_doc()
        host_recipe = doc.createElement("hostRequires")

        # Test with 'and' operand containing basic constraints
        host_requires = {
            "and": [
                {"memory": {"_op": ">=", "_value": "4096"}},
                {"key_value": {"_key": "PROCESSOR_CORES", "_op": ">=", "_value": "4"}},
            ]
        }

        provider._translate_constraint(host_requires, host_recipe)

        # Verify the XML structure contains the 'and' node with nested constraints
        xml_output = host_recipe.toxml()
        assert "<and>" in xml_output
        assert "</and>" in xml_output
        assert '<memory op="&gt;=" value="4096"/>' in xml_output
        assert '<key_value key="PROCESSOR_CORES" op="&gt;=" value="4"/>' in xml_output

    def test_translate_constraint_or_operand(self, mock_beaker_conf):
        """Test _translate_constraint with 'or' operand."""
        provider = BeakerProvider()

        # Create a mock host_recipe node
        doc = xml_doc()
        host_recipe = doc.createElement("hostRequires")

        # Test with 'or' operand containing basic constraints
        host_requires = {
            "or": [
                {"memory": {"_op": ">=", "_value": "8192"}},
                {"memory": {"_op": ">=", "_value": "4096"}},
            ]
        }

        provider._translate_constraint(host_requires, host_recipe)

        # Verify the XML structure contains the 'or' node with nested constraints
        xml_output = host_recipe.toxml()
        assert "<or>" in xml_output
        assert "</or>" in xml_output
        # Should contain both memory constraints
        assert xml_output.count('<memory op="&gt;=" value="8192"/>') == 1
        assert xml_output.count('<memory op="&gt;=" value="4096"/>') == 1

    def test_translate_constraint_nested_and_or(self, mock_beaker_conf):
        """Test _translate_constraint with nested 'and'/'or' operands."""
        provider = BeakerProvider()

        # Create a mock host_recipe node
        doc = xml_doc()
        host_recipe = doc.createElement("hostRequires")

        # Test with nested 'and' and 'or' operands
        host_requires = {
            "and": [
                {"memory": {"_op": ">=", "_value": "4096"}},
                {
                    "or": [
                        {
                            "key_value": {
                                "_key": "PROCESSOR_CORES",
                                "_op": ">=",
                                "_value": "4",
                            }
                        },
                        {
                            "key_value": {
                                "_key": "PROCESSOR_CORES",
                                "_op": ">=",
                                "_value": "8",
                            }
                        },
                    ]
                },
            ]
        }

        provider._translate_constraint(host_requires, host_recipe)

        # Verify the XML structure contains nested 'and' and 'or' nodes
        xml_output = host_recipe.toxml()
        assert "<and>" in xml_output
        assert "<or>" in xml_output
        assert "</or>" in xml_output
        assert "</and>" in xml_output
        assert '<memory op="&gt;=" value="4096"/>' in xml_output
        # Should contain both processor core constraints within the 'or'
        assert xml_output.count('key="PROCESSOR_CORES"') == 2

    def test_translate_constraint_mixed_operands(self, mock_beaker_conf):
        """Test _translate_constraint with mixed basic and and/or operands."""
        provider = BeakerProvider()

        # Create a mock host_recipe node
        doc = xml_doc()
        host_recipe = doc.createElement("hostRequires")

        # Test with mixed operands (basic + and/or)
        host_requires = {
            "memory": {"_op": ">=", "_value": "4096"},
            "and": [
                {
                    "key_value": {
                        "_key": "NETBOOT_METHOD",
                        "_op": "like",
                        "_value": "grub2",
                    }
                },
                {"key_value": {"_key": "PROCESSOR_CORES", "_op": ">=", "_value": "2"}},
            ],
        }

        provider._translate_constraint(host_requires, host_recipe)

        # Verify both basic and 'and' operands are handled correctly
        xml_output = host_recipe.toxml()
        assert '<memory op="&gt;=" value="4096"/>' in xml_output
        assert "<and>" in xml_output
        assert "</and>" in xml_output
        assert 'key="NETBOOT_METHOD"' in xml_output
        assert 'key="PROCESSOR_CORES"' in xml_output

    def test_translate_constraint_with_attributes(self, mock_beaker_conf):
        """Test _translate_constraint with underscore-prefixed attributes."""
        provider = BeakerProvider()

        # Create a mock host_recipe node
        doc = xml_doc()
        host_recipe = doc.createElement("hostRequires")

        # Test with underscore-prefixed attributes that should become node attributes
        host_requires = {
            "_method": "system",
            "_type": "primary",
            "memory": {"_op": ">=", "_value": "4096"},
        }

        provider._translate_constraint(host_requires, host_recipe)

        # Verify attributes are set on the host_recipe node
        assert host_recipe.getAttribute("method") == "system"
        assert host_recipe.getAttribute("type") == "primary"

        # Verify the memory constraint is still added as a child element
        xml_output = host_recipe.toxml()
        assert '<memory op="&gt;=" value="4096"/>' in xml_output
