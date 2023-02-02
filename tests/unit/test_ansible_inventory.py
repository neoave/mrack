from copy import deepcopy

import pytest

from mrack.errors import ConfigError
from mrack.outputs.ansible_inventory import AnsibleInventoryOutput, get_group

from .mock_data import (
    common_inventory_layout,
    create_metadata,
    get_db_from_metadata,
    metadata_extra,
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


@pytest.fixture()
def db_meta_extra(metadata):
    return get_db_from_metadata(
        metadata,
        host_extra={  # Sample data
            "meta_compose_id": "ID.0-20220317.0",
            "meta_compose_url": "http://dummy.com/compose/compose_id",
        },
    )


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

    def test_meta_extra(self, db_meta_extra, metadata):

        config = provisioning_config()
        ans_inv = AnsibleInventoryOutput(config, db_meta_extra, metadata)
        inventory = ans_inv.create_inventory()
        first_hostname = metadata["domains"][0]["hosts"][0]["name"]

        first_host = inventory["all"]["hosts"][first_hostname]

        assert (
            "meta_compose_url" in first_host
        ), "Host must have 'meta_compose_url' field"
        assert "meta_compose_id" in first_host, "Host must have 'meta_compose_id' field"

    def test_not_meta_extra(self, db, metadata):
        """
        Because some images (such as Windows images) don't have extra meta data fields
        like meta_compose_id and meta_compose_url, inventory shouldn't output them
        if not passed.
        """

        config = provisioning_config()
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()
        first_hostname = metadata["domains"][0]["hosts"][0]["name"]

        first_host = inventory["all"]["hosts"][first_hostname]

        assert (
            "meta_compose_url" not in first_host
        ), "Host must NOT have 'meta_compose_url' field"
        assert (
            "meta_compose_id" not in first_host
        ), "Host must NOT have 'meta_compose_id' field"

    def test_arbitrary_meta_attrs(self):
        """
        Test that inventory has meta_$something attribute if user defined it in job
        metadata file. Also test that they override the default meta attrs, e.g.,
        meta_os.
        """
        metadata = metadata_extra()
        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()

        srv1 = inventory["all"]["hosts"]["srv1.example.test"]

        assert "meta_readonly_dc" in srv1
        assert srv1["meta_readonly_dc"] == "yes"
        assert "meta_something_else" in srv1
        assert srv1["meta_something_else"] == "val"
        assert srv1["meta_os"] == "windows-2019"

        srv2 = inventory["all"]["hosts"]["srv2.example.test"]

        assert "meta_something_else" not in srv2
        assert "meta_readonly_dc" in srv2
        assert srv2["meta_readonly_dc"] == "no"
        assert srv2["meta_os"] == "fedora-32"

    def test_arbitrary_attrs(self):
        """
        Test that values defined in `ansible_inventory` dictionary in host part
        of job metadata file gets into host attributes in generated ansible
        inventory.
        """
        metadata = metadata_extra()
        m_srv1 = metadata["domains"][0]["hosts"][0]
        m_srv2 = metadata["domains"][0]["hosts"][1]
        m_srv1["ansible_inventory"] = {
            "readonly_dc": "yes",
            "something_else": "for_fun",
        }
        m_srv2["ansible_inventory"] = {
            "no_ca": "yes",
            "something_else": "for_fun",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()

        srv1 = inventory["all"]["hosts"]["srv1.example.test"]

        assert "readonly_dc" in srv1
        assert srv1["readonly_dc"] == "yes"
        assert "something_else" in srv1
        assert srv1["something_else"] == "for_fun"

        srv2 = inventory["all"]["hosts"]["srv2.example.test"]

        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "yes"
        assert srv2["something_else"] == "for_fun"

    def test_domain_arbitrary_attrs(self):
        """
        Test that values defined in `ansible_inventory` dictionary in domain
        section of job metadata file gets into host attributes in generated ansible
        inventory to each host of affected domain.
        """
        metadata = metadata_extra()
        metadata["domains"][0]["ansible_inventory"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()

        srv1 = inventory["all"]["hosts"]["srv1.example.test"]

        assert "something_else" in srv1
        assert srv1["something_else"] == "not_funny"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "no"

        srv2 = inventory["all"]["hosts"]["srv2.example.test"]

        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "no"
        assert srv2["something_else"] == "not_funny"

    def test_domain_arbitrary_attrs_override(self):
        """
        Test that values defined in `ansible_inventory` dictionary in domain
        section of job metadata file gets into host attributes in generated ansible
        inventory and can be overriden by attributes in host section.
        """
        metadata = metadata_extra()
        metadata["domains"][0]["ansible_inventory"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }
        m_srv1 = metadata["domains"][0]["hosts"][0]
        m_srv2 = metadata["domains"][0]["hosts"][1]
        m_srv1["ansible_inventory"] = {
            "readonly_dc": "yes",
        }
        m_srv2["ansible_inventory"] = {
            "no_ca": "yes",
            "something_else": "for_fun",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()

        srv1 = inventory["all"]["hosts"]["srv1.example.test"]

        assert "readonly_dc" in srv1
        assert srv1["readonly_dc"] == "yes"
        assert "something_else" in srv1
        assert srv1["something_else"] == "not_funny"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "no"

        srv2 = inventory["all"]["hosts"]["srv2.example.test"]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "yes"
        assert srv2["something_else"] == "for_fun"

    def test_global_arbitrary_attrs(self):
        """
        Test that values defined in `ansible_inventory` dictionary in global
        section of job metadata file gets into host attributes in generated ansible
        inventory to each host in metadata.
        """
        metadata = metadata_extra()
        metadata["ansible_inventory"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()

        srv1 = inventory["all"]["hosts"]["srv1.example.test"]

        assert "readonly_dc" not in srv1
        assert "something_else" in srv1
        assert srv1["something_else"] == "not_funny"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "no"

        srv2 = inventory["all"]["hosts"]["srv2.example.test"]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "no"
        assert srv2["something_else"] == "not_funny"

    def test_global_arbitrary_attrs_domain_override(self):
        """
        Test that values defined in `ansible_inventory` dictionary in global
        section of job metadata file gets into host attributes in generated ansible
        inventory to each host in metadata and can be overriden by domain records.
        """
        metadata = metadata_extra()
        metadata["ansible_inventory"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }

        metadata["domains"][0]["ansible_inventory"] = {
            "no_ca": "yes",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()

        srv1 = inventory["all"]["hosts"]["srv1.example.test"]

        assert "something_else" in srv1
        assert srv1["something_else"] == "not_funny"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "yes"

        srv2 = inventory["all"]["hosts"]["srv2.example.test"]

        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "yes"
        assert srv2["something_else"] == "not_funny"

    def test_global_arbitrary_attrs_host_override(self):
        """
        Test that values defined in `ansible_inventory` dictionary in global
        section of job metadata file gets into host attributes in generated ansible
        inventory to each host in metadata and can be overriden by host records.
        """
        metadata = metadata_extra()
        metadata["ansible_inventory"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }

        metadata["domains"][0]["ansible_inventory"] = {
            "no_ca": "yes",
        }

        m_srv1 = metadata["domains"][0]["hosts"][0]
        m_srv2 = metadata["domains"][0]["hosts"][1]
        m_srv1["ansible_inventory"] = {
            "readonly_dc": "yes",
        }
        m_srv2["ansible_inventory"] = {
            "no_ca": "whatever",
            "something_else": "host_value",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()

        srv1 = inventory["all"]["hosts"]["srv1.example.test"]

        assert "readonly_dc" in srv1
        assert srv1["readonly_dc"] == "yes"
        assert "something_else" in srv1
        assert srv1["something_else"] == "not_funny"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "yes"

        srv2 = inventory["all"]["hosts"]["srv2.example.test"]

        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "whatever"
        assert srv2["something_else"] == "host_value"

    def test_global_arbitrary_attrs_host_override_multiple_domains(self):
        """
        Test that values defined in `ansible_inventory` dictionary in global
        section of job metadata file gets into host attributes in generated ansible
        inventory to each host in metadata. This particular check aims to
        make sure the domain records are affecting only hosts in domain
        where they suppose to affect the host records.
        Secondary domain does has to contain attributes set on global level.
        """
        metadata = metadata_extra()
        metadata["ansible_inventory"] = {
            "no_ca": "no",
            "something_else": "default_global",
        }

        metadata["domains"].append(deepcopy(metadata["domains"][0]))
        for host in metadata["domains"][-1]["hosts"]:
            host["name"] = f"d1-{host['name']}"

        metadata["domains"][0]["ansible_inventory"] = {
            "no_ca": "yes",  # change the value only for one domain
            "something_else": "domain_0_value",  # change the value only for one domain
        }

        d0_m_srv1 = metadata["domains"][0]["hosts"][0]
        d0_m_srv2 = metadata["domains"][0]["hosts"][1]
        d0_m_srv1["ansible_inventory"] = {
            "readonly_dc": "yes",
        }
        d0_m_srv2["ansible_inventory"] = {
            "no_ca": "whatever",
            "something_else": "host_value",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        ans_inv = AnsibleInventoryOutput(config, db, metadata)
        inventory = ans_inv.create_inventory()

        srv1 = inventory["all"]["hosts"]["srv1.example.test"]
        assert "readonly_dc" in srv1
        assert srv1["readonly_dc"] == "yes"
        assert "something_else" in srv1
        assert srv1["something_else"] == "domain_0_value"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "yes"

        srv2 = inventory["all"]["hosts"]["srv2.example.test"]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "whatever"
        assert srv2["something_else"] == "host_value"

        d1_srv1 = inventory["all"]["hosts"]["d1-srv1.example.test"]
        assert "no_ca" in d1_srv1
        assert "readonly_dc" not in d1_srv1
        assert "something_else" in d1_srv1
        assert d1_srv1["no_ca"] == "no"
        assert d1_srv1["something_else"] == "default_global"

        d1_srv2 = inventory["all"]["hosts"]["d1-srv2.example.test"]
        assert "no_ca" in d1_srv2
        assert "something_else" in d1_srv2
        assert d1_srv2["no_ca"] == "no"
        assert d1_srv2["something_else"] == "default_global"
