import pytest

from mrack.errors import MetadataError
from mrack.utils import get_fqdn, get_shortname, get_username, value_to_bool


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
        with pytest.raises(MetadataError):
            get_fqdn("foo.test", "domain.com")

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
