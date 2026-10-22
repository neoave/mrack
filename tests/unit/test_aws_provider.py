"""Tests for AWS Provider - SSM image resolution and subnet placement."""

import os
from collections import Counter
from unittest.mock import MagicMock, patch

import pytest

from mrack.context import global_context
from mrack.errors import ProviderNotExists, ValidationError
from mrack.providers.aws import AWSProvider


class MockAMI:
    """Mock AWS AMI object."""

    def __init__(
        self, image_id, name=None, tags=None, creation_date="2024-01-01T00:00:00.000Z"
    ):
        self.image_id = image_id
        self.name = name
        self.tags = tags
        self.creation_date = creation_date


@pytest.fixture
def provider():
    """Create an AWSProvider with mocked boto3 clients."""
    with patch("mrack.providers.aws.boto3"):
        p = AWSProvider()
        p.dsp_name = "AWS"
        p.amis = []
        p._ssm_client = MagicMock()
        p.ssm_resolved = {}
        p.ec2 = MagicMock()
        return p


class TestValidateSSMImageDef:
    """Test validate_ssm_image_def method."""

    def test_valid(self, provider):
        image_def = {"ssm": "/aws/service/ami-windows-latest/Windows_Server-2022"}
        assert provider.validate_ssm_image_def(image_def) is True

    def test_missing_ssm_key(self, provider):
        with pytest.raises(ValidationError):
            provider.validate_ssm_image_def({"tag": "something"})

    def test_ssm_not_string(self, provider):
        with pytest.raises(ValidationError):
            provider.validate_ssm_image_def({"ssm": 123})

    def test_not_dict(self, provider):
        with pytest.raises(ValidationError):
            provider.validate_ssm_image_def("just-a-string")


class TestGetImageSSM:
    """Test get_image with SSM-based image definitions."""

    def test_returns_cached_ami_after_resolution(self, provider):
        ami = MockAMI("ami-resolved-123")
        provider.amis = [ami]
        provider.ssm_resolved = {
            "/aws/service/ami-windows-latest/Win2022": "ami-resolved-123"
        }

        req = {
            "name": "win-host",
            "image": {"ssm": "/aws/service/ami-windows-latest/Win2022"},
        }
        result = provider.get_image(req)
        assert result is ami

    def test_returns_none_before_resolution(self, provider):
        provider.amis = []
        provider.ssm_resolved = {}

        req = {
            "name": "win-host",
            "image": {"ssm": "/aws/service/ami-windows-latest/Win2022"},
        }
        result = provider.get_image(req)
        assert result is None

    def test_returns_none_when_resolved_but_not_cached(self, provider):
        provider.amis = [MockAMI("ami-other")]
        provider.ssm_resolved = {
            "/aws/service/ami-windows-latest/Win2022": "ami-resolved-123"
        }

        req = {
            "name": "win-host",
            "image": {"ssm": "/aws/service/ami-windows-latest/Win2022"},
        }
        result = provider.get_image(req)
        assert result is None

    def test_tag_lookup_still_works(self, provider):
        ami = MockAMI("ami-tag", tags=[{"Key": "env", "Value": "prod"}])
        provider.amis = [ami]

        req = {
            "name": "host",
            "image": {"tag": {"name": "env", "value": "prod"}},
        }
        result = provider.get_image(req)
        assert result is ami

    def test_ami_id_lookup_still_works(self, provider):
        ami = MockAMI("ami-direct-123")
        provider.amis = [ami]

        req = {"name": "host", "image": "ami-direct-123"}
        result = provider.get_image(req)
        assert result is ami

    def test_invalid_dict_raises(self, provider):
        req = {"name": "host", "image": {"unknown": "value"}}
        with pytest.raises(ValidationError, match="'tag', 'ssm', or AMI ID"):
            provider.get_image(req)

    def test_no_image_raises(self, provider):
        req = {"name": "host"}
        with pytest.raises(ValidationError, match="doesn't have image defined"):
            provider.get_image(req)


class TestLoadImageSSM:
    """Test load_image with SSM-based image definitions."""

    def test_resolves_ssm_and_loads_ami(self, provider):
        ssm_path = "/aws/service/ami-windows-latest/Windows_Server-2022"
        provider.ssm_client.get_parameter.return_value = {
            "Parameter": {"Value": "ami-win2022-latest"}
        }

        mock_ami = MockAMI(
            "ami-win2022-latest", creation_date="2024-06-01T00:00:00.000Z"
        )
        provider.ec2.images.filter.return_value = [mock_ami]

        req = {"name": "win-host", "image": {"ssm": ssm_path}}
        result = provider.load_image(req)

        provider.ssm_client.get_parameter.assert_called_once_with(Name=ssm_path)
        provider.ec2.images.filter.assert_called_once_with(
            Filters=[{"Name": "image-id", "Values": ["ami-win2022-latest"]}]
        )
        assert result is mock_ami
        assert provider.ssm_resolved[ssm_path] == "ami-win2022-latest"
        assert mock_ami in provider.amis

    def test_no_ami_found_raises(self, provider):
        provider.ssm_client.get_parameter.return_value = {
            "Parameter": {"Value": "ami-nonexistent"}
        }
        provider.ec2.images.filter.return_value = []

        req = {"name": "win-host", "image": {"ssm": "/aws/service/some-path"}}
        with pytest.raises(ValidationError, match="Cannot find image"):
            provider.load_image(req)

    def test_returns_newest_when_multiple(self, provider):
        provider.ssm_client.get_parameter.return_value = {
            "Parameter": {"Value": "ami-123"}
        }

        old_ami = MockAMI("ami-123", creation_date="2024-01-01T00:00:00.000Z")
        new_ami = MockAMI("ami-123", creation_date="2024-06-01T00:00:00.000Z")
        provider.ec2.images.filter.return_value = [old_ami, new_ami]

        req = {"name": "host", "image": {"ssm": "/aws/service/path"}}
        result = provider.load_image(req)
        assert result is new_ami

    def test_tag_load_still_works(self, provider):
        mock_ami = MockAMI("ami-tag-1", creation_date="2024-01-01T00:00:00.000Z")
        provider.ec2.images.filter.return_value = [mock_ami]

        req = {
            "name": "host",
            "image": {"tag": {"name": "env", "value": "prod"}},
        }
        result = provider.load_image(req)
        provider.ec2.images.filter.assert_called_once_with(
            Filters=[{"Name": "tag:env", "Values": ["prod"]}]
        )
        assert result is mock_ami

    def test_ami_id_load_still_works(self, provider):
        mock_ami = MockAMI("ami-direct", creation_date="2024-01-01T00:00:00.000Z")
        provider.ec2.images.filter.return_value = [mock_ami]

        req = {"name": "host", "image": "ami-direct"}
        result = provider.load_image(req)
        provider.ec2.images.filter.assert_called_once_with(
            Filters=[{"Name": "image-id", "Values": ["ami-direct"]}]
        )
        assert result is mock_ami


def init_spread_config(mrack_conf):
    """Load mrack.conf variant selecting the network-spread mode."""
    conf_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf")
    try:
        global_context.init(
            os.path.join(conf_dir, mrack_conf),
            os.path.join(conf_dir, "provisioning-config.yaml"),
        )
    except ProviderNotExists:
        assert global_context.CONFIG is not None


def mock_subnets(provider, availabilities, cidrs=None):
    """Mock ec2.Subnet with given available IP counts, /24 unless in cidrs."""
    cidrs = cidrs or {}

    def subnet(subnet_id):
        return MagicMock(
            cidr_block=cidrs.get(subnet_id, "10.0.0.0/24"),
            available_ip_address_count=availabilities[subnet_id],
        )

    provider.ec2.Subnet = MagicMock(side_effect=subnet)


def subnet_reqs(names, subnet_ids):
    return [{"name": name, "subnet_ids": list(subnet_ids)} for name in names]


class TestValidateHostsSubnetPlacement:
    """Test subnet placement in validate_hosts based on network-spread."""

    @pytest.mark.asyncio
    async def test_allow_groups_hosts_on_one_subnet(self, provider):
        init_spread_config("mrack.conf")
        # s3 has 241/251 IPs used, over the default 95% threshold
        mock_subnets(provider, {"s1": 200, "s2": 200, "s3": 10})
        reqs = subnet_reqs("AB", ["s1", "s2", "s3"])
        reqs += subnet_reqs("C", ["s3", "s2", "s1"])  # same candidates, other order

        await provider.validate_hosts(reqs)

        placed = {req["subnet_ids"][0] for req in reqs}
        assert all(len(req["subnet_ids"]) == 1 for req in reqs)
        assert len(placed) == 1
        assert placed <= {"s1", "s2"}

    @pytest.mark.asyncio
    async def test_force_spreads_hosts(self, provider):
        init_spread_config("mrack_force_spread.conf")
        mock_subnets(provider, {"s1": 200, "s2": 190, "s3": 180})
        reqs = subnet_reqs("ABCDE", ["s1", "s2", "s3"])

        await provider.validate_hosts(reqs)

        assert [req["subnet_ids"] for req in reqs] == [
            ["s1"],
            ["s1"],
            ["s2"],
            ["s2"],
            ["s3"],
        ]

    @pytest.mark.asyncio
    async def test_no_spread_fails_when_no_subnet_fits(self, provider):
        init_spread_config("mrack_no_spread.conf")
        mock_subnets(provider, {"s1": 2, "s2": 2})
        reqs = subnet_reqs("ABC", ["s1", "s2"])

        with pytest.raises(ValidationError):
            await provider.validate_hosts(reqs)

    @pytest.mark.asyncio
    async def test_single_or_no_subnet_untouched(self, provider):
        init_spread_config("mrack.conf")
        mock_subnets(provider, {})
        reqs = subnet_reqs("A", ["s9"]) + subnet_reqs("B", []) + [{"name": "C"}]

        await provider.validate_hosts(reqs)

        assert [req.get("subnet_ids") for req in reqs] == [["s9"], [], None]
        provider.ec2.Subnet.assert_not_called()

    @pytest.mark.asyncio
    async def test_candidate_lists_placed_independently(self, provider):
        init_spread_config("mrack.conf")
        mock_subnets(provider, {"s1": 200, "s2": 200, "s3": 200, "s4": 200})
        reqs = subnet_reqs("AB", ["s1", "s2"]) + subnet_reqs("CD", ["s3", "s4"])

        await provider.validate_hosts(reqs)

        assert {reqs[0]["subnet_ids"][0], reqs[1]["subnet_ids"][0]} < {"s1", "s2"}
        assert {reqs[2]["subnet_ids"][0], reqs[3]["subnet_ids"][0]} < {"s3", "s4"}

    @pytest.mark.asyncio
    async def test_retry_keeps_placement(self, provider):
        init_spread_config("mrack.conf")
        mock_subnets(provider, {"s1": 200, "s2": 190})
        reqs = subnet_reqs("ABC", ["s1", "s2"])
        await provider.validate_hosts(reqs)
        placed = [req["subnet_ids"] for req in reqs]

        # retry gets the same req objects for the hosts which failed
        provider.ec2.Subnet.reset_mock()
        await provider.validate_hosts(reqs[2:])
        await provider.validate_hosts(reqs)  # all hosts deleted and retried

        assert [req["subnet_ids"] for req in reqs] == placed
        provider.ec2.Subnet.assert_not_called()

    @pytest.mark.asyncio
    async def test_force_skips_subnets_over_threshold(self, provider):
        init_spread_config("mrack_force_spread.conf")
        mock_subnets(provider, {"s1": 200, "s2": 200, "s3": 10})
        reqs = subnet_reqs("ABC", ["s1", "s2", "s3"])

        await provider.validate_hosts(reqs)

        placed = [req["subnet_ids"][0] for req in reqs]
        assert len(set(placed)) == 2
        assert "s3" not in placed

    @pytest.mark.asyncio
    async def test_allow_spreads_when_all_subnets_over_threshold(self, provider):
        init_spread_config("mrack.conf")
        # both over 95% used, together they still fit the job
        mock_subnets(provider, {"s1": 10, "s2": 10})
        reqs = subnet_reqs("ABC", ["s1", "s2"])

        await provider.validate_hosts(reqs)

        assert {req["subnet_ids"][0] for req in reqs} == {"s1", "s2"}

    @pytest.mark.asyncio
    async def test_allow_spreads_job_bigger_than_any_subnet(self, provider):
        init_spread_config("mrack.conf")
        cidrs = {"s1": "10.0.0.0/27", "s2": "10.0.0.32/27"}  # 27 usable IPs each
        mock_subnets(provider, {"s1": 10, "s2": 10}, cidrs)
        reqs = subnet_reqs([f"h{i}" for i in range(12)], ["s1", "s2"])

        await provider.validate_hosts(reqs)

        placed = [req["subnet_ids"][0] for req in reqs]
        assert sorted(Counter(placed).values()) == [6, 6]

    @pytest.mark.asyncio
    async def test_fails_when_no_subnet_has_free_ips(self, provider):
        init_spread_config("mrack.conf")
        mock_subnets(provider, {"s1": 0, "s2": 0})
        reqs = subnet_reqs("AB", ["s1", "s2"])

        with pytest.raises(ValidationError, match="No available networks"):
            await provider.validate_hosts(reqs)

    @pytest.mark.asyncio
    async def test_full_subnet_never_picked(self, provider):
        init_spread_config("mrack.conf")
        mock_subnets(provider, {"s1": 0, "s2": 200, "s3": 200})
        reqs = subnet_reqs("AB", ["s1", "s2", "s3"])

        await provider.validate_hosts(reqs)

        placed = {req["subnet_ids"][0] for req in reqs}
        assert len(placed) == 1
        assert placed <= {"s2", "s3"}

    @pytest.mark.asyncio
    async def test_threshold_uses_subnet_size(self, provider):
        init_spread_config("mrack.conf")
        # same free IPs: 15/27 used in the /27, 239/251 used in the /24
        mock_subnets(provider, {"small": 12, "big": 12}, {"small": "10.0.0.0/27"})
        reqs = subnet_reqs("AB", ["small", "big"])

        await provider.validate_hosts(reqs)

        assert [req["subnet_ids"] for req in reqs] == [["small"], ["small"]]

    @pytest.mark.asyncio
    async def test_threshold_read_from_mrack_conf(self, provider):
        init_spread_config("mrack_low_threshold.conf")
        # 151/251 used is over the configured 50% threshold
        mock_subnets(provider, {"used": 100, "fresh": 200})
        reqs = subnet_reqs("AB", ["used", "fresh"])

        await provider.validate_hosts(reqs)

        assert [req["subnet_ids"] for req in reqs] == [["fresh"], ["fresh"]]

    @pytest.mark.asyncio
    async def test_unknown_spread_value_behaves_as_allow(self, provider):
        init_spread_config("mrack_unknown_spread.conf")
        mock_subnets(provider, {"s1": 200, "s2": 200})
        reqs = subnet_reqs("ABC", ["s1", "s2"])

        await provider.validate_hosts(reqs)

        assert len({req["subnet_ids"][0] for req in reqs}) == 1

    @pytest.mark.asyncio
    async def test_single_subnet_must_hold_the_job(self, provider):
        init_spread_config("mrack.conf")
        # both under threshold, only s1 can hold all 14 hosts
        mock_subnets(provider, {"s1": 200, "s2": 13})
        reqs = subnet_reqs([f"h{i}" for i in range(14)], ["s1", "s2"])

        await provider.validate_hosts(reqs)

        assert {req["subnet_ids"][0] for req in reqs} == {"s1"}
