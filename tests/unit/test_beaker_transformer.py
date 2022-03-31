import pytest

from mrack.providers import providers
from mrack.providers.beaker import PROVISIONER_KEY as BEAKER
from mrack.providers.beaker import BeakerProvider

from .mock_data import MockedBeakerTransformer, provisioning_config


class TestBeakerTransformer:
    """Test the Beaker Transformer"""

    domain_name = "example.test"
    ad_domain_name = "ad.test"

    fedora = {
        "name": f"fedora.{domain_name}",
        "role": "client",
        "group": "client",
        "os": "fedora-latest",
        "restraint_id": 1,
    }

    centos = {
        "name": f"centos.{domain_name}",
        "role": "server",
        "group": "ipaserver",
        "os": "c9s",
        "restraint_id": 2,
    }

    rhel86 = {
        "name": f"rhel86.{domain_name}",
        "role": "server",
        "group": "ipaserver",
        "os": "rhel-8.6",
        "restraint_id": 3,
    }

    windows = {
        "name": f"ad1.{ad_domain_name}",
        "role": "ad",
        "group": "ad_root",
        "os": "win-2022",
        "domain_level": "top",
        "netbios": ad_domain_name.split(".", maxsplit=1)[0].upper(),
    }

    hosts_metadata = {
        "domains": [
            {
                "name": domain_name,
                "type": "linux",
                "hosts": [
                    fedora,
                    centos,
                    rhel86,
                ],
            },
            {
                "name": ad_domain_name,
                "type": "linux",
                "hosts": [
                    windows,
                ],
            },
        ],
    }

    @pytest.mark.asyncio
    async def create_transformer(self, legacy=False):
        """Initialize the Beaker transformer"""
        providers.register(BEAKER, BeakerProvider)
        res = MockedBeakerTransformer()
        config = provisioning_config()
        if legacy:
            del config["beaker"]["distro_variants"]

        await res.init(
            config,
            self.hosts_metadata,
        )
        return res

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "meta_host,exp_distro,exp_variant",
        [
            (fedora, "Fedora-36%", "Server"),
            (centos, "CentOS-Stream-9%", "BaseOS"),
            # default variant should be there,
            # windows distro does not exist so host['os'] should be copied
            (windows, "win-2022", "BaseOS"),
            (rhel86, "RHEL-8.6%", "BaseOS"),
        ],
    )
    async def test_beaker_requirement(self, meta_host, exp_distro, exp_variant):
        """Test expected Beaker VM variant and distro"""
        bkr_transformer = await self.create_transformer()
        req = bkr_transformer.create_host_requirement(meta_host)
        assert req.get("distro") == exp_distro
        assert req.get("variant") == exp_variant

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "meta_host,exp_distro,exp_variant",
        [
            (fedora, "Fedora-36%", "Server"),
            (centos, "CentOS-Stream-9%", "Server"),
            # default variant should be there,
            # windows distro does not exist so host['os'] should be copied
            (windows, "win-2022", "Server"),
            (rhel86, "RHEL-8.6%", "BaseOS"),
        ],
    )
    # legacy test defaults to Server variant
    async def test_beaker_requirement_legacy(self, meta_host, exp_distro, exp_variant):
        """Test expected Beaker VM variant and distro"""
        bkr_transformer = await self.create_transformer(legacy=True)
        req = bkr_transformer.create_host_requirement(meta_host)
        assert req.get("distro") == exp_distro
        assert req.get("variant") == exp_variant
