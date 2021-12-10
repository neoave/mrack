import pytest

from mrack.utils import get_shortname, get_username


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
