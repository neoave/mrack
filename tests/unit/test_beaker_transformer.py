import pytest

from mrack.providers import providers
from mrack.providers.beaker import PROVISIONER_KEY as BEAKER
from mrack.providers.beaker import BeakerProvider

from .mock_data import MockedBeakerTransformer, provisioning_config


class TestBeakerTransformer:
    """Test the Beaker Transformer"""

    default_prio = "Normal"
    domain_name = "example.test"
    ad_domain_name = "ad.test"
    cat_release = "cat /etc/redhat-release"
    wget = "wget redhat.com"
    default_whiteboard = "This job has been created using mrack."

    fedora = {
        "name": f"fedora.{domain_name}",
        "role": "client",
        "group": "client",
        "os": "fedora-latest",
        "restraint_id": 1,
        "beaker": {
            "ks_meta": "FEDORA_HOST_KS_META",
            "tasks": [
                {
                    "name": "/distribution/check-install",
                    "role": "SERVER",
                }
            ],
        },
    }

    centos = {
        "name": f"centos.{domain_name}",
        "role": "server",
        "group": "ipaserver",
        "os": "c9s",
        "restraint_id": 2,
        "beaker": {
            "ks_append": [
                cat_release,
            ],
        },
    }

    rhel86 = {
        "name": f"rhel86.{domain_name}",
        "role": "server",
        "group": "ipaserver",
        "os": "rhel-8.6",
        "restraint_id": 3,
        "beaker": {
            "ks_append": [
                cat_release,
                wget,
            ],
        },
    }

    windows = {
        "name": f"ad1.{ad_domain_name}",
        "role": "ad",
        "group": "ad_root",
        "os": "win-2022",
        "domain_level": "top",
        "netbios": ad_domain_name.split(".", maxsplit=1)[0].upper(),
        "beaker": {
            "whiteboard": "BEAKER DOES NOT SUPPORT WINDOWS THIS JOB MUST FAIL",
            "priority": "ULTRAHIGH",
        },
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

    default_ks_append = []

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
        "meta_host,exp_distro,exp_variant,exp_ks_meta,exp_ks_append,exp_whiteboard,exp_prio",  # noqa: E501
        [
            (
                fedora,
                "Fedora-36%",
                "Server",
                "FEDORA_HOST_KS_META",
                default_ks_append,
                default_whiteboard,
                default_prio,
            ),
            (
                centos,
                "CentOS-Stream-9%",
                "BaseOS",
                "PROV_CONF_CENTOS_KS_META",
                ["%post\ncat /etc/redhat-release\n%end"],
                default_whiteboard,
                default_prio,
            ),
            # default variant should be there,
            # windows distro does not exist so host['os'] should be copied
            (
                windows,
                "win-2022",
                "BaseOS",
                "PROV_CONF_DEFAULT",
                default_ks_append,
                "BEAKER DOES NOT SUPPORT WINDOWS THIS JOB MUST FAIL",
                "ULTRAHIGH",
            ),
            (
                rhel86,
                "RHEL-8.6%",
                "BaseOS",
                "PROV_CONF_RHEL86_KS_META",
                ["%post\ncat /etc/redhat-release\nwget redhat.com\n%end"],
                default_whiteboard,
                default_prio,
            ),
        ],
    )
    async def test_beaker_requirement(
        self,
        meta_host,
        exp_distro,
        exp_variant,
        exp_ks_meta,
        exp_ks_append,
        exp_whiteboard,
        exp_prio,
    ):
        """Test expected Beaker VM variant and distro"""
        bkr_transformer = await self.create_transformer()
        req = bkr_transformer.create_host_requirement(meta_host)
        assert req.get("distro") == exp_distro
        assert req.get("variant") == exp_variant
        assert req.get("ks_meta") == exp_ks_meta
        assert req.get("ks_append") == exp_ks_append
        assert req.get("whiteboard") == exp_whiteboard
        assert req.get("priority") == exp_prio

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
