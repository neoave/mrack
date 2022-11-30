import pytest

from mrack.utils import get_shortname, get_username, value_to_bool


@pytest.mark.parametrize(
    "hostname,expected",
    [
        ("abc", "abc"),
        ("foo.bar.baz", "foo"),
        ("foo.", "foo"),
        (".", ""),
    ],
)
def test_get_shortname(hostname, expected):
    assert get_shortname(hostname) == expected


def test_get_username(
    provisioning_config, host1_aws, host1_osp, metahost1, host_win_aws, metahost_win
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
def test_value_to_bool(value, expected):
    try:
        assert value_to_bool(value) == expected
    except Exception as exc:
        assert isinstance(exc, expected)
