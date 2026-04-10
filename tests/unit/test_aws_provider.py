"""Tests for AWS Provider - SSM parameter image resolution."""

from unittest.mock import MagicMock, patch

import pytest

from mrack.errors import ValidationError
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
