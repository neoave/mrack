import os

import pytest

from mrack.actions.destroy import Destroy as DestroyAction
from mrack.actions.list import List as ListAction
from mrack.actions.output import Output as OutputAction
from mrack.actions.up import Up as UpAction
from mrack.host import STATUS_ACTIVE, STATUS_DELETED
from mrack.providers import aws, openstack, providers, static


@pytest.fixture()
def setup_providers():
    providers.register(aws.PROVISIONER_KEY, aws.AWSProvider)
    providers.register(openstack.PROVISIONER_KEY, openstack.OpenStackProvider)
    providers.register(static.PROVISIONER_KEY, static.StaticProvider)


class TestStaticProvider:
    @pytest.mark.asyncio
    async def test_up_action(
        self, provisioning_config, metadata, database, setup_providers
    ):
        up_action = UpAction(
            config=provisioning_config,
            metadata=metadata,
            db_driver=database,
        )
        await up_action.init(default_provider="static")
        await up_action.provision()

        assert database.hosts != {}

        num_metadata_hosts = len(metadata["domains"][0]["hosts"])
        assert len(database.hosts) == num_metadata_hosts

        for host in database.hosts.values():
            assert host.status == STATUS_ACTIVE

    @pytest.mark.asyncio
    async def test_list_action(self, database, setup_providers, caplog):
        list_action = ListAction(
            db_driver=database,
        )
        list_action.list()
        expected_lines = [
            "active fedora-30 f30.aiohabit.test "
            "f30.aiohabit.test 192.168.100.2 None None",
            "active fedora-31 f31.aiohabit.test "
            "f31.aiohabit.test 192.168.100.3 None None",
            "active fedora-32 f32.aiohabit.test "
            "f32.aiohabit.test 192.168.100.4 None None",
        ]
        for record, line in zip(caplog.records, expected_lines):
            assert record.message == line

    @pytest.mark.asyncio
    async def test_output_action(
        self, provisioning_config, metadata, database, setup_providers, cleandir
    ):
        workdir = os.getcwd()

        # Check that workdir is empty
        assert os.listdir(workdir) == []

        output_action = OutputAction(
            config=provisioning_config,
            metadata=metadata,
            db_driver=database,
            ansible_path=None,
            pytest_multihost_path=None,
        )
        await output_action.generate_outputs()

        # Check for generated files
        assert set(os.listdir(workdir)) == set(
            ["mrack-inventory.yaml", "pytest-multihost.yaml"]
        )

    @pytest.mark.asyncio
    async def test_destroy_action(
        self, provisioning_config, metadata, database, setup_providers
    ):
        destroy_action = DestroyAction(
            config=provisioning_config,
            metadata=metadata,
            db_driver=database,
        )
        await destroy_action.destroy()

        num_metadata_hosts = len(metadata["domains"][0]["hosts"])
        assert len(database.hosts) == num_metadata_hosts

        for host in database.hosts.values():
            assert host.status == STATUS_DELETED
