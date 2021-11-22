import pytest

from mrack.utils import get_shortname


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
