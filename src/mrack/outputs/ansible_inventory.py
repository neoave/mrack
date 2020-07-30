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

from copy import deepcopy

from mrack.outputs.utils import resolve_hostname
from mrack.utils import (
    get_host_from_metadata,
    get_password,
    get_ssh_key,
    get_username,
    is_windows_host,
    save_yaml,
)

DEFAULT_INVENTORY_PATH = "mrack-inventory.yaml"
DEFAULT_INVENTORY_LAYOUT = {"all": {"children": {}, "hosts": {}}}


def copy_meta_attrs(host, meta_host, attrs):
    """Copy attributes from host metadata entry and prefixing them with meta."""
    for attr in attrs:
        val = meta_host.get(attr)
        if val:
            host[f"meta_{attr}"] = val


def find_group(inventory, group_names, top=True):
    """Find first matching group in inventory which has one of the provided names."""
    if not inventory:
        return None

    groups = inventory.keys()
    for group in groups:
        if group in group_names:
            return inventory[group]

    for group in groups:
        g = inventory[group]

        if "children" not in g:
            continue

        found = find_group(g["children"], group_names, top=False)
        if found:
            return found

    if top:
        return inventory["all"]

    return None


class AnsibleInventoryOutput:
    """
    Generate Ansible inventory with provisioned machines.

    The resulting inventory combines data from provisioning config, job metadata
    files and information in DB.
    """

    def __init__(self, config, db, metadata, path=DEFAULT_INVENTORY_PATH):
        """Init the output module."""
        self._config = config
        self._db = db
        self._metadata = metadata
        self._path = path

    def create_ansible_host(self, name):
        """Create host entry for Ansible inventory."""
        meta_host, meta_domain = get_host_from_metadata(self._metadata, name)
        db_host = self._db.hosts[name]

        ip = db_host.ip
        ansible_host = resolve_hostname(ip) or ip

        python = (
            self._config["python"].get(meta_host["os"])
            or self._config["python"]["default"]
        )

        ansible_user = get_username(db_host, meta_host, self._config)
        password = get_password(db_host, meta_host, self._config)
        ssh_key = get_ssh_key(db_host, meta_host, self._config)

        # Common attributes
        host_info = {
            "ansible_host": ansible_host,
            "ansible_python_interpreter": python,
            "ansible_user": ansible_user,
            "meta_fqdn": name,
            "meta_domain": meta_domain["name"],
            "meta_provider_id": db_host.id,
            "meta_ip": ip,
            "meta_dc_record": ",".join(
                "DC=%s" % dc for dc in meta_domain["name"].split(".")
            ),
        }
        copy_meta_attrs(host_info, meta_host, ["os", "role", "netbios"])

        if "parent" in meta_domain:
            host_info["parent_domain"] = meta_domain["parent"]

        if ssh_key:
            host_info["ansible_ssh_private_key_file"] = ssh_key

        if password:
            host_info["ansible_password"] = password

        if is_windows_host(meta_host):
            host_info.update(
                {
                    "ansible_port": 5986,
                    "ansible_connection": "winrm",
                    "ansible_winrm_server_cert_validation": "ignore",
                    "meta_domain_level": meta_host.get("domain_level", "top"),
                }
            )
        return host_info

    def create_inventory(self):
        """Create the Ansible inventory in dict form."""
        provisioned = self._db.hosts
        inventory = deepcopy(
            self._config.get("inventory_layout", DEFAULT_INVENTORY_LAYOUT)
        )

        for host in provisioned.values():
            meta_host, meta_domain = get_host_from_metadata(self._metadata, host.name)
            groups = meta_host.get("groups") or [meta_host.get("group", "all")]
            group = find_group(inventory, groups)
            if "hosts" not in group:
                group["hosts"] = {}

            group["hosts"][host.name] = self.create_ansible_host(host.name)
        return inventory

    def create_output(self):
        """Create the target output file."""
        inventory = self.create_inventory()
        save_yaml(self._path, inventory)
        return inventory
