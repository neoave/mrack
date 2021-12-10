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

from mrack.utils import find_value_in_config_hierarchy

"""Tests for ProvisioningConfig and searching in config hierarchy."""


def test_find_value_in_config_hierarchy(
    provisioning_config, host1_aws, host1_osp, metahost1, host_win_aws, metahost_win
):
    value = find_value_in_config_hierarchy(
        provisioning_config,
        "aws",
        host1_aws,
        metahost1,
        "username",
        "users",
        metahost1["os"],
    )
    assert value == "ec2-user"

    value = find_value_in_config_hierarchy(
        provisioning_config,
        "openstack",
        host1_osp,
        metahost1,
        "username",
        "users",
        metahost1["os"],
    )
    assert value == "cloud-user"

    value = find_value_in_config_hierarchy(
        provisioning_config,
        "aws",
        host_win_aws,
        metahost_win,
        "username",
        "users",
        metahost_win["os"],
    )
    assert value == "Administrator"
