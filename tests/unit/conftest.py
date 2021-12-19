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

from unittest.mock import MagicMock, PropertyMock

import pytest

from mrack.config import ProvisioningConfig
from mrack.host import STATUS_ACTIVE, Host

"""Fixtures for unit tests."""


@pytest.fixture
def openstack_config():
    return {
        "strategy": "retry",
        "max_retry": 5,
        "images": {
            "rhel-8.5": "osp-rhel-8-5",
            "fedora-34": "osp-fedora34",
            "win-2019": "osp-win-2019",
        },
        "flavors": {
            "ipaserver": "test.medium",
            "ipaclient": "test.micro",
            "ad": "test.medium",
            "default": "test.nano",
        },
        "networks": {
            "IPv4": [
                "test-net4-1",
                "test-net4-2",
                "test-net4-3",
                "test-net4-4",
            ],
            "IPv6": [
                "test-net6-1",
            ],
            "dual": [
                "test-dual-1",
                "test-dual-2",
            ],
        },
        "default_network": "IPv4",
        "keypair": "mrack-keypair",
    }


@pytest.fixture
def aws_config():
    return {
        "images": {
            "rhel-8.5": "ami-rhel-8-5",
            "fedora-34": "ami-fedora34",
            "win-2019": "ami-win-2019",
        },
        "flavors": {
            "ipaserver": "t2.medium",
            "ipaclient": "t2.micro",
            "ad": "t2.medium",
            "default": "t2.nano",
        },
        "users": {
            "rhel-8.5": "ec2-user",
        },
        "keypair": "mrack-keypair.pem",
        "security_group": "sg-something",
        "credentials_file": "aws.key",
        "profile": "default",
        "spot": True,
        "instance_tags": {
            "Name": "mrack-runner",
            "mrack": "True",
            "Persistent": "False",
        },
    }


@pytest.fixture
def provisioning_config(openstack_config, aws_config):
    raw = {
        "openstack": openstack_config,
        "aws": aws_config,
        "users": {
            "rhel-8.5": "cloud-user",
            "fedora-34": "fedora",
            "win-2019": "Administrator",
        },
    }
    return ProvisioningConfig(raw)


@pytest.fixture
def metahost1():
    return {
        "name": "ipa1.example.com",
        "role": "first",
        "group": "ipaserver",
        "os": "rhel-8.5",
    }


@pytest.fixture
def metahost_win():
    return {
        "name": "ipa1.example.com",
        "role": "ad",
        "group": "ad_root",
        "os": "win-2019",
        "network": "IPv4",
    }


def mock_provider(name):
    mock = MagicMock()
    name_prop = PropertyMock(return_value=name)
    type(mock).name = name_prop
    return mock


def meta_to_host(meta_host, provider_key, host_id, ip_address):
    return Host(
        mock_provider(provider_key),
        host_id,
        meta_host["name"],
        meta_host["os"],
        meta_host["group"],
        ip_address,
        STATUS_ACTIVE,
        {},
    )


@pytest.fixture
def host1_aws(metahost1):
    return meta_to_host(metahost1, "aws", "1", "192.168.0.128")


@pytest.fixture
def host1_osp(metahost1):
    return meta_to_host(metahost1, "openstack", "2", "192.168.1.128")


@pytest.fixture
def host_win_aws(metahost_win):
    return meta_to_host(metahost_win, "aws", "3", "192.168.0.129")
