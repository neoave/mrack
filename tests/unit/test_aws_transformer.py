"""Tests for AWS Transformer - EC2 UserData support."""

from copy import deepcopy

import pytest

from mrack.config import ProvisioningConfig
from mrack.providers import providers
from mrack.providers.aws import PROVISIONER_KEY as AWS
from mrack.providers.aws import AWSProvider

from .mock_data import MockedAWSTransformer

DOMAIN = "example.test"

WIN_2019_USER_DATA = (
    "<powershell>\n"
    "$admin = [adsi]('WinNT://./administrator, user')\n"
    "$admin.PSBase.Invoke('SetPassword', 'Secret123')\n"
    "</powershell>"
)

WIN_2022_USER_DATA = (
    "<powershell>\n"
    "net user Administrator Secret123\n"
    "Restart-Service sshd\n"
    "</powershell>"
)


def _host(name, role, group, os, user_data=None):
    """Create a host metadata dict."""
    host = {"name": f"{name}.{DOMAIN}", "role": role, "group": group, "os": os}
    if user_data is not None:
        host["user_data"] = user_data
    return host


def _aws_provisioning_config(user_data=None):
    """Get provisioning config with AWS section for testing."""
    aws_cfg = {
        "images": {
            "rhel-8.5": "ami-rhel-8-5",
            "win-2019": "ami-win-2019",
            "win-2022": "ami-win-2022",
        },
        "flavors": {
            "ipaserver": "t2.medium",
            "ad": "t2.medium",
            "default": "t2.nano",
        },
        "keypair": "mrack-keypair.pem",
        "security_group": "sg-something",
        "security_groups": ["sg-something"],
        "credentials_file": "aws.key",
        "profile": "default",
        "spot": True,
        "instance_tags": {
            "Name": "mrack-runner",
            "mrack": "True",
            "Persistent": "False",
        },
    }
    if user_data is not None:
        aws_cfg["user_data"] = deepcopy(user_data)

    return ProvisioningConfig(
        {
            "aws": aws_cfg,
            "users": {
                "rhel-8.5": "cloud-user",
                "win-2019": "Administrator",
                "win-2022": "Administrator",
            },
        }
    )


class TestAWSTransformerSSMImage:
    """Test that SSM image definitions pass through the transformer correctly."""

    @pytest.mark.asyncio
    async def test_ssm_image_def_in_requirement(self):
        """SSM image dict should be passed through as-is into the requirement."""
        providers.register(AWS, AWSProvider)
        transformer = MockedAWSTransformer()

        ssm_path = (
            "/aws/service/ami-windows-latest/Windows_Server-2022-English-Full-Base"
        )
        ssm_image = {"ssm": ssm_path}
        aws_cfg = {
            "images": {
                "win-2022": ssm_image,
                "rhel-8.5": "ami-rhel-8-5",
            },
            "flavors": {"default": "t2.nano"},
            "keypair": "mrack-keypair.pem",
            "security_group": "sg-something",
            "security_groups": ["sg-something"],
            "credentials_file": "aws.key",
            "profile": "default",
            "spot": True,
            "instance_tags": {"Name": "mrack-runner"},
        }
        config = ProvisioningConfig(
            {"aws": aws_cfg, "users": {"win-2022": "Administrator"}}
        )
        hosts = [_host("ad", "ad", "ad", "win-2022")]
        metadata = {"domains": [{"name": DOMAIN, "type": "mixed", "hosts": hosts}]}
        await transformer.init(config, metadata)

        req = transformer.create_host_requirement(hosts[0])
        assert req["image"] == ssm_image


class TestAWSTransformerUserData:
    """Test the AWS Transformer's user_data handling."""

    @pytest.mark.asyncio
    async def _create_transformer(self, user_data=None):
        """Initialize the AWS transformer with mocked provider."""
        providers.register(AWS, AWSProvider)
        transformer = MockedAWSTransformer()
        config = _aws_provisioning_config(user_data=user_data)
        hosts = [
            _host("server", "master", "ipaserver", "rhel-8.5"),
            _host("ad", "ad", "ad", "win-2019"),
            _host("ad2", "ad", "ad", "win-2022"),
        ]
        metadata = {"domains": [{"name": DOMAIN, "type": "mixed", "hosts": hosts}]}
        await transformer.init(config, metadata)
        return transformer

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "config_user_data, meta_host, expected_user_data",
        [
            pytest.param(
                {"win-2019": WIN_2019_USER_DATA},
                _host("ad", "ad", "ad", "win-2019"),
                WIN_2019_USER_DATA,
                id="from_provisioning_config",
            ),
            pytest.param(
                None,
                _host("ad", "ad", "ad", "win-2019", user_data=WIN_2019_USER_DATA),
                WIN_2019_USER_DATA,
                id="from_host_metadata",
            ),
            pytest.param(
                {"win-2019": "<powershell>echo config</powershell>"},
                _host("ad", "ad", "ad", "win-2019", user_data=WIN_2019_USER_DATA),
                WIN_2019_USER_DATA,
                id="host_metadata_overrides_config",
            ),
            pytest.param(
                None,
                _host("ad", "ad", "ad", "win-2019"),
                None,
                id="none_when_not_configured",
            ),
            pytest.param(
                {"win-2019": WIN_2019_USER_DATA},
                _host("server", "master", "ipaserver", "rhel-8.5"),
                None,
                id="none_for_linux_host",
            ),
        ],
    )
    async def test_user_data_requirement(
        self, config_user_data, meta_host, expected_user_data
    ):
        """Test user_data is correctly resolved in host requirements."""
        transformer = await self._create_transformer(user_data=config_user_data)
        req = transformer.create_host_requirement(meta_host)
        err = (
            f"user_data mismatch: {repr(req.get('user_data'))}"
            f" != {repr(expected_user_data)}"
        )
        assert req.get("user_data") == expected_user_data, err

    @pytest.mark.asyncio
    async def test_user_data_for_multiple_windows_os(self):
        """Test user_data is resolved correctly per OS when multiple are configured."""
        transformer = await self._create_transformer(
            user_data={
                "win-2019": WIN_2019_USER_DATA,
                "win-2022": WIN_2022_USER_DATA,
            }
        )
        win19_req = transformer.create_host_requirement(
            _host("ad", "ad", "ad", "win-2019")
        )
        win22_req = transformer.create_host_requirement(
            _host("ad2", "ad", "ad", "win-2022")
        )
        assert win19_req.get("user_data") == WIN_2019_USER_DATA
        assert win22_req.get("user_data") == WIN_2022_USER_DATA

    @pytest.mark.asyncio
    async def test_other_fields_unaffected_by_user_data(self):
        """Test that adding user_data doesn't affect other requirement fields."""
        transformer = await self._create_transformer(
            user_data={"win-2019": WIN_2019_USER_DATA}
        )
        req = transformer.create_host_requirement(_host("ad", "ad", "ad", "win-2019"))
        assert req["name"] == f"ad.{DOMAIN}"
        assert req["os"] == "win-2019"
        assert req["group"] == "ad"
        assert req["image"] == "ami-win-2019"
        assert req["flavor"] == "t2.medium"
        assert req["security_group_ids"] == ["sg-something"]
        assert req["user_data"] == WIN_2019_USER_DATA
