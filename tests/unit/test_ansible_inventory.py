import pytest

from mrack.errors import ConfigError
from mrack.outputs.ansible_inventory import AnsibleInventoryOutput, get_group

from .mock_data import (
    common_inventory_layout,
    create_metadata,
    get_db_from_metadata,
    provisioning_config,
)


def ensure_all_groups_present(metadata, inventory):
    """
    Ensure that all groups defined in metadata hosts objects are present.

    And contain the host
    """
    for domain in metadata["domains"]:
        for meta_host in domain["hosts"]:
            for groupname in meta_host.get("groups"):
                group = get_group(inventory, groupname)
                assert group, "All defined groups in host must be in inventory"
                assert "hosts" in group, "Group must contain hosts dict"
                hosts = group["hosts"]
                assert meta_host["name"] in hosts, "Group must contain the host"


def ensure_hosts_in_all_group(db, inventory):
    """Ensure that group 'all' contains all hosts from DB."""
    all_group = inventory["all"]
    hosts = all_group["hosts"]
    db_hosts = db.hosts

    assert len(db_hosts) > 0, "Make sure we do not work on empty data set"

    required_attrs = [
        "ansible_host",
        "ansible_python_interpreter",
        "ansible_user",
        "meta_domain",
        "meta_fqdn",
        "meta_os",
        "meta_ip",
        "meta_provider_id",
        "meta_role",
    ]

    for name, dbhost in db_hosts.items():
        assert dbhost.name in hosts, "All hosts must be present in inventory"

        invhost = hosts[dbhost.name]

        assert dbhost.ip_addr == invhost["meta_ip"], "IP from DB in inventory"
        for attr in required_attrs:
            assert attr in required_attrs, "All required attrs are in host definition"


@pytest.fixture()
def metadata():
    return create_metadata(ipaservers=1, ipaclients=1, ads=1)


@pytest.fixture()
def db(metadata):
    return get_db_from_metadata(metadata)


def empty_layout():
    return {
        "all": {},
    }


class TestAnsibleInventory:
    @pytest.mark.parametrize(
        "layout",
        [
            # It is more tolerant with falsy values
            common_inventory_layout(),
            None,
            {},
            empty_layout(),
            [],
            False,
        ],
    )
    def test_layouts(self, layout, db, metadata):

        config = provisioning_config(layout)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()

        assert "all" in inventory, "Inventory must have group 'all'"
        all_group = inventory["all"]
        assert "hosts" in all_group, "All group must have 'hosts' dict"
        assert "children" in all_group, "All group must have 'children' dict"

        ensure_all_groups_present(metadata, inventory)
        ensure_hosts_in_all_group(db, inventory)

    @pytest.mark.parametrize(
        "layout",
        [
            # Non-dict truthy values are not valid
            ["test"],
            "test",
            True,
            (True, False),
        ],
    )
    def test_invalid_layouts(self, layout, db, metadata):

        config = provisioning_config(layout)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)

        with pytest.raises(ConfigError) as excinfo:
            ans_inv.create_inventory()
        assert "dictionary" in str(excinfo.value)
