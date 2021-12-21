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

"""Tests for mrack.outputs.utils"""

from unittest.mock import patch

from mrack.outputs.utils import get_external_id


@patch("mrack.outputs.utils.resolve_hostname")
def test_get_external_id(mock_resolve, provisioning_config, host1_aws, metahost1):
    """
    Test that resolve_hostname is not called when it is not supposed to be.
    """
    dns = "my.dns.name"
    mock_resolve.return_value = dns

    # By default, it resolves DNS
    ext_id = get_external_id(host1_aws, metahost1, provisioning_config)
    assert ext_id == dns

    # Disable in host metadata
    metahost1["resolve_host"] = False
    ext_id = get_external_id(host1_aws, metahost1, provisioning_config)
    assert ext_id == host1_aws.ip_addr

    # Disable in provider
    del metahost1["resolve_host"]
    provisioning_config["aws"]["resolve_host"] = False
    ext_id = get_external_id(host1_aws, metahost1, provisioning_config)
    assert ext_id == host1_aws.ip_addr

    # Explicitly enabled in provider
    provisioning_config["aws"]["resolve_host"] = True
    ext_id = get_external_id(host1_aws, metahost1, provisioning_config)
    assert ext_id == dns

    # Resolution enabled, but nothing is resolved
    mock_resolve.return_value = None
    ext_id = get_external_id(host1_aws, metahost1, provisioning_config)
    assert ext_id == host1_aws.ip_addr
