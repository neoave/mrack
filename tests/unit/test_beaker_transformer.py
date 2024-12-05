import pytest

from mrack.providers import providers
from mrack.providers.beaker import PROVISIONER_KEY as BEAKER
from mrack.providers.beaker import BeakerProvider

from .mock_data import MockedBeakerTransformer, provisioning_config
from .utils import get_file_path


class TestBeakerTransformer:
    """Test the Beaker Transformer"""

    default_prio = "Normal"
    domain_name = "example.test"
    ad_domain_name = "ad.test"
    cat_release = "cat /etc/redhat-release"
    wget = "wget redhat.com"
    default_whiteboard = "This job has been created using mrack."
    default_tasks = [
        {
            "name": "/distribution/dummy",
            "role": "STANDALONE",
            "params": [
                "RSTRNT_DISABLED=10_avc_check",
            ],
        }
    ]
    default_retention_tag = "audit"
    default_product = "[internal]"
    key_one = get_file_path("key_one")
    key_two = get_file_path("key_two")
    raw_maximal_ksappend = (
        [
            "%pre\npre_dummy\n%end\nscript_dummy\n%post\npost_dummy\n%end",
        ]
        + [
            '%post\nmkdir -p /root/.ssh\ncat >>/root/.ssh/authorized_keys << "__EOF__"',
        ]
        + [
            "# keys added by mrack:\nssh-rsa key_one_content\nssh-rsa key_two_content",
        ]
        + [
            "# end section of keys added by mrack\n__EOF__\nrestorecon -R /root/.ssh",
        ]
        + [
            "chmod go-w /root /root/.ssh /root/.ssh/authorized_keys\n%end",
        ]
    )
    maximal_ksappend = [
        "\n".join(raw_maximal_ksappend),
    ]
    fedora = {
        "name": f"fedora.{domain_name}",
        "role": "client",
        "group": "client",
        "os": "fedora-latest",
        "restraint_id": 1,
        "beaker": {
            "ks_meta": "FEDORA_HOST_KS_META",
            "kernel_options": "FEDORA_KERNEL_OPTIONS",
            "kernel_options_post": "FEDORA_KERNEL_OPTIONS_POST",
            "job_owner": "FEDORA",
            "ks_append": {
                "pre-install": "%pre\npre_dummy\n%end",
                "script": "script_dummy",
                "post-install": "%post\npost_dummy\n%end",
            },
            "pubkeys": [key_one, key_two],
            "tasks": [
                {
                    "name": "/distribution/check-install",
                    "role": "SERVER",
                }
            ],
        },
    }

    fedora_server = {
        "name": f"fedora-server.{domain_name}",
        "role": "server",
        "group": "server",
        "os": "fedora-latest",
        "restraint_id": 1,
        "beaker": {
            "ks_meta": "FEDORA_HOST_KS_META",
            "retention_tag": "active",
            "product": "cpe:/a:redhat:jboss_operations_network:2.3",
            "tasks": [{"name": "/distribution/sleep", "role": "STANDALONE"}],
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

    centos_client = {
        "name": f"centos-client.{domain_name}",
        "role": "client",
        "group": "ipaclient",
        "os": "c9s",
        "restraint_id": 2,
        "beaker": {
            "ks_append": [
                cat_release,
            ],
            "retention_tag": "scratch",
            "product": "",
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
                    fedora_server,
                    centos,
                    centos_client,
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
        "meta_host, exp_values",  # noqa: E501
        [
            (
                fedora,
                {
                    "distro": "Fedora-36%",
                    "variant": "Server",
                    "ks_meta": "FEDORA_HOST_KS_META",
                    "job_owner": "FEDORA",
                    "job_group": "client",
                    "ks_append": maximal_ksappend,
                    "kernel_options": "FEDORA_KERNEL_OPTIONS",
                    "kernel_options_post": "FEDORA_KERNEL_OPTIONS_POST",
                    "whiteboard": default_whiteboard,
                    "priority": default_prio,
                    "tasks": [
                        {"name": "/distribution/check-install", "role": "SERVER"}
                    ],
                    "retention_tag": default_retention_tag,
                    "product": default_product,
                },
            ),
            (
                fedora_server,
                {
                    "distro": "Fedora-36%",
                    "variant": "Server",
                    "ks_meta": "FEDORA_HOST_KS_META",
                    "job_group": "server",
                    "ks_append": default_ks_append,
                    "whiteboard": default_whiteboard,
                    "priority": default_prio,
                    "retention_tag": "active",
                    "product": "cpe:/a:redhat:jboss_operations_network:2.3",
                    "tasks": [{"name": "/distribution/sleep", "role": "STANDALONE"}],
                },
            ),
            (
                centos,
                {
                    "distro": "CentOS-Stream-9%",
                    "variant": "BaseOS",
                    "job_group": "ipaserver",
                    "ks_meta": "PROV_CONF_CENTOS_KS_META",
                    "ks_append": ["%post\ncat /etc/redhat-release\n%end"],
                    "whiteboard": default_whiteboard,
                    "priority": default_prio,
                    "tasks": default_tasks,
                    "retention_tag": default_retention_tag,
                    "product": default_product,
                },
            ),
            (
                centos_client,
                {
                    "distro": "CentOS-Stream-9%",
                    "variant": "BaseOS",
                    "job_group": "ipaclient",
                    "ks_meta": "PROV_CONF_CENTOS_KS_META",
                    "ks_append": ["%post\ncat /etc/redhat-release\n%end"],
                    "whiteboard": default_whiteboard,
                    "priority": default_prio,
                    "tasks": default_tasks,
                    "retention_tag": "scratch",
                    "product": "",
                },
            ),
            # default variant should be there,
            # windows distro does not exist so host['os'] should be copied
            (
                windows,
                {
                    "distro": "win-2022",
                    "variant": "BaseOS",
                    "job_group": "ad_root",
                    "ks_meta": "PROV_CONF_DEFAULT",
                    "ks_append": default_ks_append,
                    "whiteboard": "BEAKER DOES NOT SUPPORT WINDOWS THIS JOB MUST FAIL",
                    "priority": "ULTRAHIGH",
                    "tasks": default_tasks,
                    "retention_tag": default_retention_tag,
                    "product": default_product,
                },
            ),
            (
                rhel86,
                {
                    "distro": "RHEL-8.6%",
                    "variant": "BaseOS",
                    "job_group": "ipaserver",
                    "ks_meta": "PROV_CONF_RHEL86_KS_META",
                    "ks_append": [
                        "%post\ncat /etc/redhat-release\nwget redhat.com\n%end"
                    ],
                    "whiteboard": default_whiteboard,
                    "priority": default_prio,
                    "tasks": default_tasks,
                    "retention_tag": default_retention_tag,
                    "product": default_product,
                },
            ),
        ],
    )
    async def test_beaker_requirement(
        self,
        meta_host,
        exp_values,
    ):
        """Test expected Beaker VM variant and distro"""
        beaker_req_keys = [
            "distro",
            "variant",
            "ks_meta",
            "ks_append",
            "kernel_options",
            "kernel_options_post",
            "whiteboard",
            "priority",
            "tasks",
            "retention_tag",
            "product",
        ]
        bkr_transformer = await self.create_transformer()
        req = bkr_transformer.create_host_requirement(meta_host)
        for key in beaker_req_keys:
            err = (
                f"Mismatch of transformed value and expected value[{key}]: "
                f"{req.get(key)} != {exp_values.get(key)}"
            )
            assert req.get(key) == exp_values.get(key), err

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
