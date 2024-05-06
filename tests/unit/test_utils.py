from xml.dom.minidom import Document as xml_doc

import pytest

from mrack.utils import (
    add_dict_to_node,
    get_fqdn,
    get_os_type,
    get_shortname,
    get_ssh_options,
    get_username,
    ssh_options_to_cli,
    value_to_bool,
)

from .mock_data import get_db_from_metadata


class TestPytestMrackUtils:
    @pytest.mark.parametrize(
        "hostname,expected",
        [
            ("abc", "abc"),
            ("foo.bar.baz", "foo"),
            ("foo.", "foo"),
            (".", ""),
        ],
    )
    def test_get_shortname(self, hostname, expected):
        assert get_shortname(hostname) == expected

    @pytest.mark.parametrize(
        "hostname,domain,expected",
        [
            ("foo.subdomain.test", "test", "foo.subdomain.test"),
            ("foo", "test", "foo.test"),
            ("foo", "subdomain.test", "foo.subdomain.test"),
        ],
    )
    def test_get_fqdn(self, hostname, domain, expected):
        assert get_fqdn(hostname, domain) == expected

    def test_get_fqdn_mismatch(self):
        assert get_fqdn("foo.test", "domain.com") == "foo.test"

    def test_get_username(
        self,
        provisioning_config,
        host1_aws,
        host1_osp,
        metahost1,
        host_win_aws,
        metahost_win,
    ):
        value = get_username(host1_aws, metahost1, provisioning_config)
        assert value == "ec2-user"

        value = get_username(host1_osp, metahost1, provisioning_config)
        assert value == "cloud-user"

        value = get_username(host_win_aws, metahost_win, provisioning_config)
        assert value == "Administrator"

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("true", True),
            ("True", True),
            ("t", True),
            ("T", True),
            ("TRUe", True),
            ("trUE", True),
            ("TRUE", True),
            ("1", True),
            ("false", False),
            ("False", False),
            ("FALse", False),
            ("faLSE", False),
            ("FALSE", False),
            ("0", False),
            ([], False),
            (["ITEM"], True),
            ({"A": 9}, True),
            ({}, False),
            ((), False),
            ((1, 2), True),
            (True, True),
            (False, False),
            ("foo.true.baz", ValueError),
            ("abc false", ValueError),
            ("true9.", ValueError),
            ("false1", ValueError),
        ],
    )
    def test_value_to_bool(self, value, expected):
        try:
            assert value_to_bool(value) == expected
        except Exception as exc:
            assert isinstance(exc, expected)

    @pytest.mark.parametrize(
        "metahost,expected",
        [
            ({"os": "rhel-8.5"}, "linux"),
            ({"os": "fedora-35"}, "linux"),
            ({"os": "windows-2022"}, "windows"),
            ({"os": "rhel-8.5", "os_type": "my-linux"}, "my-linux"),
            ({"os": "fedora-35", "os_type": "my-linux"}, "my-linux"),
            ({"os": "windows-2022", "os_type": "my-windows"}, "my-windows"),
        ],
    )
    def test_get_os_type(self, metahost, expected):
        assert get_os_type(metahost) == expected

    def test_get_ssh_options(self, provisioning_config, metahost1):
        """Test obtaining of SSH options."""
        metadata = {
            "domains": [
                {
                    "name": "example.com",
                    "hosts": [
                        metahost1,
                    ],
                }
            ]
        }

        db = get_db_from_metadata(metadata)

        assert "strategy" in provisioning_config["openstack"]

        host = list(db.hosts.values())[0]

        ssh_options = get_ssh_options(host, metadata, provisioning_config)
        assert isinstance(ssh_options, dict)

        # Test that ssh options has expected default values when nothing is set
        assert "StrictHostKeyChecking" in ssh_options
        assert ssh_options["StrictHostKeyChecking"] == "no"
        assert "UserKnownHostsFile" in ssh_options
        assert ssh_options["UserKnownHostsFile"] == "/dev/null"
        assert len(ssh_options) == 2

        # Test that default ssh options can be nullified in provisioning config
        provisioning_config["ssh"] = {"options": {}}
        ssh_options = get_ssh_options(host, metadata, provisioning_config)
        assert isinstance(ssh_options, dict)
        assert len(ssh_options) == 0

        # Test that custom options are returned
        options_spec = {"Foo": "Bar", "Baz": 0, "Third": "Value"}
        provisioning_config["ssh"] = {"options": options_spec}
        ssh_options = get_ssh_options(host, metadata, provisioning_config)
        assert isinstance(ssh_options, dict)
        assert len(ssh_options) == 3
        for key, value in options_spec.items():
            assert key in ssh_options
            assert ssh_options[key] == value

    @pytest.mark.parametrize(
        "options,expected",
        [
            # simple
            ({"Foo": "Bar"}, ["-o", "'Foo=Bar'"]),
            # integer + 2 values
            ({"Foo": "Bar", "A": 0}, ["-o", "'Foo=Bar'", "-o", "'A=0'"]),
            # handles boolean (this should be rare)
            ({"Foo": False}, ["-o", "'Foo=False'"]),
            # Value could be empty
            ({"Foo": ""}, ["-o", "'Foo='"]),
        ],
    )
    def test_ssh_options_to_cli(self, options, expected):
        """Test conversion of SSH options to CLI params."""
        assert ssh_options_to_cli(options) == expected

    @pytest.mark.parametrize(
        "req_node, dct, expected",
        [
            (
                xml_doc().createElement("not"),
                {
                    "key_value": {
                        "_key": "NETBOOT_METHOD",
                        "_op": "like",
                        "_value": "grub2",
                    }
                },
                '<not><key_value key="NETBOOT_METHOD" op="like" value="grub2"/></not>',
            ),
            (
                xml_doc().createElement("and"),
                {
                    "not": [
                        {
                            "key_value": {
                                "_key": "BOOTDISK",
                                "_op": "==",
                                "_value": "dum",
                            }
                        },
                    ]
                },
                '<and><not><key_value key="BOOTDISK" op="==" value="dum"/></not></and>',
            ),
        ],
    )
    def test_add_dict_to_node(self, req_node, dct, expected):
        assert add_dict_to_node(req_node, dct).toxml() == expected
