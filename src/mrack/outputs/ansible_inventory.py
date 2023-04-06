# Copyright 2020 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Ansible inventory output module."""
import logging
import os
import typing
from copy import deepcopy

from mrack.errors import ConfigError
from mrack.outputs.utils import get_external_id
from mrack.utils import (
    get_fqdn,
    get_host_from_metadata,
    get_os_type,
    get_password,
    get_shortname,
    get_ssh_key,
    get_ssh_options,
    get_username,
    is_windows_host,
    save_yaml,
    ssh_options_to_cli,
)

DEFAULT_INVENTORY_PATH = "mrack-inventory.yaml"
DEFAULT_INVENTORY_LAYOUT: typing.Dict[str, typing.Dict] = {
    "all": {"children": {}, "hosts": {}}
}

logger = logging.getLogger(__name__)


def copy_meta_attrs(host, meta_host, attrs):
    """Copy attributes from host metadata entry and prefixing them with meta."""
    for attr in attrs:
        val = meta_host.get(attr)
        if val:
            host[f"meta_{attr}"] = val


def ensure_all_group(inventory):
    """Ensure that inventory has group "all" with both "hosts" and "children"."""
    if "all" not in inventory:
        inventory["all"] = {
            "children": {},
            "hosts": {},
        }
    all_group = inventory["all"]
    if "children" not in all_group:
        all_group["children"] = {}
    if "hosts" not in all_group:
        all_group["hosts"] = {}
    return all_group


def get_group(inventory, groupname):
    """Get group from inventory, return group or None."""
    groups = inventory.keys()
    found = None
    for g_name in groups:
        group = inventory[g_name]
        if g_name == groupname:
            found = group
        else:
            if "children" in group:
                found = get_group(group["children"], groupname)
        if found is not None:
            break
    return found


def add_to_group(inventory, groupname, hostname):
    """
    Find a group in inventory layout and add a host to it.

    Returns group or None if it doesn't exist.
    """
    group = get_group(inventory, groupname)
    if group is None:
        return None

    if "hosts" not in group:
        group["hosts"] = {}
    group["hosts"][hostname] = {}
    return group


def add_group(inventory, groupname, hostname=None):
    """Add a group to inventory, optionally add it with hostname."""
    all_group = inventory["all"]
    group = {}
    if hostname:
        group["hosts"] = {hostname: {}}
    all_group["children"][groupname] = group
    return group


class AnsibleInventoryOutput:
    """
    Generate Ansible inventory with provisioned machines.

    The resulting inventory combines data from provisioning config, job metadata
    files and information in DB.
    """

    def __init__(self, config, db, metadata, path=None):  # pylint: disable=invalid-name
        """Init the output module."""
        self._config = config
        self._db = db
        self._metadata = metadata
        self._path = path or DEFAULT_INVENTORY_PATH

    def create_ansible_host(self, name):
        """Create host entry for Ansible inventory."""
        # pylint: disable=too-many-locals
        meta_host, meta_domain = get_host_from_metadata(self._metadata, name)
        db_host = self._db.hosts[name]

        ip_addr = db_host.ip_addr
        ansible_host = get_external_id(db_host, meta_host, self._config)

        python = (
            self._config["python"].get(meta_host["os"])
            or self._config["python"]["default"]
        )

        ansible_user = get_username(db_host, meta_host, self._config)
        password = get_password(db_host, meta_host, self._config)
        ssh_key = get_ssh_key(db_host, meta_host, self._config)
        ssh_options = get_ssh_options(db_host, self._metadata, self._config)
        dom_name = meta_domain["name"]

        # Common attributes
        dc_list = [f"DC={dc}" for dc in dom_name.split(".")]
        host_info = {
            "ansible_host": ansible_host,
            "ansible_python_interpreter": python,
            "ansible_user": ansible_user,
            "meta_os_type": get_os_type(meta_host),
            "meta_fqdn": f"{get_fqdn(name, dom_name)}",
            "meta_hostname": get_shortname(name),
            "meta_domain": f"{get_fqdn(name, dom_name).split('.', 1)[1]}",
            "meta_provider": db_host.provider.name,
            "meta_provider_id": db_host.host_id,
            "meta_ip": ip_addr,
            "meta_dc_record": ",".join(dc_list),
        }

        if "restraint_id" in meta_host:
            host_info.update({"meta_restraint_id": meta_host["restraint_id"]})

        copy_meta_attrs(host_info, meta_host, ["os", "role", "netbios"])

        if "parent" in meta_domain:
            host_info["meta_parent_domain"] = meta_domain["parent"]

        if ssh_key:
            host_info["ansible_ssh_private_key_file"] = os.path.abspath(ssh_key)

        if ssh_options:
            ssh_common_args = " ".join(ssh_options_to_cli(ssh_options))
            host_info["ansible_ssh_common_args"] = ssh_common_args

        if password:
            host_info["ansible_password"] = password

        if db_host.provider.name in ("docker", "podman"):
            host_info.update({"ansible_user": "root"})  # TODO make it configurable

        if db_host.meta_extra:
            for key, value in db_host.meta_extra.items():
                host_info.update({key: value})

        if is_windows_host(meta_host):
            if "netbios" in meta_host:
                host_info.update({"meta_netbios": meta_host["netbios"]})

            host_info.update(
                {
                    "ansible_port": 5986,
                    "ansible_connection": "winrm",
                    "ansible_winrm_server_cert_validation": "ignore",
                    "meta_domain_level": meta_host.get("domain_level", "top"),
                }
            )

        for key, val in meta_host.items():
            if key.startswith("meta_"):
                host_info[key] = val

        glob_ansible_inv = deepcopy(self._metadata.get("ansible_inventory", {}))
        dom_ansible_inv = deepcopy(meta_domain.get("ansible_inventory", {}))
        host_ansible_inv = deepcopy(meta_host.get("ansible_inventory", {}))

        if any([glob_ansible_inv, dom_ansible_inv, host_ansible_inv]):
            host_info.update(glob_ansible_inv | dom_ansible_inv | host_ansible_inv)

        return host_info

    def get_inventory_layout(self):
        """Get Ansible inventory layout."""
        layout = self._metadata.get("config", {}).get("ansible", {}).get("layout")
        if layout is None:
            return self._config.get("inventory_layout", DEFAULT_INVENTORY_LAYOUT)

        return layout

    def create_inventory(self):
        """Create the Ansible inventory in dict form."""
        provisioned = self._db.hosts
        inventory = deepcopy(self.get_inventory_layout())
        if not isinstance(inventory, dict):
            raise ConfigError("Inventory layout should be a dictionary")
        all_group = ensure_all_group(inventory)

        for host in provisioned.values():
            meta_host, _meta_domain = get_host_from_metadata(self._metadata, host.name)
            if meta_host is None:
                continue

            # Groups can be defined in both "groups" and "group" variable.
            groups = meta_host.get("groups", [])
            group = meta_host.get("group")
            if group and group not in groups:
                groups.append(group)

            # Add only a reference custom groups
            for group in groups:
                added = add_to_group(inventory, group, host.name)
                if not added:  # group doesn't exist
                    add_group(inventory, group, host.name)

            # Main record belongs in "all" group
            all_group["hosts"][host.name] = self.create_ansible_host(host.name)
        return inventory

    def create_output(self):
        """Create the target output file."""
        inventory = self.create_inventory()
        save_yaml(self._path, inventory)
        if self._path:
            logger.info(f"Created: {self._path}")
        return inventory
